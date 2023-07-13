from FLPUCI.utils.files import Path
from FLPUCI.utils.helpers import sorted_files, get_file_path


class DataCleaning:

    def __init__(self, raw_data_path: str, window_size: int):
        self.input_data_path = Path.f1_raw_data(raw_data_path)
        self.output_data_path = Path.f2_data(raw_data_path)
        self.window_size = window_size
        self.header = 'win,latitude,longitude,time\n'

    @staticmethod
    def input_file_lines(file_path: str):
        input_file = open(file_path, 'r')
        lines = input_file.readlines()
        return lines

    @staticmethod
    def line_split(line: str):
        split = line.split(',')
        lat = float(split[0])
        lon = float(split[1])
        time = float(split[2])
        return lat, lon, time

    def output_file(self, output_file_path: str):
        output_file = open(output_file_path, 'a')
        output_file.write(self.header)
        return output_file

    def run(self):
        for file_name in sorted_files(self.input_data_path):
            file_path = get_file_path(self.input_data_path, file_name)
            lines = self.input_file_lines(file_path)

            output_file_path = get_file_path(self.output_data_path, file_name)
            output_file = self.output_file(output_file_path)

            next_window = 0
            window_index = 0

            for line in lines:
                lat, lon, time = self.line_split(line)

                while next_window + self.window_size < time:
                    next_window = next_window + self.window_size
                    window_index += 1

                output_file.write('{},{},{},{}\n'.format(window_index, lat, lon, time))
