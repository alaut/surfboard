import numpy as np

from stl import mesh


def triangulate(x):
    """subdivide structured grid into triangles"""

    tl = x[:-1, :-1]
    tr = x[:-1, 1:]
    br = x[1:, :-1]
    bl = x[1:, 1:]

    return np.stack([[tl, tr, br], [tr, bl, br]], axis=-1)


def surf2tri(r, stlname=None, flip=False):
    """convert structured surface grid to triangular mesh"""

    # setup indices
    dim = r.shape[1:]

    # get gridded indices
    I, J = np.indices(dim)

    # triangulate indices
    i = triangulate(I)
    j = triangulate(J)

    # linearize indices
    con = np.ravel_multi_index((i, j), dim)

    # flip normals
    con = con[::-1] if flip else con

    pts = r.reshape(3, -1)
    con = con.reshape(3, -1)
    tri = pts.T[con.T, :]

    if stlname:

        stl_mesh = mesh.Mesh(np.zeros(tri.shape[0], dtype=mesh.Mesh.dtype))
        stl_mesh.vectors = tri

        stl_mesh.save(f'{stlname}.stl')

    return pts, con
