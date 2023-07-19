import os


def dir_exists_create(dir_name: str):
    path = os.path.join(os.path.normpath(os.getcwd()), dir_name)
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def sorted_files(dir_path: str):
    return sorted(os.listdir(dir_path))


def get_file_path(dir_path: str, file_name: str):
    return os.path.join(dir_path, file_name)
