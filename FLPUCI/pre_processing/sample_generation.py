import math
import os.path
import random

import numpy as np
import pandas as pd

from FLPUCI.utils.helpers import sorted_files, get_file_path
from components.settings import SimulationSettings


def logit(cells_list: list):
    """
    performs logit transformation over the displacement matrix
    :param cells_list: the displacement matrix cells as a list
    :return: the displacement matrix cells transformed
    """
    for j in range(len(cells_list)):
        p = float(cells_list[j])
        e = float(0)
        if p == float(0) or p == float(1):
            e += 0.000001
        new_p = math.log((p + e) / ((1 - p) + e))
        cells_list[j] = new_p
    return cells_list


class DisplacementMatrix:

    def __init__(self, settings: SimulationSettings):
        """
        Instantiates the functions to create a displacement matrix from the trace records
        :param settings: a SimulationSettings object
        """
        self.settings = settings
        self.header = ['interval', 'x', 'y', 'time']

    def new_record(self, interval: int):
        """
        creates a new record in the displacement matrix file
        :param interval: interval regarding the new record
        """
        for file_name in sorted_files(self.settings.trace_path):
            file_path = get_file_path(self.settings.trace_path, file_name)
            trace_df = pd.read_csv(file_path, names=self.header)

            dm_file_path = get_file_path(self.settings.dm_path, file_name)
            dm_df = self.get_matrix(dm_file_path)

            this_interval_records = trace_df[trace_df.interval == interval]
            copy = this_interval_records.copy().reset_index()

            self.fill_record(copy, dm_df, dm_file_path)

    def get_matrix(self, file_path: str):
        """
        accesses the displacement matrix
        :param file_path: path to the displacement matrix to be created or accessed
        :return: the displacement matrix
        """
        if not os.path.exists(file_path):
            columns = np.arange(0, self.settings.width * self.settings.height, 1)
            matrix = pd.DataFrame(columns=columns)
            matrix.to_csv(file_path, index=False)
        else:
            matrix = pd.read_csv(file_path)
        return matrix

    def fill_record(self, this_interval_records: pd.DataFrame, dm_df: pd.DataFrame, file_path: str):
        """
        fills a new displacement matrix record 
        :param this_interval_records: the trace data regarding the considered interval
        :param dm_df: the displacement matrix as a DataFrame
        :param file_path: the displacement matrix path
        """
        cell_stay_time = np.zeros(len(dm_df.columns))

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


def handle_pixels(sample_pixels: np.array):
    """
    handles the pixels of a sample
    :param sample_pixels: the sample pixels
    :return: the sample pixels treated
    """
    if sample_pixels.max() != sample_pixels.min():
        delta = sample_pixels.max() - sample_pixels.min()
        pixels = np.absolute(sample_pixels.astype("float64")) / delta
        pixels = 1 - pixels
        pixels = pixels + np.absolute(pixels.min())
    else:
        pixels = np.absolute(sample_pixels) * 0
    return pixels


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
                indices.append(index)
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
                sample = handle_pixels(sample)
                sample = sample.reshape(self.settings.width, self.settings.height)
                if sample.max() > sample.min():
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
