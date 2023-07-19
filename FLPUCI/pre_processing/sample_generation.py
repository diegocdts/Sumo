import numpy as np
import pandas as pd

from FLPUCI.utils.helpers import sorted_files, get_file_path, dir_exists_create


class FeatureMatrix:

    def __init__(self, trace_path: str):
        self.trace_path = trace_path
        self.fm_path = dir_exists_create(f'{trace_path}_fm')
        self.header = 'win,x,y,time\n'

    def generate(self):
        for file_name in sorted_files(self.trace_path):
            file_path = get_file_path(self.trace_path, file_name)
            output_file_path = get_file_path(self.fm_path, file_name)
            df = pd.read_csv(file_path)
            matrix = self.empty_matrix(output_file_path)
            for window in range(0, self.max_window + 1):
                df_window = df[df.win == window]
                copy = df_window.copy().reset_index()
                self.fill_matrix(copy, matrix, output_file_path)

    def empty_matrix(self, output_file_path):
        column_names = np.arange(0, self.dataset.width * self.dataset.height, 1)
        matrix = pd.DataFrame(columns=column_names)
        matrix.to_csv(output_file_path, index=False)
        return matrix
