# generates 3D and 2D board formats

import pyvista as pv
from surfmeta import Board, dxfwrite
import numpy as np
import matplotlib.pyplot as plt

board = Board(
    name='./data/board',
    # rotation=(180, 90, 0),
    # position=(36, -1.5, 0)
)
board.show(filename='./data/board.stl', sy=3.5, nz=500, nx=200, ny=200)

mesh = pv.read('./data/shorty.stl')
mesh = mesh.rotate_x(180)
mesh = mesh.rotate_y(-90)
# it's a 6'4' board chopped down to 6'
mesh = mesh.translate([0, -1.25, -76/2+4])

print(mesh)
# mesh.
board.plotter.add_mesh(mesh, opacity=0.5)
# board.slice(x=0)
# board.slice(y=0)
# board.slice(z=0)
board.plotter.camera_position = 'zx'
board.plotter.show()
# plt.show()

# make slices
z = np.arange(-board.lz/2, board.lz/2, 1/4)
for i in range(len(z)):
    lines = board.slice(z=z[i], nx=300, ny=300, sy=3, show=False)
    dxfwrite(lines, filename=f"./data/dxf/xy-{i:03d}.dxf", s=25.4)
#     # cmd = f"magick -delay 5 ./png/*.png xy.gif"
#     # os.system(cmd)
