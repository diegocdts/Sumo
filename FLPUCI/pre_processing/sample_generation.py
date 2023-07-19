import math
import os.path

import numpy as np
import pandas as pd

from FLPUCI.utils.helpers import sorted_files, get_file_path, dir_exists_create


class FeatureMatrix:

    def __init__(self, trace_path: str, window_size: int, resolution: int, boundary: list):
        self.trace_path = trace_path
        self.fm_path = dir_exists_create(f'{trace_path}_fm')

        self.window_size = window_size

        min_x, min_y = boundary[0], boundary[1]
        max_x, max_y = boundary[2], boundary[3]

        self.resolution = resolution
        self.width = int((max_x - min_x) / resolution)
        self.height = int((max_y - min_y) / resolution)

        self.header = ['win', 'x', 'y', 'time']

    def new_record(self, window: int):
        for file_name in sorted_files(self.trace_path):
            file_path = get_file_path(self.trace_path, file_name)
            trace_df = pd.read_csv(file_path, names=self.header)

            fm_file_path = get_file_path(self.fm_path, file_name)
            fm_df = self.get_matrix(fm_file_path)

            this_window_records = trace_df[trace_df.win == window]
            copy = this_window_records.copy().reset_index()

            self.fill_record(copy, fm_df, fm_file_path)

    def get_matrix(self, output_file_path: str):
        if not os.path.exists(output_file_path):
            columns = np.arange(0, self.width * self.height, 1)
            matrix = pd.DataFrame(columns=columns)
            matrix.to_csv(output_file_path, index=False)
        else:
            matrix = pd.read_csv(output_file_path)
        return matrix

    def fill_record(self, this_window_records: pd.DataFrame, fm_df: pd.DataFrame, output_file_path: str):
        cell_stay_time = np.zeros(len(fm_df.columns))

        if len(this_window_records) > 0:
            previous_time = this_window_records.time[0] - 1

            for index, row in this_window_records.iterrows():
                # cell position calculation
                x_index = int(row.x / self.resolution)
                y_index = int(row.y / self.resolution)
                cell = (x_index * self.height) + y_index

                # time a node spends in a cell
                delta_time = row.time - previous_time
                new_time = cell_stay_time[cell] + delta_time
                cell_stay_time[cell] = new_time
                previous_time = row.time

            # appends feature_row at the matrix
        cell_stay_time = self.normalize_by_window_size(cell_stay_time)
        output_file = open(output_file_path, 'a')
        output_file.write(cell_stay_time)

    def normalize_by_window_size(self, cell_stay_time: np.array):
        cells_stay_time_logit = self.logit([item / self.window_size for item in cell_stay_time])
        cells_stay_time_str = ', '.join([str(item) for item in cells_stay_time_logit]) + '\n'
        return cells_stay_time_str

    def logit(self, cells_list: list):
        for j in range(len(cells_list)):
            p = float(cells_list[j])
            e = float(0)
            if p == float(0) or p == float(1):
                e += 0.000001
            new_p = math.log((p + e) / ((1 - p) + e))
            cells_list[j] = new_p
        return cells_list
