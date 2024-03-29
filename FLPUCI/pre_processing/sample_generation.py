import os.path
import random

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from FLPUCI.utils.helpers import sorted_files, get_file_path
from components.settings import SimulationSettings


def logit(normalized_cell_stay_time: list):
    """
    performs logit transformation over the displacement matrix
    :param normalized_cell_stay_time: the displacement matrix cells as a list
    :return: the displacement matrix cells transformed
    """
    epsilon = 1e-15
    arr_clipped = np.clip(normalized_cell_stay_time, epsilon, 1 - epsilon)
    arr_logit = np.log(arr_clipped / (1 - arr_clipped))
    return arr_logit


class DisplacementMatrix:

    def __init__(self, settings: SimulationSettings):
        """
        Instantiates the functions to create a displacement matrix from the trace records
        :param settings: a SimulationSettings object
        """
        self.settings = settings
        self.header = ['interval', 'x', 'y', 'time']
        self.columns = np.arange(0, self.settings.width * self.settings.height, 1)

    def new_record(self, interval: int):
        """
        creates a new record in the displacement matrix file
        :param interval: interval regarding the new record
        """
        for file_name in sorted_files(self.settings.trace_path):
            file_path = get_file_path(self.settings.trace_path, file_name)
            trace_df = pd.read_csv(file_path, names=self.header)

            dm_file_path = get_file_path(self.settings.dm_path, file_name)
            self.displacement_matrix(dm_file_path)

            this_interval_records = trace_df[trace_df.interval == interval]
            copy = this_interval_records.copy().reset_index()

            self.fill_record(copy, dm_file_path)

    def displacement_matrix(self, file_path: str):
        """
        creates the displacement matrix
        :param file_path: path to the displacement matrix to be created or accessed
        :return: the displacement matrix
        """
        if not os.path.exists(file_path):
            matrix = pd.DataFrame(columns=self.columns)
            matrix.to_csv(file_path, index=False, header=False)

    def fill_record(self, this_interval_records: pd.DataFrame, file_path: str):
        """
        fills a new displacement matrix record 
        :param this_interval_records: the trace data regarding the considered interval
        :param file_path: the displacement matrix path
        """
        cell_stay_time = np.zeros(len(self.columns))

        if len(this_interval_records) > 0:
            previous_time = this_interval_records.time[0] - 1

            for index, row in this_interval_records.iterrows():
                # cell position calculation
                x_index = int(row.x / self.settings.spatial_resolution)
                y_index = int(row.y / self.settings.spatial_resolution)
                cell = (x_index * self.settings.height) + y_index

                # time a node spends in a cell
                delta_time = row.time - previous_time
                new_time = cell_stay_time[cell] + delta_time
                cell_stay_time[cell] = new_time
                previous_time = row.time

        # appends feature_row at the matrix
        cell_stay_time = self.normalize_by_temporal_resolution(cell_stay_time)
        output_file = open(file_path, 'a')
        output_file.write(cell_stay_time)

    def normalize_by_temporal_resolution(self, cell_stay_time: np.array):
        """
        normalizes the new displacement matrix record by the temporal resolution (interval size)
        :param cell_stay_time: the array representing the cells and the time the user spend in each one of them
        :return: the new displacement matrix record normalized
        """
        cells_stay_time_logit = logit([item / self.settings.temporal_resolution for item in cell_stay_time])
        cells_stay_time_str = ', '.join(['{:.3f}'.format(item) for item in cells_stay_time_logit]) + '\n'
        return cells_stay_time_str


def reshape(samples: np.array):
    """
    reshapes the array of samples by adding the gray scale axis
    :param samples: the array of samples
    :return: the array of samples with the gray scale axis
    """
    if len(samples.shape) == 4:
        samples = np.reshape(samples, (samples.shape[0], samples.shape[1], samples.shape[2], samples.shape[3], 1))
    elif len(samples.shape) == 3:
        samples = np.reshape(samples, (samples.shape[0], samples.shape[1], samples.shape[2], 1))
    return samples


def heatmaps_view(dataset):
    if len(dataset) > 0:
        plt.figure(figsize=(20, 10))
        for i in range(len(dataset)):
            i = int(i)
            plt.subplot(1, len(dataset), i + 1)
            plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
            plt.xticks([])
            plt.yticks([])
            plt.grid(False)
            plt.imshow(dataset[i])
        plt.show()


def compare_samples_reconstructions(samples, reconstructions):
    if len(samples) > 0 and len(reconstructions) > 0:
        plt.figure(figsize=(20, 10))
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)

        for i in range(len(samples)):
            plt.subplot(1, 2, 1)  # Subplot for sample
            plt.xticks([])
            plt.yticks([])
            plt.grid(False)
            plt.imshow(samples[i])
            plt.title("Sample")

            plt.subplot(1, 2, 2)  # Subplot for reconstruction
            plt.xticks([])
            plt.yticks([])
            plt.grid(False)
            plt.imshow(reconstructions[i])
            plt.title("Reconstruction")

            path = 'comparisons'
            if not os.path.exists(path):
                os.mkdir(path)
            plt.savefig(f'{path}/{i}.png')


def min_max_scaling(pixels: np.array):
    return (pixels - pixels.min()) / (pixels.max() - pixels.min())


class SampleHandler:

    def __init__(self, settings: SimulationSettings):
        """
        Handles the mobility samples
        :param settings: a SimulationSetting object
        """
        self.settings = settings

    def get_datasets(self, start_window: int, end_window: int):
        """
        gets the user datasets. The user datasets may have different number of samples from each other
        :param start_window: the first interval of the window considered
        :param end_window: the last interval of the window considered
        :return: the array of user datasets and a list of indices of users who have not empty datasets
        """
        indices = []
        datasets = []
        for index, file_name in enumerate(sorted_files(self.settings.dm_path)):
            file_path = get_file_path(self.settings.dm_path, file_name)
            user_samples = self.get_samples(file_path, start_window, end_window)
            if len(user_samples) > 0:
                dataset_id = file_name.replace('.csv', '')
                indices.append(dataset_id)
                datasets.append(user_samples)
            del user_samples
        return datasets, indices

    def get_samples(self, file_path: str, start_window: int, end_window: int):
        """
        gets the user samples
        :param file_path: the displacement matrix file path
        :param start_window: the first interval of the window considered
        :param end_window: the last interval of the window considered
        :return: the array of user samples
        """
        samples = []
        with open(file_path) as file:
            intervals = file.readlines()[start_window:end_window]
            for interval in intervals:
                sample = np.array(interval.split(','), dtype="float64")
                if sample.max() > sample.min():
                    sample = min_max_scaling(sample)
                    sample = sample.reshape(self.settings.width, self.settings.height)
                    samples.append(sample)
                del sample
        samples = np.array(samples)
        return reshape(samples)

    def random_dataset(self):
        """
        gets a random user dataset
        :return: the dataset of a random user
        """
        def get_random():
            total_users = len(sorted_files(self.settings.dm_path))
            file_name = sorted_files(self.settings.dm_path)[random.randrange(total_users)]
            file_path = get_file_path(self.settings.dm_path, file_name)
            single_dataset = self.get_samples(file_path, 0, 1)
            return single_dataset
        dataset = get_random()
        return dataset

    def samples_as_list(self, start_window: int, end_window: int):
        """
        gets the user datasets as a list
        :param start_window: the first interval of the window considered
        :param end_window: the last interval of the window considered
        :return: user datasets as a list
        """
        datasets, indices = self.get_datasets(start_window, end_window)
        samples = []
        for dataset in datasets:
            for sample in dataset:
                samples.append(sample)
                del sample
            del dataset
        del datasets
        return np.array(samples), indices
