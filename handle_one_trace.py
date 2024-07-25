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


handle('2024-07-24-17-09-14/sim_24-07-24-18-23-43/one_trace.txt')
