import numpy as np
from matplotlib.transforms import Affine2D

import bean


if __name__ == '__main__':
    B = bean.Volume(scale=0.25)
    scale = 0.9
    for x in [-1, 0, 1, 2]:
        B.new_cube(pos=(x - 0.5, 1.5), scale=scale, colour=B.hsl((4/4 + x)/4))
        B.new_pyramid(pos=(x - 0.5, 0.5), scale=scale, height=2, colour=B.hsl((5/4 + x)/4))
        B.new_polysphere(pos=(x - 0.5, -0.5), scale=scale, colour=B.hsl((6/4 + x)/4))
        B.new_pyramid(pos=(x - 0.5, -1.5), scale=scale, colour=B.hsl((7/4 + x)/4))
    B.update(colour=B.hsl())
    B.update('cube', colour=B.hsl(0))
    B.update('polysphere', scale=0.5)
    B.save()
