import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LightSource


dm = np.loadtxt('../_times/sim_24-02-08-01-15-51_dm/veh10.csv', delimiter=',')
min_stay_time = dm.min()

num_cells = dm.shape[1]

visited_cells_count = np.zeros(num_cells)

for heatmap in dm:
    for cell_index, stay_time in enumerate(heatmap):
        if stay_time > min_stay_time:
            visited_cells_count[cell_index] += stay_time

z = visited_cells_count.reshape(136, 128)

nrows, ncols = z.shape
x = np.linspace(0, ncols+1, ncols)
y = np.linspace(0, nrows+1, nrows)
x, y = np.meshgrid(x, y)

fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))

ls = LightSource(270, 45)
# To use a custom hillshading mode, override the built-in shading and pass
# in the rgb colors of the shaded surface calculated from "shade".
rgb = ls.shade(z, cmap=mpl.colormaps['gist_earth'], vert_exag=0.1, blend_mode='soft')
surf = ax.plot_surface(x, y, z, rstride=1, cstride=1, facecolors=rgb,
                       linewidth=0, antialiased=False, shade=False)

plt.show()
