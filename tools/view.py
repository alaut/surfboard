import numpy as np
import pyvista as pv
from scipy.constants import foot, inch
from shapely import get_parts

from tools.board import Board, axes, field

RANGES = dict(
    length=(5 * foot, 10 * foot),
    width=(16 * inch, 24 * inch),
    height=(2 * inch, 3.5 * inch),
    head_rocker=(-1 / (10 * foot), 0),
    tail_rocker=(-1 / (10 * foot), 0),
    side_rocker=(0, 1 / (2 * foot)),
    squareness=(1.5, 4),
    eggness=(-0.5, 0.5),
    center_cut=(0, 8 * inch),
    tail_cut=(0, 8 * inch),
)


def preview(board: Board, n=50):
    """show the board surface with one slider per parameter; sliders edit board in place"""
    grid = pv.RectilinearGrid(*axes(Board(**{k: max(r, key=abs) for k, r in RANGES.items()}), n))
    plotter = pv.Plotter()

    def update(name, value):
        setattr(board, name, value)
        plotter.add_mesh(field(board, grid).contour([0], scalars="F"), name="board")

    for i, (name, rng) in enumerate(RANGES.items()):
        v = 0.95 - 0.09 * i
        plotter.add_slider_widget(
            lambda value, name=name: update(name, value),
            rng,
            value=getattr(board, name),
            title=name,
            pointa=(0.02, v),
            pointb=(0.25, v),
            fmt="%.3g",  # rocker curvatures are ~1e-2 per metre
        )
    plotter.show()
    print(board)


def embed(part, z=None):
    """3D outline of a rib (x, y) placed at z, or of the stringer (z, y) at x = 0 when z is None"""
    blocks = []
    for poly in get_parts(part):
        for ring in [poly.exterior, *poly.interiors]:
            u, v = np.asarray(ring.coords).T
            blocks.append(pv.lines_from_points(np.c_[0 * u, v, u] if z is None else np.c_[u, v, np.full_like(u, z)]))
    return pv.merge(blocks)


def show(spine, ribs, stations):
    """show the assembled frame"""
    plotter = pv.Plotter()
    plotter.add_mesh(pv.merge([embed(spine)] + [embed(r, z) for r, z in zip(ribs, stations)]))
    plotter.show()
