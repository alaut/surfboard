import ezdxf
import numpy as np
import pyvista as pv
from contourpy import contour_generator
from scipy.constants import milli
from shapely import LineString, Polygon, box, get_parts, union_all
from shapely.affinity import translate

from tools.board import Board, axes, field


def polygon(lines):
    """union of closed contour lines"""
    return union_all([Polygon(line) for line in lines if len(line) > 3])


def span(part, u):
    """lowest and highest v of part along the line at first coordinate u"""
    _, v0, _, v1 = part.intersection(LineString([(u, -1), (u, 1)])).bounds
    return v0, v1


def section(board: Board, z, n=400):
    """rib outline at z, in (x, y)"""
    x, y, _ = axes(board, n)
    F = field(board, pv.RectilinearGrid(x, y, [z]))["F"].reshape(n, n)
    return polygon(contour_generator(x, y, F).lines(0))


def profile(board: Board, n=400):
    """stringer outline at x = 0, in (z, y)"""
    _, y, z = axes(board, n)
    F = field(board, pv.RectilinearGrid([0.0], y, z))["F"].reshape(len(z), n).T
    return polygon(contour_generator(z, y, F).lines(0))


def frame(spine, ribs, stations, slot, skin, web):
    """inset by skin, cross-lap ribs (slot from below) onto the stringer (slot from above), lighten ribs
    https://en.wikipedia.org/wiki/Lap_joint#Cross_lap"""
    spine = spine.buffer(-skin)
    out = []
    for rib, z in zip(ribs, stations):
        rib = rib.buffer(-skin)
        ym = np.mean(span(rib, 0))
        holes = rib.buffer(-web).difference(box(-web, -1, web, 1))
        out.append(rib.difference(holes).difference(box(-slot / 2, -1, slot / 2, ym)))
        spine = spine.difference(box(z - slot / 2, ym, z + slot / 2, 1))
    return spine, out


def split(part, cuts, key=20 * milli):
    """cut part at first coordinate u = cuts, each with a dovetail key at mid-height
    https://en.wikipedia.org/wiki/Dovetail_joint"""
    pieces = []
    for u in cuts:
        v = np.mean(span(part, u))
        tail = Polygon([(u, v - key / 4), (u + key / 2, v - key / 2), (u + key / 2, v + key / 2), (u, v + key / 4)])
        u0, v0, _, v1 = part.bounds
        pieces.append(part.intersection(box(u0, v0, u, v1).union(tail)))
        part = part.difference(pieces[-1])
    return pieces + [part]


def tile(parts: dict, bed, gap=5 * milli):
    """shelf-pack parts by bounding box onto sheets of size bed, tallest first
    https://en.wikipedia.org/wiki/Bin_packing_problem"""
    sheets, u, v, row = [{}], gap, gap, 0
    for name, p in sorted(parts.items(), key=lambda kv: kv[1].bounds[1] - kv[1].bounds[3]):
        u0, v0, u1, v1 = p.bounds
        if u + u1 - u0 > bed[0]:
            u, v, row = gap, v + row + gap, 0
        if v + v1 - v0 > bed[1]:
            sheets.append({})
            u, v, row = gap, gap, 0
        sheets[-1][name] = translate(p, u - u0, v - v0)
        u, row = u + u1 - u0 + gap, max(row, v1 - v0)
    return sheets


def dxf(parts: dict, filename, kerf=0.0, label=5 * milli):
    """write parts in mm: outlines grown by kerf/2 on layer CUT, names on layer ENGRAVE"""
    doc = ezdxf.new(units=ezdxf.units.MM)
    msp = doc.modelspace()
    for name, p in parts.items():
        for poly in get_parts(p.buffer(kerf / 2)):
            for ring in [poly.exterior, *poly.interiors]:
                msp.add_lwpolyline(np.asarray(ring.coords) / milli, close=True, dxfattribs={"layer": "CUT"})
        text = msp.add_text(name, height=label / milli, dxfattribs={"layer": "ENGRAVE"})
        text.set_placement(np.asarray(p.representative_point().coords[0]) / milli)
    doc.saveas(filename)
