import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter
from math import sin, cos, radians
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
                vector_list = [list(line.strip().split(", ")) for line in lines]
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
        x1 = float(p[i, 0])
        y1 = float(p[i, 1])
        x2 = float(p[i, 2]) + x1
        y2 = float(p[i, 3]) + y1

        #Camera
        cx = [x1, float(p[i, 4]), float(p[i, 5])]
        cy = [y1, float(p[i, 6]), float(p[i, 7])]
        
        if index == 0:
            ax.fill(cx, cy, color='#ff7575')

        # Plot sensors using the x and y coordinates
        x = [x1]
        y = [y1]
        
        # for loop breaks this part for some weird reason, don't change
        rx, ry = rotate_lines(x1,y1,x2,y2,-40)
        x.append(rx)
        y.append(ry)

        rx, ry = rotate_lines(x1,y1,x2,y2,-20)
        x.append(rx)
        y.append(ry)

        x.append(x2)
        y.append(y2)

        rx, ry = rotate_lines(x1,y1,x2,y2,20)
        x.append(rx)
        y.append(ry)

        rx, ry = rotate_lines(x1,y1,x2,y2,40)
        x.append(rx)
        y.append(ry)
        
        ax.fill(x, y, color='g')

        # back sensor
        rx2, ry2 = rotate_lines(x1,y1,x2,y2,180)
        x = [x1, rx2]
        y = [y1, ry2]
        ax.plot(x, y, "-", linewidth=2, color='g')
        
        #Color
        point_color = p[i, 8]

        ax.plot(x1, y1,
                label='original', marker='o', color=point_color)
        # Set the x and y axis to display a fixed range

    # zoom
    ax.set_xlim([(-W * 1.10) / 2, (W * 1.10) / 2])
    ax.set_ylim([(-H * 1.10) / 2, (H * 1.10) / 2])

    # plot middle space
    SBW = 0.05
    SBH = 0.05
    ax.plot([-SBW / 2, SBW / 2], [-SBH / 2, -SBH / 2], color='k')
    ax.plot([-SBW / 2, SBW / 2], [SBH / 2, SBH / 2], color='k')
    ax.plot([-SBW / 2, -SBW / 2], [-SBH / 2, SBH / 2], color='k')
    ax.plot([SBW / 2, SBW / 2], [-SBH / 2, SBH / 2], color='k')

def rotate_lines(x1, y1, x2, y2, deg):
    theta = radians(deg)  # Convert angle from degrees to radians

    # Rotate each around whole polyline's center point
    px = cos(theta) * (x2-x1) - sin(theta) * (y2-y1) + x1
    py = sin(theta) * (x2-x1) + cos(theta) * (y2-y1) + y1

    # Replace vertices with updated values
    return px, py


ani = FuncAnimation(fig, animate, frames=row,
                    interval=500, repeat=False)

#plt.show()
plt.close()

# Save the animation as an animated GIF
ani.save("animator/simulation.gif", dpi=300,
         writer=PillowWriter(fps=10))
