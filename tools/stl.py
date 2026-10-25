import pyvista as pv
from shapely import get_parts, linestrings, polygonize, union_all


def section(mesh: pv.PolyData, normal, origin, uv):
    """cross-section of a closed mesh as a polygon in coordinates uv: (0, 1) for normal z, (2, 1) for normal x"""
    cut = mesh.slice(normal=normal, origin=origin)
    segments = cut.points[cut.lines.reshape(-1, 3)[:, 1:]][..., list(uv)]
    return union_all(get_parts(polygonize(linestrings(segments))))
