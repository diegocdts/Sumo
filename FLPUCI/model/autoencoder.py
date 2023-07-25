import tensorflow_federated as tff
import tensorflow as tf
import collections

from FLPUCI.pre_processing.sample_generation import SampleHandler
from FLPUCI.utils.props import TrainingParameters, FCAEProperties
from components.settings import SimulationSettings


class FederatedSampleHandler:

    def __init__(self, settings: SimulationSettings, training_parameters: TrainingParameters):
        """
        Instantiates a handler for the datasets to be used during federated training
        :param settings: a SimulationSettings object
        :param training_parameters: a TrainingParameters object
        """
        self.sample_handler = SampleHandler(settings)
        self.training_parameters = training_parameters
        self.element_spec = self.element_spec_build()

    def preprocess(self, dataset):
        """
        preprocesses the dataset to be used
        :param dataset: the dataset to be preprocessed
        :return: the preprocessed dataset
        """
        batch_size = self.training_parameters.batch_size
        if len(dataset) < batch_size:
            batch_size = len(dataset)

        def batch_format_fn(element):
            return collections.OrderedDict(x=element, y=element)

        return dataset.repeat(self.training_parameters.epochs).shuffle(self.training_parameters.shuffle_buffer).batch(
            batch_size).map(batch_format_fn).prefetch(self.training_parameters.prefetch_buffer)

    def element_spec_build(self):
        """
        gets the input spec for the tff.learning.from_keras_model
        :return: the input_spec
        """
        single_user_dataset = tf.data.Dataset.from_tensor_slices(self.sample_handler.random_dataset())
        preprocessed = self.preprocess(single_user_dataset)
        del single_user_dataset
        return preprocessed.element_spec

    def users_data(self, start_window: int, end_window: int):
        """
        gets the user datasets and transforms them into a list of federated datasets samples
        :param start_window: the first interval of the window considered
        :param end_window: the last interval of the window considered
        :return: list of federated datasets samples
        """
        users_dataset_samples, indices = self.sample_handler.get_datasets(start_window, end_window)
        federated_dataset_samples = []

        for dataset in users_dataset_samples:
            if len(dataset) > 0:
                federated_dataset = tf.data.Dataset.from_tensor_slices(dataset)
                preprocessed = self.preprocess(federated_dataset)
                federated_dataset_samples.append(preprocessed)
        del users_dataset_samples
        return federated_dataset_samples


class FederatedFullConvolutionalAutoEncoder:

    def __init__(self, settings: SimulationSettings, parameters: TrainingParameters, properties: FCAEProperties):
        """
        Instantiates a FederatedFullConvolutionalAutoEncoder to perform federated training and prediction over mobility
        trace data
        :param settings: a SimulationSettings object
        :param parameters: a TrainingParameters object
        :param properties: a FCAEProperties object
        """
        self.settings = settings
        self.properties = properties
        self.federated_sample_handler = FederatedSampleHandler(settings, parameters)

        self.iterative_process, self.state = self.global_model_start()
        self.evaluator = self.build_evaluator()
        self.manager = None
        tff.backends.native.set_local_execution_context(clients_per_thread=100)

    def global_model_start(self):
        """
        initiates a global model
        :return: the iterative training process and the initial model state
        """
        iterative_process = tff.learning.build_federated_averaging_process(
            model_fn=self.model_fn,
            client_optimizer_fn=lambda: tf.keras.optimizers.Adam(learning_rate=self.properties.learning_rate),
            server_optimizer_fn=lambda: tf.keras.optimizers.Adam(learning_rate=self.properties.learning_rate)
        )
        return iterative_process, iterative_process.initialize()

    def build_evaluator(self):
        """
        builds an evaluator to the model
        :return: the evaluator of the model
        """
        return tff.learning.build_federated_evaluation(self.model_fn)

    def model_fn(self):
        """
        builds the federated model
        :return: the federated model
        """
        keras_model = model_build(self.properties)
        return tff.learning.from_keras_model(
            keras_model=keras_model,
            input_spec=self.federated_sample_handler.element_spec,
            loss=tf.keras.losses.MeanSquaredError()
        )

    def model_evaluation(self, testing_data):
        """
        performs a model evaluation
        :param testing_data: the data to be used for evaluation
        :return: the model evaluation
        """
        return self.evaluator(self.state.model, testing_data)

    def training(self, start_window: int, end_window: int):
        """
        performs model training
        :param start_window: the first interval of the window considered
        :param end_window: the last interval of the window considered
        """
        rounds = self.federated_sample_handler.training_parameters.rounds

        training_data = self.federated_sample_handler.users_data(start_window, end_window)

        for round_num in range(rounds):
            print('start: {} | end: {} | round: {}'.format(start_window, end_window, round_num))
            round_iteration = self.iterative_process.next(self.state, training_data)
            self.state = round_iteration[0]
            self.manager.save_checkpoint(self.state, round_num)

    def encoder_prediction(self, start_window: int, end_window: int):
        """
        encodes samples from a window using the trained encoding model layers
        :param start_window: the first interval of the window considered
        :param end_window: the last interval of the window considered
        :return: the encoded samples and the list of indices of users who have not empty datasets
        """
        samples, indices = self.federated_sample_handler.sample_handler.samples_as_list(start_window, end_window)
        keras_model = model_build(self.properties)
        self.state.model.assign_weights_to(keras_model)
        encoder = get_trained_encoder(keras_model)
        predictions = encoder.predict(samples)
        del samples, encoder
        return predictions, indices


def model_build(fcaep: FCAEProperties):
    """
    builds a full convolutional autoencoder
    :param fcaep: a FCAEProperties object
    :return: the full convolutional autoencoder
    """
    encoder = encoder_build(fcaep)
    decoder = decoder_build(fcaep)
    return tf.keras.models.Model(inputs=encoder.input, outputs=decoder(encoder.outputs))


def encoder_build(fcaep: FCAEProperties):
    """
    builds the encoding layers of the model
    :param fcaep: a FCAEProperties object
    :return: the encoding layers
    """
    encoder = tf.keras.Sequential()
    encoder.add(tf.keras.layers.InputLayer(input_shape=fcaep.input_shape))

    for layer in fcaep.encode_layers:
        encoder.add(tf.keras.layers.Conv2D(layer, fcaep.kernel_size, activation=fcaep.encode_activation,
                                           strides=fcaep.strides, padding=fcaep.padding))
    encoder.add(tf.keras.layers.Flatten())
    encoder.add(tf.keras.layers.Dense(fcaep.latent_space, activation=fcaep.encode_activation))
    return encoder


def decoder_build(fcaep: FCAEProperties):
    """
    builds the decoding layers of the model
    :param fcaep: a FCAEProperties object
    :return: the decoding layers
    """
    dense_layer, width, height = dense_nodes_width_height(fcaep)

    decoder = tf.keras.Sequential()
    decoder.add(tf.keras.layers.InputLayer(input_shape=(fcaep.latent_space,)))

    decoder.add(tf.keras.layers.Dense(dense_layer, activation=fcaep.decode_activation))
    decoder.add(tf.keras.layers.Reshape((height, width, fcaep.decode_layers[0])))

    for layer in fcaep.decode_layers:
        decoder.add(tf.keras.layers.Conv2DTranspose(layer, fcaep.kernel_size, activation=fcaep.decode_activation,
                                                    strides=fcaep.strides, padding=fcaep.padding))
    decoder.add(tf.keras.layers.Conv2DTranspose(1, fcaep.kernel_size, activation=fcaep.decode_activation,
                                                padding=fcaep.padding))
    return decoder


def dense_nodes_width_height(fcaep: FCAEProperties):
    """
    gets the number of units for the dense layer, the width and height for the reshape layer (see decoder_build)
    :param fcaep: a FCAEProperties object
    :return: units, width and height
    """
    width, height = fcaep.input_shape[0], fcaep.input_shape[1]
    for _ in fcaep.encode_layers:
        width = width / 2
        height = height / 2
    dense_nodes = int(width * height * fcaep.encode_layers[-1])
    return dense_nodes, int(width), int(height)


def get_trained_encoder(model: tf.keras.Model):
    """
    gets the encoding layers of the trained model
    :param model: a trained model
    :return: the encoding layers
    """
    return tf.keras.models.Model(model.input, model.layers[-2].output)
