import numpy as np
from scipy.constants import foot, inch, milli

from tools.board import Board
from tools.cut import dxf, frame, profile, section, split, tile
from tools.view import preview, show

board = Board(
    length=6 * foot + 4 * inch,
    width=19.5 * inch,
    height=2.5 * inch,
    head_rocker=-1 / (20 * foot),
    tail_rocker=-1 / (37 * foot),
    side_rocker=1 / (4 * foot),
    squareness=2,
    eggness=-0.2,
    center_cut=2.5 * inch,
    tail_cut=4 * inch,
)
pitch = 6 * inch
fab = dict(slot=6 * milli, skin=3 * milli, web=12 * milli)  # slot = measured sheet + fit clearance
bed = (44 * inch, 30 * inch)  # outline drawn by the old dxfwrite
kerf = 0.15 * milli

if __name__ == "__main__":
    preview(board)
    stations = np.arange(board.tail_cut - board.length / 2, board.length / 2, pitch)[1:]
    spine, ribs = frame(profile(board), [section(board, z) for z in stations], stations, **fab)
    show(spine, ribs, stations)

    parts = {f"S{i}": p for i, p in enumerate(split(spine, stations[[5]] + pitch / 2))}
    parts |= {f"R{i}": r for i, r in enumerate(ribs)}
    for i, sheet in enumerate(tile(parts, bed)):
        dxf(sheet, f"shorty.{i}.dxf", kerf)
