import sys
import unittest
import numpy as np

sys.path.append('.')

from bean import Volume


class VolumeTests(unittest.TestCase):

    VL = Volume()

    '''
    main volumes
    '''

    def test_sphere(self):
        self.VL.reset()
        self.VL.depth_shift = 0.05
        self.VL.depth_scale = 0.75
        self.VL.side_scale = 0.8
        num = 10
        self.VL.scale = 1/num
        for y in range(num + 1):
            self.VL.new_volume(
                name='sphere',
                xy=(0.5, 0.5 + y),
                radius=0.4,
                colour='gold',
            )
            for x in range(num + 1):
                if ((x + y) % 2) == 0:
                    self.VL.new_volume(
                        name='sphere',
                        pos=(x, y, (x + y)/num),
                        radius=0.4,
                        colour='forestgreen',
                    )
                else:
                    self.VL.new_volume(
                        name='sphere',
                        pos=(x, y, 0),
                        radius=0.2,
                        colour='royalblue',
                    )
        self.VL.save('sphere')


if __name__ == '__main__':
    unittest.main(verbosity=2)