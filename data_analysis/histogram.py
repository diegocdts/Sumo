import os

import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LightSource

dm_dir = '../_times/sim_24-02-08-01-15-51_dm/'
dms = sorted(os.listdir(dm_dir), key=lambda x: int(x.replace('.csv', '')[3:]))

for file in dms:
    dm_path = os.path.join(dm_dir, file)

    dm = np.loadtxt(dm_path, delimiter=',')
    min_stay_time = dm.min()

    num_cells = dm.shape[1]

    x = []
    y = []
    stay_times = []

    for heatmap in dm:
        for cell_index, stay_time in enumerate(heatmap):
            if stay_time > min_stay_time:
                x_index = cell_index % 128
                y_index = int(cell_index / 128)
                x.append(x_index)
                y.append(y_index)
                stay_times.append(stay_time)
    x = np.array(x)
    y = np.array(y)

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    hist, xedges, yedges = np.histogram2d(x, y, bins=30)

    # Construct arrays for the anchor positions of the 16 bars.
    xpos, ypos = np.meshgrid(xedges[:-1] + 0.25, yedges[:-1] + 0.25, indexing="ij")
    xpos = xpos.ravel()
    ypos = ypos.ravel()
    zpos = 0

    # Construct arrays with the dimensions for the 16 bars.
    dx = dy = (xedges.max() - xedges.min()) * 0.02 * np.ones_like(zpos)
    dz = hist.ravel()

    ax.bar3d(xpos, ypos, zpos, dx, dy, dz, zsort='average')
    fig.suptitle(file.replace('.csv', ''))
    plt.xlabel('Visited cells')
    plt.ylabel('Visited cells')
    ax.set_zlabel('Frequency')

    plt.show()

    plt.hist(stay_times, bins=10, weights=np.ones(len(stay_times)) / len(stay_times) * 100)
    plt.suptitle(file.replace('.csv', ''))
    plt.xlabel('Normalized stay time in cells')
    plt.ylabel('Frequency')

    plt.show()
