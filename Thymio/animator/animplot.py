import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter
import numpy as np


def plot():
    with open('trajectory.dat', 'r') as f:
        lines = f.readlines()
        vector_list = [list(map(float, line.split(", "))) for line in lines]
        vectors = np.array(vector_list)
    return vectors


points = plot()
row, col = points.shape

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5, 5)


def animate(i):
    ax.clear()
    # Get the point from the points list at index i
    # point = points[i]
    xs = points[i, 0]
    ys = points[i, 1]
    x = [xs, points[i, 2] + xs]
    y = [ys, points[i, 3] + ys]
    # Plot that point using the x and y coordinates
    ax.plot(xs, ys,
            label='original', marker='o')

    ax.plot(x, y, "-", linewidth=2)
    # Set the x and y axis to display a fixed range
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])


ani = FuncAnimation(fig, animate, frames=row,
                    interval=500, repeat=False)

plt.close()

# Save the animation as an animated GIF
ani.save("simulation.gif", dpi=300,
         writer=PillowWriter(fps=10))
