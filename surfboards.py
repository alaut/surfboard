import matplotlib.pyplot as plt
from dataclasses import dataclass

import numpy as np

from stl import mesh


@dataclass
class Surfboard:
    """defines standard surfboard parametric shape"""

    name: str = 'Board'

    units = 'ft'

    w: float = 2.5
    h: float = 1/4
    l: float = 9

    k: float = 0.1
    fz: float = 20
    fx: float = -3

    def __post_init__(self, nu=29, nv=31):

        # parameterize
        u, v = np.meshgrid(
            np.linspace(np.pi, 0, nu),
            np.linspace(-np.pi, np.pi, nv)
        )

        # define ellipsoid
        x = self.w/2*np.sin(u)*np.cos(v)
        y = self.h/2*np.sin(u)*np.sin(v)
        z = self.l/2*np.cos(u)

        # apply ovoid (https://www.mathematische-basteleien.de/eggcurves.htm)
        x = x*np.sqrt(1 + self.k*z)

        # apply parabolic deformation
        y = y + z**2/(4*self.fz) + x**2/(4*self.fx)

        # store grid
        self.r = np.stack([x, y, z])

    def show(self, ind=[(0, 1), (2, 0), (2, 1)], axes={0: 'x', 1: 'y', 2: 'z'}):

        for i, j in ind:

            fig, ax = plt.subplots()

            ax.plot(self.r[i], self.r[j])
            ax.plot(self.r[i].T, self.r[j].T)
            ax.set_xlabel(f"{axes[i]} ({self.units})")
            ax.set_ylabel(f"{axes[j]} ({self.units})")
            ax.set_aspect('equal')
            ax.set_title(self)

            fig.savefig(f"{self.name}.{i}-{j}.svg")

    def triangulate(self, export=False):

        x, y, z = self.r
        _, m, n = self.r.shape
        num_faces = 2 * (m - 1) * (n - 1)  # Two triangles per grid cell

        # Create an empty mesh for STL
        self.tri = mesh.Mesh(np.zeros(num_faces, dtype=mesh.Mesh.dtype))

        face_index = 0
        for i in range(m - 1):
            for j in range(n - 1):
                # Define vertices of two triangles per grid cell
                v1 = [x[i, j], y[i, j], z[i, j]]
                v2 = [x[i + 1, j], y[i + 1, j], z[i + 1, j]]
                v3 = [x[i, j + 1], y[i, j + 1], z[i, j + 1]]
                v4 = [x[i + 1, j + 1], y[i + 1, j + 1], z[i + 1, j + 1]]

                # Triangle 1: (v1, v2, v3)
                self.tri.vectors[face_index] = [v1, v2, v3]
                face_index += 1

                # Triangle 2: (v2, v4, v3)
                self.tri.vectors[face_index] = [v2, v4, v3]
                face_index += 1

        if export:
            self.tri.save(f"{self.name}.stl")


if __name__ == "__main__":

    surfboard = Surfboard()

    surfboard.triangulate(export=True)
    surfboard.show()

    plt.show()
