import gc

from FLPUCI.model.clustering import GaussianMixtureModel
from FLPUCI.model.tf.architecture import FederatedArchitecture


class Server:

    def __init__(self, settings, parameters, properties):
        self.autoencoder_model = FederatedArchitecture(settings, parameters, properties)
        self.clustering_model = GaussianMixtureModel(settings.max_communities)
        self.window_size = settings.window_size

    def autoencoder_training(self, current_interval: int):
        """
        performs federated model training
        :param current_interval: the current interval
        """
        if current_interval >= self.window_size:
            self.autoencoder_model.training(
                start_window=current_interval - self.window_size,
                end_window=current_interval)
            gc.collect()

    def clustering(self, current_interval):
        """
        performs clustering of the current interval users
        :param current_interval: the current interval
        """
        if current_interval >= self.window_size:
            predictions, indices = self.autoencoder_model.encoder_prediction(start_window=current_interval,
                                                                             end_window=current_interval + 1)
            return self.clustering_model.best_communities(predictions)
