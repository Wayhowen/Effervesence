import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter
import numpy as np
 
points = np.array([[ 1.05634744e-03,  2.28545764e-06],
       [ 5.33372452e-02,  6.55913550e-03],
       [ 1.02044510e-01,  2.51061012e-02],
       [ 1.23875911e-01,  3.51324195e-02],
       [ 1.46872198e-01,  4.30873206e-02],
       [ 1.85862827e-01,  4.88500609e-02],
       [ 2.25391749e-01,  4.38772307e-02],
       [ 2.82543479e-01,  2.27393535e-02],
       [ 3.34239691e-01, -8.75052284e-03],
       [ 3.62580861e-01, -3.78336762e-02],
       [ 3.80978686e-01, -7.41929100e-02],
       [ 3.88585119e-01, -1.21249596e-01],
       [ 3.81150586e-01, -1.68874103e-01],
       [ 3.59373059e-01, -2.40469089e-01],
       [ 3.38832949e-01, -3.12327328e-01],
       [ 3.27433849e-01, -3.81223284e-01],
       [ 3.30252823e-01, -4.50739561e-01],
       [ 3.29383441e-01, -5.07425982e-01],
       [ 3.11766798e-01, -5.61593959e-01],
       [ 2.77002095e-01, -6.22777377e-01],
       [ 2.35957553e-01, -6.79009337e-01],
       [ 2.12325637e-01, -7.01555592e-01],
       [ 1.83623062e-01, -7.18133878e-01],
       [ 1.32875533e-01, -7.44225679e-01],
       [ 8.60196494e-02, -7.76033393e-01],
       [ 5.56183502e-02, -7.94326902e-01],
       [ 2.20824249e-02, -8.05541464e-01],
       [-6.92663566e-03, -8.11080306e-01],
       [-3.62606905e-02, -8.15048003e-01],
       [-6.80374889e-02, -8.23299692e-01],
       [-9.60828206e-02, -8.39871050e-01],
       [-1.12689482e-01, -8.51046220e-01],
       [-1.31004473e-01, -8.59714536e-01],
       [-1.61908578e-01, -8.69269476e-01],
       [-1.93848691e-01, -8.74511055e-01],
       [-2.26112481e-01, -8.82538477e-01],
       [-2.55450953e-01, -8.99753511e-01],
       [-3.11105046e-01, -9.45648068e-01]])
row, col = points.shape
 
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
 
def animate(i):
    ax.clear()
    # Get the point from the points list at index i
    #point = points[i]
    xs = points[i, 0]
    ys = points[i, 1]
    # Plot that point using the x and y coordinates
    ax.plot(xs, ys, 
            label='original', marker='o')
    # Set the x and y axis to display a fixed range
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
ani = FuncAnimation(fig, animate, frames=row,
                    interval=500, repeat=False)
plt.close()

# Save the animation as an animated GIF
ani.save("simulation.gif", dpi=300,
         writer=PillowWriter(fps=10))