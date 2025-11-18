import numpy as np
import pyvista as pv
from scipy.constants import inch

from surfmeta.templates import shorty, longboard

boards = [shorty, longboard]


def main(brd, sx=0.6, sy=2, sz=0.6, d=0.25 * inch):

    # construct coarse volume to get board shape
    vol = pv.RectilinearGrid(
        np.linspace(-brd.width * sx, brd.width * sx, 30),
        np.linspace(-brd.height * sy, brd.height * sy, 30),
        np.linspace(-brd.length * sz, brd.length * sz, 30),
    )

    # extract surface
    poly = brd.apply(vol).contour([0])

    # re-build volume with efficient bounds
    vol = pv.RectilinearGrid(
        np.linspace(poly.bounds.x_min, poly.bounds.x_max, 50),
        np.linspace(poly.bounds.y_min, poly.bounds.y_max, 50),
        np.linspace(poly.bounds.z_min, poly.bounds.z_max, 150),
    ).scale(1.05)

    # get upscaled outline
    poly = brd.apply(vol).contour([0])

    # slice through board
    z = np.arange(poly.bounds.z_min - d, poly.bounds.z_max + d, d)
    x = np.linspace(poly.bounds.x_min - d, poly.bounds.x_max + d, 300)
    y = np.linspace(poly.bounds.y_min - d, poly.bounds.y_max + d, 300)

    slices = pv.MultiBlock()
    for zq in z:
        grid = pv.RectilinearGrid(x, y, [zq])
        slice = brd.apply(grid).contour([0])
        slices.append(slice)

    # plot results
    plotter = pv.Plotter()
    # plotter.add_mesh(poly, opacity=0.2)
    # plotter.add_mesh(vol.outline())
    plotter.add_mesh(slices, show_scalar_bar=False, color="black")

    plotter.show()


if __name__ == "__main__":
    for board in boards:
        main(board)
