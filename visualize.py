import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

def update_lines(num):
    """Update 3d points with random
    """
    dx, dy, dz = np.random.random((3,)) * 255 * 2 - 255  # replace this line with code to get data from serial line
    text.set_text("{:d}: [{:.0f},{:.0f},{:.0f}]".format(num, dx, dy, dz))  # for debugging
    x.append(dx)
    y.append(dy)
    z.append(dz)
    graph._offsets3d = (x, y, z)
    return graph,

def plot3d_anim():
    """Plots an animated 3d plot
    """
    global x, y, z
    x = []
    y = []
    z = []

    global fig, graph
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111, projection="3d")
    graph = ax.scatter(x, y, z, c='orange')
    global text
    text = fig.text(0, 1, "TEXT", va='top')  # for debugging

    ax.set_xlim3d(-255, 255)
    ax.set_ylim3d(-255, 255)
    ax.set_zlim3d(-255, 255)

    # Creating the Animation object
    ani = animation.FuncAnimation(fig, update_lines, frames=200, interval=100, blit=False)
    plt.show()


def plot3d(x,y,z):
    """Show 3d points

    Args:
        x: (1,N) array
        y: (1,N) array
        z: (1,N) array

    Returns:
        None
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c='orange')
    plt.show()

def plot3d_test():
    x = [1,2,3,4,5,6,7,8,9,10]
    y = [5,6,2,3,13,4,1,2,4,8]
    z = [2,3,3,3,5,7,9,11,9,10]
    plot3d(x,y,z)

if __name__ == '__main__':
    plot3d_test()