import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np


def show_vectors(vectors, title="Vectors", origin=(0, 0)):
    rows, cols = vectors.shape

    for i in range(0, cols):
        xs = [origin[0], vectors[0, i]]
        ys = [origin[1], vectors[1, i]]
        plt.plot(xs, ys, "-", linewidth=2)
    
    config_plot(title, vectors, 'v')

def show_points(points, title="Points"):
    rows, cols = points.shape

    for i in range(0, cols):
        xs = points[0, i]
        ys = points[1, i]
        plt.plot(xs, ys, "o", linewidth=2)
    
    config_plot(title, points, 'p')

def config_plot(title, data, data_type):
    rows, cols = data.shape
    
    plt.title(title)
    plt.grid(b=True, which="major")
    #plt.legend([f'{data_type}{i+1}' for i in range(cols)])
    plt.axis('scaled')
    plt.plot(0, 0, "ok")

    plt.xlabel("X-Axis")
    plt.ylabel("Y-Axis")
    
    max_values = 1.3 * np.max(abs(data.T), axis = 0)
    plt.xlim([-1, 1])
    plt.ylim([-1, 1])
    
    plt.show()

def plot():
    with open('./trajectory.dat', 'r') as f:
        lines = f.readlines()
        vectorList = [list(map(float,line.split(", "))) for line in lines]
        vectors = np.array(vectorList)[:,:2]
    show_points(np.transpose(vectors[:,:2]))


if __name__ == "__main__":
    plot()
