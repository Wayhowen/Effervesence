import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter
import numpy as np
import os

W = 1.09  # width of arena
H = 1.87  # height of arena
B = 0.03  # boundary


def plot():
    dir_name = "animator/"
    test = os.listdir(dir_name)
    vectors = []
    for item in test:
        if item.endswith(".dat"):
            with open(dir_name + item, 'r') as f:
                lines = f.readlines()
                vector_list = [list(map(float, line.split(", "))) for line in lines]
                vectors_set = np.array(vector_list)

            vectors.append(vectors_set)

    return vectors


points = plot()
row, col = points[0].shape

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(8 * (W / H), 8)


# animate
def animate(i):
    ax.clear()

    # plot arena boundary
    ax.plot([-W / 2, W / 2], [-H / 2, -H / 2], color='k')
    ax.plot([-W / 2, W / 2], [H / 2, H / 2], color='k')
    ax.plot([-W / 2, -W / 2], [-H / 2, H / 2], color='k')
    ax.plot([W / 2, W / 2], [-H / 2, H / 2], color='k')

    # Get the point from the points list at index i
    # point = points[i]
    for index, p in enumerate(points):
        xs = p[i, 0]
        ys = p[i, 1]
        x = [xs, p[i, 2] + xs]
        y = [ys, p[i, 3] + ys]
        # Plot that point using the x and y coordinates
        ax.plot(x, y, "-", linewidth=2, color='g')

        point_color = 'g'
        if index == 0:
            point_color = 'r'
        elif index == 1:
            point_color = 'b'

        ax.plot(xs, ys,
                label='original', marker='o', color=point_color)
        # Set the x and y axis to display a fixed range

    # plot inner line
    ax.set_xlim([(-W * 1.10) / 2, (W * 1.10) / 2])
    ax.set_ylim([(-H * 1.10) / 2, (H * 1.10) / 2])

    # plot middle space
    SBW = 0.05
    SBH = 0.05
    ax.plot([-SBW / 2, SBW / 2], [-SBH / 2, -SBH / 2], color='k')
    ax.plot([-SBW / 2, SBW / 2], [SBH / 2, SBH / 2], color='k')
    ax.plot([-SBW / 2, -SBW / 2], [-SBH / 2, SBH / 2], color='k')
    ax.plot([SBW / 2, SBW / 2], [-SBH / 2, SBH / 2], color='k')


ani = FuncAnimation(fig, animate, frames=row,
                    interval=500, repeat=False)

plt.close()

# Save the animation as an animated GIF
ani.save("animator/simulation.gif", dpi=300,
         writer=PillowWriter(fps=10))
