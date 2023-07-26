import numpy as np
from sklearn.mixture import GaussianMixture


class GaussianMixtureModel:

    def __init__(self, max_communities: int):
        self.max_communities = range(1, max_communities+1)

    def fit(self, k: int, input_data: np.array):
        gmm = GaussianMixture(n_components=k, max_iter=1000)
        gmm.fit(input_data)
        aic = gmm.aic(input_data)
        labels = gmm.predict(input_data)
        clusters = np.unique(labels)
        return clusters, labels, aic

    def best_communities(self, input_data: np.array):
        best_aic_score = None
        best_clusters = None
        best_labels = None
        for k in self.max_communities:
            if k >= len(input_data):
                clusters, labels, aic = self.fit(k, input_data)
                if not best_aic_score or best_aic_score > aic:
                    best_aic_score = aic
                    best_clusters = clusters
                    best_labels = labels
            else:
                break
        return best_clusters, best_labels
