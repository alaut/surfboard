import pyvista as pv
from surfmeta import Board, dxfwrite
import numpy as np
import matplotlib.pyplot as plt

import pandas as pd

import os


def demo():
    """generate boards"""

    df = pd.read_excel('boards.xlsx').fillna(0)
    print(df)

    options = [row.to_dict() for i, row in df.iterrows()]

    boards = [Board(**option) for option in options]
    boards = [boards[-1]]

    for board in boards:

        # export 3D mesh
        board.generate_mesh(nx=150, ny=150, nz=500)

        # view 3D model
        # plotter = pv.Plotter()
        # plotter.add_mesh(board.mesh, opacity=0.2)
        # plotter.show()

        # make slices
        zq = np.arange(-board.lz/2, board.lz/2, 1/8)
        # zq = np.arange(-board.lz/2, board.lz/2, 2)
        N = len(zq)
        slices = [board.slice(z=z, nx=300, ny=300)[0] for z in zq]
        M = 24*2

        n = (N + M - 1) // M  # Number of columns (ceiling of N/M)
        dxf = []

        for i, lines in enumerate(slices):
            for line in lines:
                row = i // n  # Which row (0 to M-1)
                col = i % n   # Which column (0 to n-1)
                dx = 22.25 * col  # Horizontal offset based on column
                dy = 3 * row   # Vertical offset based on row
                dxf.append(line + np.stack([dx, dy]))

        # fig, ax = plt.subplots()
        # for line in dxf:
        #     ax.plot(*line.T)
        # ax.set_aspect('equal')

        dxfwrite(dxf, f"{board.name}.dxf")
        # plt.show()

        for i, z in enumerate(slices):
            lines, F = board.slice(z=z, nx=300, ny=300)
            dxfwrite(lines, filename=f"{board.name}.{i:03d}.dxf", s=1)

            fig, ax = plt.subplots()
            ax.pcolormesh(*F)
            for line in lines:
                ax.plot(*line.T)

            ax.set_aspect('equal')
            ax.set_title(f"{i:03d}")
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            fig.savefig(f"{board.name}.{i:03d}.png")
            plt.close(fig)

        os.system(
            f'magick.exe -delay 10 "{board.name}*.png" "{board.name}.gif"')


if __name__ == "__main__":
    demo()
