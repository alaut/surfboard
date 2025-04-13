# takes input STL file and slices it into svg's

import numpy as np
import matplotlib.pyplot as plt
import pyvista as pv
from glob import glob

import trimesh


def slice_stl(file, nx=50, ny=10, nz=10):
    mesh = trimesh.load(file)

    xmin, ymin, zmin = np.min(mesh.vertices, axis=0)
    xmax, ymax, zmax = np.max(mesh.vertices, axis=0)

    x = np.linspace(xmin, xmax, nx)
    y = np.linspace(ymin, ymax, ny)
    z = np.linspace(zmin, zmax, nz)

    plotter = pv.Plotter()
    plotter.add_mesh(mesh)
    plotter.add_axes()
    plotter.add_axes_at_origin()
    plotter.show()

    for i, x0 in enumerate(x):
        r = [x0, 0, 0]
        n = [1, 0, 0]

        print(r)

        section = mesh.section(plane_normal=n, plane_origin=r)

        if section:
            contour = section.to_planar(normal=n, check=False)[0]

            c = [contour.vertices[item.points].T for item in contour.entities]

            fig, ax = plt.subplots()
            for z, y in c:
                ax.plot(z, y)
            ax.plot(0, 0, 'rs')
            ax.set_xlim(-10, 10)
            ax.set_ylim(-2, 2)
            ax.set_aspect('equal')

            fig.savefig(f"./data/svg/x0={x0:+0.2f}.png")
            ax.axis('off')
            fig.tight_layout()
            fig.savefig(f"./data/svg/x0={x0:+0.2f}.svg")
            plt.close(fig)


def main():
    folder = '../wood board/AKU Shaper Files/3D Models/'

    files = glob(f"{folder}*.stl")
    files = [f"{folder}test1new.stl"]

    for file in files:

        slice_stl(file)


if __name__ == "__main__":
    main()
