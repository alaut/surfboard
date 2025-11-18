from scipy.constants import inch,   foot
import pyvista as pv
import matplotlib.pyplot as plt    
import numpy as np
 
from dataclasses import dataclass

import ezdxf


def gyroid(X, Y, Z, lam=1 * inch):
    """https://en.wikipedia.org/wiki/Gyroid"""

    k = 2 * np.pi / lam

    SX = np.sin(k * X)
    CX = np.cos(k * X)

    SY = np.sin(k * Y)
    CY = np.cos(k * Y)

    SZ = np.sin(k * Z)
    CZ = np.cos(k * Z)

    return SX * CY + SY * CZ + SZ * CX


@dataclass
class Board:
 
    height: float = 2.5 * inch
    width: float = 19.5 * inch
    length: float = 6 * foot + 4 * inch

    wall_thickness: float = 4 * inch

    head_rocker: float = 0
    tail_rocker: float = 0
    side_rocker: float = 0

    squareness: float = 2
    eggness: float = -0.2

    center_cut: float = 2.5 * inch  # shifts x coordainte to form point/taper
    tail_cut: float = 4 * inch  # portion removed from tail

    # spine properties
    spine_width: float = 1 * inch
    spine_position: tuple = (-6 * inch, 0, 6 * inch)
    spine_radius: float = 1 / 4 * inch

    def apply(self, ds: pv.DataSet):
        """return signed distance field"""

        x = ds.points[..., 0]
        y = ds.points[..., 1]
        z = ds.points[..., 2]

        # apply parabolic deformation
        y = (
            0.5 * self.head_rocker * z**2 * (z > 0)
            + 0.5 * self.tail_rocker * z**2 * (z <= 0)
            + 0.5 * self.side_rocker * x**2
            + y
        )

        # apply ovoid deformation
        x = x * np.sqrt(1 + self.eggness * z / self.length)

        # squeeze board along x
        dx = x + self.center_cut * sign(x)

        a = (self.width + 2 * self.center_cut) / 2
        b = 0.5 * self.height
        c = self.length / 2 / np.sqrt(1 - self.center_cut**2 / a**2)

        ai = (self.width - self.wall_thickness + 2 * self.center_cut) / 2
        bi = 0.5 * (self.height - self.wall_thickness)
        ci = (
            (self.length - self.wall_thickness)
            / 2
            / np.sqrt(1 - self.center_cut**2 / ai**2)
        )

        # define from outer shell
        Fo = (
            np.abs(dx / a) ** self.squareness
            + (y / b) ** 2
            + np.abs(z / c) ** self.squareness
            - 1
        )

        # define inner shell
        Fi = (
            np.abs(dx / ai) ** self.squareness
            + (y / bi) ** 2
            + np.abs(z / ci) ** self.squareness
            - 1
        )

        # cut spines (parabolic definition)
        Fs = [1 - (2 * (x - xc) / self.spine_width) ** 2 for xc in self.spine_position]
        Fs = np.max(np.stack(Fs), axis=0)

        # add cores inside spines
        Fc = [(x - xc) ** 2 + y**2 - self.spine_radius**2 for xc in self.spine_position]
        Fc = np.min(np.stack(Fc), axis=0)

        # chop back of board
        if self.tail_cut > 0:
            Fb1 = -(z - (-self.length / 2 + self.tail_cut))
            Fb2 = -(z - (-self.length / 2 + self.tail_cut + self.wall_thickness / 2))

            # cut tail
            Fo = np.maximum(Fo, Fb1)
            Fi = np.maximum(Fi, Fb2)

        # put it all together
        F = Fo * np.maximum(Fi, Fs * Fc)
        # F = Fo * np.maximum(Fi, Fs)

        # gyrooid infill
        Fg = np.abs(gyroid(x, y, z, lam=3 * inch)) - 0.95
        F = Fo * np.maximum(Fi, Fg)

        F = np.clip(F, -1, 1)

        ds["sdf"] = F

        return ds


def sign(x):
    """modified to be positive at x = 0"""
    return np.where(x == 0, 1, np.sign(x))

 


def dxfwrite(contours, filename, s=1, show=False):
    """export contours as dxf file"""

    if show:
        fig, ax = plt.subplots()
        for line in contours:
            ax.plot(*line.T * s)
        ax.set_title(filename)
        ax.set_aspect("equal")

        outline = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]) * np.stack(
            [44, 30]
        )

        ax.plot(*outline.T)

        fig.savefig(f"{filename}.png")

        plt.show()

    doc = ezdxf.new()
    msp = doc.modelspace()

    for contour in contours:
        points = [(x * s, y * s) for x, y in contour]
        msp.add_polyline2d(points)

    doc.saveas(filename)

    print(f"saved {filename}")


def tile(slices, rows=8, col_spacing=22.25, row_spacing=3):
    """Take list of contours and tile to a grid and export as a single DXF."""
    N = len(slices)

    cols = (N + rows - 1) // rows

    print(f"tiling {N} slices into {rows} rows x {cols} columns")

    all_slices = []

    for i, lines in enumerate(slices):
        for line in lines:
            offset = [col_spacing * (0.5 + i // rows), row_spacing * (0.5 + i % rows)]
            all_slices.append(line + np.stack(offset))

    return all_slices
