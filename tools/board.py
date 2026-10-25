from dataclasses import dataclass

import numpy as np
import pyvista as pv
from scipy.constants import foot, inch


@dataclass
class Board:
    """outer shape: superellipsoid with egg taper, center cut and parabolic rocker"""

    length: float = 6 * foot + 4 * inch  # tip to tip, before tail_cut
    width: float = 19.5 * inch  # at z = 0
    height: float = 2.5 * inch  # at x = z = 0
    head_rocker: float = 0  # curvature, negative lifts the nose
    tail_rocker: float = 0
    side_rocker: float = 0
    squareness: float = 2
    eggness: float = 0
    center_cut: float = 0  # x shift forming a pointed nose
    tail_cut: float = 0  # length removed from the tail


def axes(board: Board, n=400):
    """sample axes x, y, z enclosing the board; y spans twice the rocker sagitta L²/8R"""
    s = board.height + abs(board.side_rocker) * board.width**2
    s += max(abs(board.head_rocker), abs(board.tail_rocker)) * board.length**2 / 4
    return (
        np.linspace(-board.width, board.width, n),
        np.linspace(-s, s, n),
        np.linspace(-0.55 * board.length, 0.55 * board.length, 4 * n),
    )


def field(board: Board, probe: pv.DataSet) -> pv.DataSet:
    """write level function F (negative inside) onto probe
    https://en.wikipedia.org/wiki/Superellipsoid, https://www.mathematische-basteleien.de/eggcurves.htm"""
    x, y, z = probe.points.T
    p, cc = board.squareness, board.center_cut

    y = y + 0.5 * z**2 * np.where(z > 0, board.head_rocker, board.tail_rocker) + 0.5 * board.side_rocker * x**2
    x = x * np.sqrt(1 + board.eggness * z / board.length)
    dx = x + cc * np.where(x < 0, -1, 1)

    a = board.width / 2 + cc
    s = 1 - (cc / a) ** p  # x = 0 sits at dx = cc, so stretch b and c to keep height and length
    b = board.height / 2 / np.sqrt(s)
    c = board.length / 2 / s ** (1 / p)

    F = np.abs(dx / a) ** p + (y / b) ** 2 + np.abs(z / c) ** p - 1
    probe["F"] = np.maximum(F, (board.tail_cut - board.length / 2 - z) / c)
    return probe
