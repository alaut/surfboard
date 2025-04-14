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
        for i, z in enumerate(np.arange(-board.lz/2, board.lz/2, 1)):
            lines, F = board.slice(z=z, nx=300, ny=300)
            dxfwrite(lines, filename=f"{board.name}.{i:03d}.dxf", s=1/4*25.4/1000)

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

        os.system(f'magick.exe -delay 10 "{board.name}*.png" "{board.name}.gif"')


if __name__ == "__main__":
    demo()
