import numpy as np
from matplotlib.transforms import Affine2D

import bean


if __name__ == '__main__':
    # B = bean.Volume(scale=0.25)
    # scale = 0.9
    # for x in [-1, 0, 1, 2]:
    #     B.new_cube(pos=(x - 0.5, 1.5), scale=scale, colour=B.hsl((4/4 + x)/4))
    #     B.new_pyramid(pos=(x - 0.5, 0.5), scale=scale, height=2, colour=B.hsl((5/4 + x)/4))
    #     B.new_polysphere(pos=(x - 0.5, -0.5), scale=scale, colour=B.hsl((6/4 + x)/4))
    #     B.new_pyramid(pos=(x - 0.5, -1.5), scale=scale, colour=B.hsl((7/4 + x)/4))
    # B.update('cube', colour=B.hsl(0))
    # B.update('polysphere', scale=0.7, colour=B.hsl(0.7))
    # B.save()
    B = bean.Sculpt(view_scale=0.5, draft=0)
    scale = 0.9
    opacity = 1
    orientation = None
    B.cube(pos=(+0.5, +0.5), scale=scale, colour='forestgreen', opacity=opacity, orientation=orientation)
    B.sphere(pos=(-0.5, +0.5), scale=scale, colour='royalblue', opacity=opacity)
    B.sphere(pos=(+0.5, -0.5), scale=scale, colour='crimson', opacity=opacity, overground=False)
    B.sphere(pos=(-0.5, -0.5, 2), scale=scale, colour='gold', opacity=opacity)
    B.mold()
    B.save()
