import ezdxf
import numpy as np
from scipy.constants import inch, milli

from designs.shorty import bed, board, fab, pitch
from tools.cut import dxf, frame, profile, section, span, split, tile


def test_cross_lap(board=board, pitch=pitch, fab=fab):
    """rib and stringer slots meet, and both parts reach the inset deck and bottom"""
    stations = np.arange(board.tail_cut - board.length / 2, board.length / 2, pitch)[1:]
    ribs = [section(board, z) for z in stations]
    spine, slotted = frame(profile(board), ribs, stations, **fab)
    inset = profile(board).buffer(-fab["skin"])
    for rib, plain, z in zip(slotted, ribs, stations):
        rib_bottom, rib_top = span(rib, 0)
        spine_bottom, spine_top = span(spine, z)
        expected = [spine_top, span(inset, z)[1], span(plain.buffer(-fab["skin"]), 0)[0]]
        np.testing.assert_allclose([rib_bottom, rib_top, spine_bottom], expected, atol=0.5 * milli)


def test_split(board=board, cut=5 * inch, key=20 * milli):
    """pieces add up to the stringer, the key overhangs the cut, and all fit on the bed"""
    spine = profile(board)
    pieces = split(spine, [cut], key)
    np.testing.assert_allclose(sum(p.area for p in pieces), spine.area, rtol=1e-9)
    np.testing.assert_allclose(pieces[0].bounds[2], cut + key / 2)

    sheets = tile({str(i): p for i, p in enumerate(pieces)}, bed)
    u0, v0, u1, v1 = np.array([p.bounds for sheet in sheets for p in sheet.values()]).T
    assert u0.min() >= 0 and v0.min() >= 0 and u1.max() <= bed[0] and v1.max() <= bed[1]


def test_dxf(board=board, kerf=0.15 * milli):
    """outline reads back in mm, grown by the kerf"""
    rib = section(board, 0)
    dxf({"R": rib}, "test_cut.dxf", kerf)
    x = np.array(ezdxf.readfile("test_cut.dxf").modelspace().query("LWPOLYLINE")[0].get_points("xy"))[:, 0]
    np.testing.assert_allclose(np.ptp(x) * milli, rib.bounds[2] - rib.bounds[0] + kerf, rtol=1e-4)


if __name__ == "__main__":
    test_cross_lap()
    test_split()
    test_dxf()
