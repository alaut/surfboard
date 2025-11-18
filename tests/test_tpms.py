import matplotlib.pyplot as plt
from surfmeta import gyroid
import numpy as np
import pyvista as pv


def signed_volume(mesh):
    """compute signed volume fo mesh"""

    # Extract points and triangle faces
    points = mesh.points
    # Skip first element (3 for triangles)
    faces = mesh.faces.reshape(-1, 4)[:, 1:]

    # Get vertices for all triangles
    v0 = points[faces[:, 0]]  # First vertex of each triangle
    v1 = points[faces[:, 1]]  # Second vertex
    v2 = points[faces[:, 2]]  # Third vertex

    # Compute cross product v1 x v2 for all triangles
    cross = np.cross(v1 - v0, v2 - v0)

    # Compute signed volume: dot(v0, cross) / 6.0 for all triangles
    volume = np.sum(np.einsum('ij,ij->i', v0, cross)) / 6.0

    return abs(volume)


def make_gyrosphere(c, show=False):
    """generate unit sphere with gyroid fill"""

    V = np.maximum(F_gyroid - c, F_sphere)

    grid = pv.StructuredGrid(x, y, z)
    grid["scalars"] = V.ravel(order='F')

    mesh = grid.contour(isosurfaces=[0])

    vol = signed_volume(mesh)

    if show:
        mesh.save('gyroid.stl')

        plotter = pv.Plotter()
        plotter.add_mesh(mesh)#, opacity=0.1)
        plotter.show()
    print(vol)

    return vol


if __name__ == "__main__":
    n = 50

    R = 3/4

    c = 0.9

    x, y, z = np.meshgrid(
        np.linspace(-1, 1, n - 1),
        np.linspace(-1, 1, n + 1),
        np.linspace(-1, 1, n),
    )   
    grid = pv.StructuredGrid(x, y, z)

    F_gyroid = gyroid(x, y, z, lam=1/2)

    grid['scalars'] = F_gyroid.ravel('F')

    plotter = pv.Plotter()
    plotter.add_volume(grid, opacity='linear')
    plotter.show()
    F_sphere = x**2 + y**2 + z**2 - R**2
    V_sphere = (4/3*np.pi*R**3)

    c = np.linspace(-2.0, 2.0, 30)

    make_gyrosphere(0, show=True)

    V_gyrosphere = np.asarray([make_gyrosphere(c) for c in c])

    fig, ax = plt.subplots()
    ax.plot(c, V_gyrosphere/V_sphere, '.-')
    ax.set_ylim(0, 1)
    ax.set_xlabel('c')
    ax.set_ylabel('fill fraction')
    fig.savefig('./data/figs/gyrosphere.png')
    plt.show()
