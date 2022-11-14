import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter
import numpy as np
import os


def plot():
    dir_name = "animator/"
    test = os.listdir(dir_name)
    vectors = []
    for item in test:
        if item.endswith(".dat"):
            with open(dir_name+item, 'r') as f:
                lines = f.readlines()
                vector_list = [list(map(float, line.split(", "))) for line in lines]
                vectors_set = np.array(vector_list)
            
            vectors.append(vectors_set)
    
    return vectors


points = plot()
row, col = points[0].shape

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5, 5)


def animate(i):
    ax.clear()
    # Get the point from the points list at index i
    # point = points[i]
    for p in points:
        xs = p[i, 0]
        ys = p[i, 1]
        x = [xs, p[i, 2] + xs]
        y = [ys, p[i, 3] + ys]
        # Plot that point using the x and y coordinates
        ax.plot(x, y, "-", linewidth=2, color='g')

        ax.plot(xs, ys,
                label='original', marker='o')
        # Set the x and y axis to display a fixed range
        ax.set_xlim([-1, 1])
        ax.set_ylim([-1, 1])


ani = FuncAnimation(fig, animate, frames=row,
                    interval=500, repeat=False)

plt.close()

# Save the animation as an animated GIF
ani.save("animator/simulation.gif", dpi=300,
         writer=PillowWriter(fps=10))
