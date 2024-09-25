import sys
import unittest
import numpy as np

sys.path.append('.')

from bean import Volume


class VolumeTests(unittest.TestCase):

    VL = Volume()

    '''
    main method
    '''

    def test_main(self):
        self.VL.reset()
        num = 20
        self.VL.scale = 1/num
        for y in range(num):
            self.VL.new_volume(
                name='sphere',
                xy=(0.5, 0.5 + y),
                radius=0.4,
                colour='royalblue',
            )
            self.VL.new_volume(
                name='sphere',
                pos=(num/2 + 0.5, 0.5 + y, 5),
                radius=0.4,
                colour='royalblue',
            )
            self.VL.new_volume(
                name='tube',
                xy1=(1.5, 0.5 + y),
                xy2=(1.5, 0.5 + y),
                radius1=0.3,
                radius2=0.2,
                colour='crimson',
            )
            self.VL.new_volume(
                name='tube',
                pos1=(num/2 + 1.5, 0.5 + y, 5),
                pos2=(num/2 + 1.5, 0.5 + y, 5),
                radius1=0.3,
                radius2=0.2,
                colour='crimson',
            )
            self.VL.new_volume(
                name='tube',
                xy1=(
                    2.5 + 0.3*np.cos(np.pi*y/10),
                    0.5 + y + 0.3*np.sin(np.pi*y/10),
                ),
                xy2=(
                    2.5 - 0.3*np.cos(np.pi*y/10),
                    0.5 + y - 0.3*np.sin(np.pi*y/10),
                ),
                radius1=0.1,
                colour='gold',
            )
            self.VL.new_volume(
                name='tube',
                pos1=(
                    num/2 + 2.5 + 0.3*np.cos(np.pi*y/10),
                    0.5 + y + 0.3*np.sin(np.pi*y/10),
                    5,
                ),
                pos2=(
                    num/2 + 2.5 - 0.3*np.cos(np.pi*y/10),
                    0.5 + y - 0.3*np.sin(np.pi*y/10),
                    5,
                ),
                radius1=0.1,
                colour='gold',
            )
            self.VL.new_volume(
                name='tube',
                xy1=(3.5, 0.5 + y),
                xy2=(
                    3.5 + 0.25*np.cos(np.pi*y/10),
                    0.5 + y + 0.25*np.sin(np.pi*y/10),
                ),
                radius1=0.2,
                radius2=0.05,
                colour='forestgreen',
            )
            self.VL.new_volume(
                name='tube',
                pos1=(num/2 + 3.5, 0.5 + y, 5),
                pos2=(
                    num/2 + 3.5 + 0.25*np.cos(np.pi*y/10),
                    0.5 + y + 0.25*np.sin(np.pi*y/10),
                    5,
                ),
                radius1=0.2,
                radius2=0.05,
                colour='forestgreen',
            )
        self.VL.save()


if __name__ == '__main__':
    unittest.main(verbosity=2)