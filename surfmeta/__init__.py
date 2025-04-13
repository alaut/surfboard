
import pyvista as pv
import os
import matplotlib.pyplot as plt
import numpy as np

from contourpy import contour_generator
from dataclasses import dataclass

import ezdxf


@dataclass
class Board:

    units: str = 'inches'

    ly: float = 2.5
    lx: float = 19.5
    lz: float = 76

    tw: float = 1  # wall thickness

    # spine properties
    w_spine: float = 1
    x_spine: tuple = (-6, 0, 6)

    r_core: float = 1/4

    name: str = 'board'

    rz1: float = -20*12
    rz2: float = -37*12
    rx: float = 4*12

    n: float = 2
    k: float = -0.2  # eggness

    x_shift: float = 1.5    # shifts x coordainte to form point/taper
    x_shift: float = 2.5    # shifts x coordainte to form point/taper

    tail_cut: float = 4    # portion removed from tail

    rotation: tuple = (0, 0, 0)
    position: tuple = (0, 0, 0)

    def fsd(self, x, y, z):
        """return FSD

        references:
            https://www.ntop.com/resources/blog/understanding-the-basics-of-b-reps-and-implicits/"""

        # apply parabolic deformation
        y = y + (z > 0) * z**2/(2*self.rz1) +\
            (z <= 0)*z**2 / (2*self.rz2) + x**2/(2*self.rx)

        # apply ovoid deformation
        x = x*np.sqrt(1 + self.k*z/self.lz)

        # squeeze board along x
        dx = x + self.x_shift*sign(x)

        a = (self.lx + 2*self.x_shift)/2
        b = 0.5*self.ly
        c = self.lz/2/np.sqrt(1 - self.x_shift**2/a**2)

        ai = (self.lx - self.tw + 2*self.x_shift)/2
        bi = 0.5*(self.ly - self.tw)
        ci = (self.lz - self.tw)/2/np.sqrt(1 - self.x_shift**2/ai**2)

        # define from outer shell
        Fo = np.abs(dx/a)**self.n + (y/b)**2 + np.abs(z/c)**self.n - 1

        # define inner shell
        Fi = np.abs(dx/ai)**self.n + (y/bi)**2 + np.abs(z/ci)**self.n - 1

        # cut spines (parabolic definition)
        Fs = [1 - (2*(x - xc) / self.w_spine)**2 for xc in self.x_spine]
        Fs = np.max(np.stack(Fs), axis=0)

        # add cores inside spines
        Fc = [(x - xc)**2 + y**2 - self.r_core**2 for xc in self.x_spine]
        Fc = np.min(np.stack(Fc), axis=0)

        # chop back of board
        Fb1 = -(z - (-self.lz/2 + self.tail_cut))
        Fb2 = -(z - (-self.lz/2 + self.tail_cut + self.tw/2))

        # the magic
        # F = Fo*np.maximum(Fi, Fs*Fc)
       
        
        Fo = np.maximum(Fo, Fb1)
        Fi = np.maximum(Fi, Fb2)

        # F = Fi*Fo

        # F = Fo*Fi
        F = Fo*np.maximum(Fi, Fs*Fc)
        # F = Fo

        # F = np.clip(F, -1, 1)

        return F

    def slice(self, x=None, y=None, z=None, show=True,
              nx=100, ny=100, nz=100, sx=1.5, sy=1.5, sz=1.5):
        """return slice"""
        r = {
            'x': sx*self.lx*np.linspace(-1/2, 1/2, nx),
            'y': sy*self.ly*np.linspace(-1/2, 1/2, ny),
            'z': sz*self.lz*np.linspace(-1/2, 1/2, nz),
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

        F = self.fsd(**points)
        lines = contour_generator(U, V, F).lines(0)

        if show:

            fig, ax = plt.subplots()
            pcm = ax.pcolormesh(U, V, F)
            for line in lines:
                ax.plot(*line.T)
            # fig.colorbar(pcm, ax=ax, label='F')

            ax.set_xlabel(f"{k1} ({self.units})")
            ax.set_ylabel(f"{k2} ({self.units})")
            ax.set_aspect('equal')

        return lines

    def show(self, filename=None,
             nx=100, ny=100, nz=100, sx=1.5, sy=1.5, sz=1.5):

        xq = sx*self.lx*np.linspace(-1/2, 1/2, nx)
        yq = sy*self.ly*np.linspace(-1/2, 1/2, ny)
        zq = sz*self.lz*np.linspace(-1/2, 1/2, nz)

        X, Y, Z = np.meshgrid(xq, yq, zq)
        V = self.fsd(X, Y, Z)

        grid = pv.StructuredGrid(X, Y, Z)
        grid["scalars"] = V.ravel(order='F')

        mesh = grid.contour(isosurfaces=[0])

        if self.rotation:
            mesh = mesh.rotate_x(self.rotation[0])
            mesh = mesh.rotate_y(self.rotation[1])
            mesh = mesh.rotate_z(self.rotation[2])

        mesh = mesh.translate(self.position)

        if filename:
            mesh.save(filename)

        self.plotter = pv.Plotter()
        self.plotter.add_mesh(mesh, opacity=0.3, show_scalar_bar=False)
        self.plotter.show_grid()
        self.plotter.add_axes_at_origin()
        self.plotter.show_axes_all()
        self.plotter.enable_parallel_projection()

        # for view, zoom in zip(['zy', 'zx', 'xy'], [1.25, 1.25, 5]):
        #     plotter.camera_position = view
        #     plotter.camera.zoom(zoom)
        #     plotter.save_graphic(f'{self.name}.{view}.svg')
        self.plotter.save_graphic(f'{self.name}.svg')


def sign(x):
    """modified to be positive at x = 0"""
    return np.where(x == 0, 1, np.sign(x))


def dxfwrite(contours, filename, s=1):
    """export contours as dxf file"""

    doc = ezdxf.new()
    msp = doc.modelspace()

    for contour in contours:
        points = [(x*s, y*s) for x, y in contour]
        msp.add_polyline2d(points)

    doc.saveas(filename)

    print(f"wrote {filename}")
