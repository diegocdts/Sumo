import os

import pandas as pd


def min_max(df):
    min_time = min(df.time)
    max_time = max(df.time)
    min_x = min(df.x)
    max_x = max(df.x)
    min_y = min(df.y)
    max_y = max(df.y)

    return min_time, max_time, min_x, max_x, min_y, max_y


def handle(path):

    df = pd.read_csv(path, sep=' ', names=['time', 'id', 'x', 'y'], skiprows=1)

    min_time, max_time, min_x, max_x, min_y, max_y = min_max(df)
    df.time = df.time - min_time
    df.x = df.x - min_x
    df.y = df.y - min_y
    min_time, max_time, min_x, max_x, min_y, max_y = min_max(df)

    offset = f'{min_time} {max_time} {min_x} {max_x} {min_y} {max_y} 0 0\n'

    df_first_positions = df.drop_duplicates(subset='id', keep='first', ignore_index=True)
    df_first_positions.time = 0
    df = pd.concat([df_first_positions, df], ignore_index=True)
    print(df)

    df.to_csv(path, sep=' ', index=False, header=False)

    with open(path, 'r') as file:
        lines = file.readlines()
    lines.insert(0, offset)
    with open(path, 'w') as file:
        file.writelines(lines)


def handle_report(dir, file_name):
    report_path = os.path.join(dir, file_name)
    new_file = os.path.join(dir, 'time_infection.txt')
    time_infection = ''
    with open(report_path, 'r') as file:
        lines = file.readlines()
        lines = [line for line in lines if line.__contains__(' R\n') or line.endswith(' D\n')]
        for line in lines:
            split = line.split(' ')
            time = round(float(split[0]), 2)
            infected = split[3]
            new_line = f'{time} {infected}\n'
            time_infection = f'{time_infection}{new_line}'
    with open(new_file, 'w') as file:
        file.writelines(time_infection)

