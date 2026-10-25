import numpy as np
import pyvista as pv

from tools import stl
from tools.board import Board, axes, field


def test_ellipse(board=Board()):
    """mesh sections of the undeformed board are ellipses, A = π/4 · W H and π/4 · L H
    https://en.wikipedia.org/wiki/Ellipse#Area"""
    mesh = field(board, pv.RectilinearGrid(*axes(board, 100))).contour([0], scalars="F")
    areas = [stl.section(mesh, "z", (0, 0, 0), (0, 1)).area, stl.section(mesh, "x", (0, 0, 0), (2, 1)).area]
    np.testing.assert_allclose(areas, np.pi / 4 * board.height * np.array([board.width, board.length]), rtol=1e-2)


if __name__ == "__main__":
    test_ellipse()
