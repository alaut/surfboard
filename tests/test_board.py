import numpy as np
import pyvista as pv

from designs.longboard import board as longboard
from tools.board import Board, axes, field
from tools.cut import profile, section, span


def test_dimensions(board=longboard):
    """length, width at z = 0 and height at x = z = 0 match spec for squareness 3"""
    z0, _, z1, _ = profile(board).bounds
    x0, _, x1, _ = section(board, 0).bounds
    y0, y1 = span(profile(board), 0)
    measured = [z1 - z0, x1 - x0, y1 - y0]
    np.testing.assert_allclose(measured, [board.length - board.tail_cut, board.width, board.height], rtol=1e-3)


def test_volume(board=Board()):
    """undeformed board is an ellipsoid, V = π W H L / 6
    https://en.wikipedia.org/wiki/Ellipsoid#Volume"""
    surface = field(board, pv.RectilinearGrid(*axes(board, 100))).contour([0], scalars="F")
    np.testing.assert_allclose(surface.volume, np.pi / 6 * board.width * board.height * board.length, rtol=1e-2)


if __name__ == "__main__":
    test_dimensions()
    test_volume()
