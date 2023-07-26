from tensorflow import keras
from FLPUCI.utils.props import FCAEProperties


def model_build(fcaep: FCAEProperties):
    """
    builds a full convolutional autoencoder
    :param fcaep: a FCAEProperties object
    :return: the full convolutional autoencoder
    """
    encoder = encoder_build(fcaep)
    decoder = decoder_build(fcaep)
    return keras.models.Model(inputs=encoder.input, outputs=decoder(encoder.outputs))


def encoder_build(fcaep: FCAEProperties):
    """
    builds the encoding layers of the model
    :param fcaep: a FCAEProperties object
    :return: the encoding layers
    """
    encoder = keras.Sequential()
    encoder.add(keras.layers.InputLayer(input_shape=fcaep.input_shape))

    for layer in fcaep.encode_layers:
        encoder.add(keras.layers.Conv2D(layer, fcaep.kernel_size, activation=fcaep.encode_activation,
                                        strides=fcaep.strides, padding=fcaep.padding))
    encoder.add(keras.layers.Flatten())
    encoder.add(keras.layers.Dense(fcaep.latent_space, activation=fcaep.encode_activation))
    return encoder


def decoder_build(fcaep: FCAEProperties):
    """
    builds the decoding layers of the model
    :param fcaep: a FCAEProperties object
    :return: the decoding layers
    """
    dense_layer, width, height = dense_nodes_width_height(fcaep)

    decoder = keras.Sequential()
    decoder.add(keras.layers.InputLayer(input_shape=(fcaep.latent_space,)))

    decoder.add(keras.layers.Dense(dense_layer, activation=fcaep.decode_activation))
    decoder.add(keras.layers.Reshape((width, height, fcaep.decode_layers[0])))

    for layer in fcaep.decode_layers:
        decoder.add(keras.layers.Conv2DTranspose(layer, fcaep.kernel_size, activation=fcaep.decode_activation,
                                                 strides=fcaep.strides, padding=fcaep.padding))
    decoder.add(keras.layers.Conv2DTranspose(1, fcaep.kernel_size, activation=fcaep.decode_activation,
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


def get_trained_encoder(model: keras.Model):
    """
    gets the encoding layers of the trained model
    :param model: a trained model
    :return: the encoding layers
    """
    return keras.models.Model(model.input, model.layers[-2].output)
