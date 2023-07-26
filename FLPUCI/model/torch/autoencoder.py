import torch.nn as nn

from FLPUCI.utils.props import FCAEProperties


class ReshapeLayer(nn.Module):
    def __init__(self, shape):
        super(ReshapeLayer, self).__init__()
        self.shape = shape

    def forward(self, x):
        return x.view(self.shape)


def model_build(fcaep: FCAEProperties):
    encoder = encoder_build(fcaep)
    decoder = decoder_build(fcaep)
    return nn.Sequential(encoder, decoder)


def encoder_build(fcaep: FCAEProperties):
    encoder = nn.Sequential()
    encoder.add_module('input_layer', nn.Conv2d(fcaep.input_shape[2], fcaep.encode_layers[0], fcaep.kernel_size,
                                                stride=fcaep.strides, padding=0))
    encoder.add_module('activation', nn.ReLU())

    for i in range(len(fcaep.encode_layers) - 1):
        encoder.add_module(f'conv_{i}', nn.Conv2d(fcaep.encode_layers[i], fcaep.encode_layers[i + 1], fcaep.kernel_size,
                                                  stride=fcaep.strides, padding=0))
        encoder.add_module(f'activation_{i}', nn.ReLU())

    encoder.add_module('flatten', nn.Flatten())
    encoder.add_module('dense', nn.Linear(fcaep.latent_space, fcaep.latent_space))
    encoder.add_module('latent_activation', nn.ReLU())
    return encoder


def decoder_build(fcaep: FCAEProperties):
    dense_layer, width, height = dense_nodes_width_height(fcaep)
    decoder = nn.Sequential()
    decoder.add_module('dense', nn.Linear(fcaep.latent_space, dense_layer))
    decoder.add_module('dense_activation', nn.ReLU())

    # Usamos a classe personalizada ReshapeLayer para alterar a forma do tensor
    decoder.add_module('reshape', ReshapeLayer((-1, fcaep.encode_layers[-1], width, height)))

    for i in range(len(fcaep.decode_layers) - 1):
        decoder.add_module(f'conv_transpose_{i}', nn.ConvTranspose2d(fcaep.decode_layers[i], fcaep.decode_layers[i + 1],
                                                                     fcaep.kernel_size, stride=fcaep.strides,
                                                                     padding=0))
        decoder.add_module(f'activation_{i}', nn.ReLU())

    decoder.add_module('output', nn.ConvTranspose2d(fcaep.decode_layers[-1], fcaep.input_shape[2], fcaep.kernel_size,
                                                    padding=0))
    return decoder


def dense_nodes_width_height(fcaep: FCAEProperties):
    width, height = fcaep.input_shape[0], fcaep.input_shape[1]
    for _ in fcaep.encode_layers:
        width = width // 2
        height = height // 2
    dense_nodes = int(width * height * fcaep.encode_layers[-1])
    return dense_nodes, width, height
