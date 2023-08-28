from glob import glob

import numpy as np
from matplotlib import pyplot as plt


def plot_travel_time_histogram(trace_path):
    files = f'{trace_path}/*.csv'
    files = glob(files)

    bike = []
    bus = []
    motorcycle = []
    truck = []
    veh = []

    for file in files:
        if file.__contains__('bike'):
            bike.append(time_inside(file))
        elif file.__contains__('bus'):
            bus.append(time_inside(file))
        elif file.__contains__('motorcycle'):
            motorcycle.append(time_inside(file))
        elif file.__contains__('truck'):
            truck.append(time_inside(file))
        elif file.__contains__('veh'):
            veh.append(time_inside(file))

    data = [bike, bus, motorcycle, truck, veh]
    titles = ['bikes', 'buses', 'motorcycles', 'trucks', 'vehicles']

    plot_figure(data, titles)


def time_inside(file):
    records = np.loadtxt(file, delimiter=',')
    last_record = len(records) - 1
    time_in = records[0][3]
    time_out = records[last_record][3]
    return time_out - time_in


def plot_figure(data, titles):
    plt.figure(figsize=(15, 10))

    for i in range(5):
        plt.subplot(2, 3, i + 1)
        plt.hist(data[i], bins=10, alpha=0.7)
        plt.title(titles[i])

    plt.subplot(2, 3, 6)
    for i in range(5):
        plt.hist(data[i], bins=10, density=True, alpha=0.5)
    plt.legend(titles)
    plt.title('PDF')
    plt.tight_layout()
    plt.savefig('trace_analysis.png')


path = '_uruguaiana/sim_23-08-28-18-44-47'
plot_travel_time_histogram(path)
