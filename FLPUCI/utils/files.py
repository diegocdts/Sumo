import os


def dir_exists_create(dir_name: str):
    path = os.path.join(os.path.normpath(os.getcwd()), dir_name)
    if not os.path.exists(path):
        os.mkdir(path)
    return path


class Path:
    @staticmethod
    def f1_raw_data(mobility_output: str):
        return dir_exists_create('{}/'.format(mobility_output))

    @staticmethod
    def f2_data(mobility_output: str):
        return dir_exists_create('{}_f1_data/'.format(mobility_output))

    @staticmethod
    def f3_utm(mobility_output: str):
        return dir_exists_create('{}_f2_utm/'.format(mobility_output))

    @staticmethod
    def f4_fms(mobility_output: str):
        return dir_exists_create('{}_f3_fm/'.format(mobility_output))

    @staticmethod
    def f5_logit(mobility_output: str):
        return dir_exists_create('{}_f4_logit/'.format(mobility_output))