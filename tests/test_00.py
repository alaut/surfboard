import pyvista as pv
from surfmeta import Board, dxfwrite, tile
import numpy as np
import matplotlib.pyplot as plt

import pandas as pd

import os
from scipy.constants import inch, milli, centi, foot


def export_slices(board):
    """makes 1/4 scale board using 1/4" slices"""

    # slice thickness
    thickness = 0.25 * inch
    thickness = 0.75 * inch

    # scale factor
    scale = 1 / 4

    # pick longitudinal slices
    zq = np.arange(-board.lz / 2, board.lz / 2, thickness / scale)

    slices = [board.slice(z=z, nx=500, ny=500) for z in zq]

    return pv.MultiBlock(slices)


from boards import boards


def demo():
    """generate boards"""

    # df = pd.read_excel("boards.xlsx").fillna(0)
    # print(df)

    # options = [row.to_dict() for i, row in df.iterrows()]

    # boards = [Board(**option) for option in options]
    # boards = [boards[-1]]

    for board in boards:

        # for z in np.linspace(-board.lz/2, board.lz/2, 30):
        #     x, y = np.meshgrid(
        #         np.linspace(-board.lx/2, board.lx/2, 50),
        #         np.linspace(-board.ly/2, board.ly/2, 50)
        #     )
        #     r = np.stack(np.broadcast_arrays(x, y, z))
        #     grid = pv.StructuredGrid(*r)
        #     grid.rotate_x(45, inplace=True)

        # F = board.sdf(**points)
        # lines = contour_generator(U, V, F).lines(0)

        # export 3D mesh
        board.generate_mesh(nx=150, ny=150, nz=500)

        slices = export_slices(board)
        slices.plot()

        dxf = tile([slice[0] for slice in slices], rows=30)
        # grids = [slice[-1] for slice in slices]
        # scale factor
        scale = 1 / 4
        dxfwrite(dxf, f"{board.name}_scale_{scale}_in.dxf", s=scale, show=True)

        # view 3D model
        plotter = pv.Plotter()

        # plotter.add_mesh(board.mesh, opacity=0.2)
        pv.global_theme.allow_empty_mesh = True
        for slice in slices:
            plotter.add_mesh(slice[-1], style="wireframe")
        plotter.add_mesh(board.mesh, opacity=0.2)
        plotter.show()

        # slice in long ways?
        # xq = np.arange(-board.lx/2, board.lx/2, 1)
        # slices = [board.slice(x=x, ny=150, nz=300) for x in xq]
        # dxf = tile([slice[0] for slice in slices], rows=np.inf, col_spacing=4)
        # dxfwrite(dxf, f"{board.name}_small_mm_long.dxf", s=25.4/6, show=True)

        if False:
            for i, (lines, F) in enumerate(slices):

                dxfwrite(lines, filename=f"{board.name}.{i:03d}.dxf", s=1)

                fig, ax = plt.subplots()
                ax.pcolormesh(*F)
                for line in lines:
                    ax.plot(*line.T)

                ax.set_aspect("equal")
                ax.set_title(f"{i:03d}")
                ax.set_xlabel("x")
                ax.set_ylabel("y")
                fig.savefig(f"{board.name}.{i:03d}.png")
                plt.close(fig)

            os.system(f'magick.exe -delay 10 "{board.name}*.png" "{board.name}.gif"')


if __name__ == "__main__":
    demo()
