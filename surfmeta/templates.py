from scipy.constants import inch, foot


from . import Board

shorty = Board(
    width=19.5 * inch,
    height=2.5 * inch,
    length=6 * foot + 4 * inch,
    head_rocker=-1 / (20 * foot),
    tail_rocker=-1 / (37 * foot),
    side_rocker=1 / (4 * foot),
    squareness=2,
    eggness=-0.2,
    center_cut=2.5 * inch,
    tail_cut=4 * inch,
)

longboard = Board(
    height=2.75 * inch,
    width=22 * inch,
    length=8 * foot,
    wall_thickness=1 * inch,
    head_rocker=-1 / (50 * foot),
    tail_rocker=-1 / (200 * foot),
    side_rocker=1 / (5 * foot),
    squareness=3,
    eggness=0.1,
    center_cut=6 * inch,
    tail_cut=1 * inch,
)
