import numpy as np
from scipy.constants import foot, inch, milli

from tools.board import Board
from tools.cut import dxf, frame, profile, section, split, tile
from tools.view import export, preview, show

board = Board(
    length=8 * foot,
    width=22 * inch,
    height=2.75 * inch,
    head_rocker=-1 / (50 * foot),
    tail_rocker=-1 / (200 * foot),
    side_rocker=1 / (5 * foot),
    squareness=3,
    eggness=0.1,
    center_cut=6 * inch,
    tail_cut=1 * inch,
)
pitch = 6 * inch
fab = dict(slot=6 * milli, skin=3 * milli, web=12 * milli)  # slot = measured sheet + fit clearance
bed = (44 * inch, 30 * inch)  # outline drawn by the old dxfwrite
kerf = 0.15 * milli

if __name__ == "__main__":
    export(board, __file__.replace(".py", ".html"))
    preview(board)
    stations = np.arange(board.tail_cut - board.length / 2, board.length / 2, pitch)[1:]
    spine, ribs = frame(profile(board), [section(board, z) for z in stations], stations, **fab)
    show(spine, ribs, stations)

    parts = {f"S{i}": p for i, p in enumerate(split(spine, stations[[4, 9]] + pitch / 2))}
    parts |= {f"R{i}": r for i, r in enumerate(ribs)}
    for i, sheet in enumerate(tile(parts, bed)):
        dxf(sheet, f"longboard.{i}.dxf", kerf)
