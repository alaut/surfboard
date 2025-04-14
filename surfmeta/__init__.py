
import pyvista as pv
import os
import matplotlib.pyplot as plt
import numpy as np

from contourpy import contour_generator
from dataclasses import dataclass

import ezdxf


@dataclass
class Board:

    # dimensions
    ly: float = 2.5
    lx: float = 19.5
    lz: float = 76

    # wall thickness
    tw: float = 1

    # rockers
    rz1: float = 0
    rz2: float = 0
    rx0: float = 0

    # squareness
    n: float = 2

    # eggness
    k: float = -0.2

    # flat cuts
    center_cut: float = 2.5    # shifts x coordainte to form point/taper
    tail_cut: float = 4    # portion removed from tail

    # spine properties
    spine_width: float = 1
    spine_position: tuple = (-6, 0, 6)
    spine_radius: float = 1/4

    # export properties
    name: str = 'board'

    rotation: tuple = (0, 0, 0)
    position: tuple = (0, 0, 0)

    # oversize factors
    sx: float = 1.25
    sy: float = 1.25
    sz: float = 1.25

    comments: str = None

    def __post_init__(self):
        os.makedirs(os.path.dirname(self.name), exist_ok=True)
        if self.comments:
            print(self.comments)

    def sdf(self, x, y, z):
        """return signed distance field

        references:
            https://www.ntop.com/resources/blog/understanding-the-basics-of-b-reps-and-implicits/"""

        # apply parabolic deformation
        y = 0.5*self.rz1*z**2*(z > 0) + \
            0.5*self.rz2*z**2*(z <= 0) + \
            0.5*self.rx0*x**2 + y

        # apply ovoid deformation
        x = x*np.sqrt(1 + self.k*z/self.lz)

        # squeeze board along x
        dx = x + self.center_cut*sign(x)

        a = (self.lx + 2*self.center_cut)/2
        b = 0.5*self.ly
        c = self.lz/2/np.sqrt(1 - self.center_cut**2/a**2)

        ai = (self.lx - self.tw + 2*self.center_cut)/2
        bi = 0.5*(self.ly - self.tw)
        ci = (self.lz - self.tw)/2/np.sqrt(1 - self.center_cut**2/ai**2)

        # define from outer shell
        Fo = np.abs(dx/a)**self.n + (y/b)**2 + np.abs(z/c)**self.n - 1

        # define inner shell
        Fi = np.abs(dx/ai)**self.n + (y/bi)**2 + np.abs(z/ci)**self.n - 1

        # cut spines (parabolic definition)
        Fs = [1 - (2*(x - xc) / self.spine_width) **
              2 for xc in self.spine_position]
        Fs = np.max(np.stack(Fs), axis=0)

        # add cores inside spines
        Fc = [(x - xc)**2 + y**2 - self.spine_radius **
              2 for xc in self.spine_position]
        Fc = np.min(np.stack(Fc), axis=0)

        # chop back of board
        if self.tail_cut > 0:
            Fb1 = -(z - (-self.lz/2 + self.tail_cut))
            Fb2 = -(z - (-self.lz/2 + self.tail_cut + self.tw/2))

            # cut tail
            Fo = np.maximum(Fo, Fb1)
            Fi = np.maximum(Fi, Fb2)

        # put it all together
        F = Fo*np.maximum(Fi, Fs*Fc)

        F = np.clip(F, -1, 1)

        return F

    def slice(self, x=None, y=None, z=None, nx=100, ny=100, nz=100):
        """return slice"""

        r = {
            'x': self.sx*self.lx*np.linspace(-1/2, 1/2, nx),
            'y': self.sy*self.ly*np.linspace(-1/2, 1/2, ny),
            'z': self.sz*self.lz*np.linspace(-1/2, 1/2, nz),
        }

        if x is not None:
            k1 = 'z'
            k2 = 'y'
            points = {'x': x}
        if y is not None:
            k1 = 'z'
            k2 = 'x'
            points = {'y': y}
        if z is not None:
            k1 = 'x'
            k2 = 'y'
            points = {'z': z}

        U, V = np.meshgrid(r[k1], r[k2])
        points[k1] = U
        points[k2] = V

        F = self.sdf(**points)
        lines = contour_generator(U, V, F).lines(0)

        return lines, [U, V, F]

    def generate_mesh(self, nx=100, ny=100, nz=100):
        """generate mesh of given geometry"""

        xq = self.sx*self.lx*np.linspace(-1/2, 1/2, nx)
        yq = self.sy*self.ly*np.linspace(-1/2, 1/2, ny)
        zq = self.sz*self.lz*np.linspace(-1/2, 1/2, nz)

        X, Y, Z = np.meshgrid(xq, yq, zq)
        V = self.sdf(X, Y, Z)

        grid = pv.StructuredGrid(X, Y, Z)
        grid["scalars"] = V.ravel(order='F')

        self.mesh = grid.contour(isosurfaces=[0])

        if self.rotation:
            self.mesh = self.mesh.rotate_x(self.rotation[0])
            self.mesh = self.mesh.rotate_y(self.rotation[1])
            self.mesh = self.mesh.rotate_z(self.rotation[2])

        self.mesh = self.mesh.translate(self.position)

        self.mesh.save(f"{self.name}.stl")


def sign(x):
    """modified to be positive at x = 0"""
    return np.where(x == 0, 1, np.sign(x))


def dxfwrite(contours, filename, s=1, show=False):
    """export contours as dxf file"""

    if show:
        fig, ax = plt.subplots()
        for line in contours:
            ax.plot(*line.T*s)
        ax.set_title(filename)
        ax.set_aspect('equal')
        plt.show()

    doc = ezdxf.new()
    msp = doc.modelspace()

    for contour in contours:
        points = [(x*s, y*s) for x, y in contour]
        msp.add_polyline2d(points)

    doc.saveas(filename)

    print(f"saved {filename}")


def tile(slices, rows=8, col_spacing=22.25, row_spacing=3):
    """Take list of contours and tile to a grid and export as a single DXF."""
    N = len(slices)

    cols = (N + rows - 1) // rows

    print(f'tiling {N} slices into {rows} rows x {cols} columns')

    all_slices = []

    for i, lines in enumerate(slices):
        for line in lines:
            offset = [col_spacing * (i // rows), row_spacing * (i % rows)]
            all_slices.append(line + np.stack(offset))

    return all_slices
