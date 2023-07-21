from FLPUCI.utils.props import TrainingParameters, FCAEProperties

parameters = TrainingParameters(epochs=3, batch_size=2, shuffle_buffer=10, prefetch_buffer=-1, rounds=5)

properties = FCAEProperties(encode_layers=[128, 64, 32], encode_activation='relu', decode_activation='linear',
                            kernel_size=(3, 3), strides=2, padding='same', latent_space=10, learning_rate=0.0005)
