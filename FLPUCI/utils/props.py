
class TrainingParameters:

    def __init__(self, epochs: int, batch_size: int, shuffle_buffer: int = None, prefetch_buffer: int = None,
                 rounds: int = None):
        self.epochs = epochs
        self.batch_size = batch_size
        self.shuffle_buffer = shuffle_buffer
        self.prefetch_buffer = prefetch_buffer
        self.rounds = rounds


class FCAEProperties:

    def __init__(self, encode_layers: list, encode_activation: str, decode_activation: str, kernel_size: tuple,
                 strides: int, padding: str, latent_space: int, learning_rate, input_shape: tuple = None):
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
        self.input_shape = (width, height, 1)
