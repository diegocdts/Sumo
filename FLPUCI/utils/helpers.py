import os


def sorted_files(dir_path: str):
    """
    sorts the files inside a path
    :param dir_path: directory path
    :return: files sorted
    """
    return sorted(os.listdir(dir_path))


def get_file_path(dir_path: str, file_name: str):
    """
    gets a file path by joining the directory path and the file name
    :param dir_path: directory path
    :param file_name: file name
    :return: file path
    """
    return os.path.join(dir_path, file_name)
