import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LightSource


dm = np.loadtxt('../_times/sim_24-02-08-01-15-51_dm/veh125.csv', delimiter=',')
min_stay_time = dm.min()

num_cells = dm.shape[1]

x = []
y = []

for heatmap in dm:
    for cell_index, stay_time in enumerate(heatmap):
        if stay_time > min_stay_time:
            x_index = cell_index % 128
            y_index = int(cell_index / 128)
            x.append(x_index)
            y.append(y_index)
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

plt.show()
