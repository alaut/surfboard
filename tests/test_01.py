import matplotlib.pyplot as plt

import numpy as np

from contourpy import contour_generator


def sign(x):
    return np.where(x == 0, 1, np.sign(x))


def tanh(x):
    return np.where(x == 0, x, np.tanh(x))


l = 8
w = 2


Z, X = np.meshgrid(
    1.5*np.linspace(-l/2, l/2, 301),
    1.5*np.linspace(-w/2, w/2, 299)
)

c = 1/2

a = l/2
b = w/2

# adjust to maintain sizing
bp = (w + 2*c)/2
ap = a/np.sqrt(1 - c**2/bp**2)


z0 = -3
sdf = [
    Z**2/a**2 + X**2/b**2 - 1,  # standard ellipse
    np.maximum(-(Z-z0), Z**2/a**2 + X**2/b**2 - 1),
    (Z < z0) + (Z**2/a**2 + X**2/b**2 - 1),
    Z**2/ap**2 + (X + c*sign(X))**2/bp**2 - 1
]


for f in sdf:
    fig, ax = plt.subplots()
    pcm = ax.pcolormesh(Z, X, f)
    lines = contour_generator(Z, X, f).lines(0)

    for line in lines:
        ax.plot(*line.T, 'm-')
    ax.set_aspect('equal')
    fig.colorbar(pcm, ax=ax)

plt.show()
