
class TrainingParameters:

    def __init__(self, epochs: int, batch_size: int, shuffle_buffer: int = None, prefetch_buffer: int = None,
                 rounds: int = None):
        """
        Instantiates training parameters for the federated model
        :param epochs: number of training epochs
        :param batch_size: size of the samples batch
        :param shuffle_buffer: size of the buffer to randomly sample elements from. Should be greater than or equal to
        the full size of the dataset for perfect shuffling
        :param prefetch_buffer: number of later elements to be prepared while the current element is being processed
        :param rounds: number of federated rounds to be executed
        """
        self.epochs = epochs
        self.batch_size = batch_size
        self.shuffle_buffer = shuffle_buffer
        self.prefetch_buffer = prefetch_buffer
        self.rounds = rounds


class FCAEProperties:

    def __init__(self, encode_layers: list, encode_activation: str, decode_activation: str, kernel_size: tuple,
                 strides: int, padding: str, latent_space: int, learning_rate, input_shape: tuple = None):
        """
        Instantiates the full convolutional autoencoder model properties
        :param encode_layers: number of kernels in the encoding layers
        :param encode_activation: encoding activation function
        :param decode_activation: decoding activation function
        :param kernel_size: size of the kernel
        :param strides: strides step size
        :param padding: padding size
        :param latent_space: number of unites in the latent space
        :param learning_rate: model learning rate
        :param input_shape: model input shape
        """
        self.encode_layers = encode_layers
        self.decode_layers = encode_layers[::-1]
        self.encode_activation = encode_activation
        self.decode_activation = decode_activation
        self.kernel_size = kernel_size
        self.strides = strides
        self.padding = padding
        self.latent_space = latent_space
        self.learning_rate = learning_rate
        self.input_shape = input_shape

    def set_input_shape(self, width: int, height: int):
        """
        sets the input shape to be passed to the model
        :param width: samples width
        :param height: samples height
        """
        self.input_shape = (width, height, 1)
