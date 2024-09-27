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

    # def test_sphere(self):
    #     self.VL.reset()
    #     self.VL.depth_shift = 0.05
    #     self.VL.depth_scale = 0.75
    #     self.VL.side_scale = 0.8
    #     num = 10
    #     self.VL.scale = 1/num
    #     for y in range(num + 1):
    #         self.VL.new_volume(
    #             name='sphere',
    #             xy=(0.5, 0.5 + y),
    #             radius=0.4,
    #             colour='gold',
    #         )
    #         for x in range(num + 1):
    #             if ((x + y) % 2) == 0:
    #                 self.VL.new_volume(
    #                     name='sphere',
    #                     pos=(x, y, (x + y)/num),
    #                     radius=0.4,
    #                     colour='forestgreen',
    #                 )
    #             else:
    #                 self.VL.new_volume(
    #                     name='sphere',
    #                     pos=(x, y, 0),
    #                     radius=0.2,
    #                     colour='royalblue',
    #                 )
    #     self.VL.save('sphere')

    def test_tubes(self):
        self.VL.reset()
        self.VL.depth_shift = 0.05
        self.VL.depth_scale = 0.75
        self.VL.side_scale = 0.8
        num = 10
        self.VL.scale = 1/num
        for y in range(num + 1):
            self.VL.new_volume(
                name='tube',
                xy1=(0.5, 0.5 + y),
                xy2=(0.5, 0.5 + y),
                radius1=0.4,
                radius2=0.2,
                colour='gold',
            )
            self.VL.new_volume(
                name='tube',
                xy1=(num - 0.5, 0.5 + y),
                xy2=(
                    num - 0.5 + 0.35*np.cos(2*np.pi*y/num),
                    0.5 + y + 0.35*np.sin(2*np.pi*y/num)
                ),
                radius1=0.35,
                radius2=0.05,
                colour='crimson',
            )
            for x in range(num + 1):
                if ((x + y) % 2) == 0:
                    if x > y:
                        self.VL.new_volume(
                            name='tube',
                            pos1=(x, y, 0),
                            pos2=(x, y, (x + y)/num),
                            radius1=0.2,
                            colour='forestgreen',
                        )
                    else:
                        self.VL.new_volume(
                            name='tube',
                            pos1=(
                                x + 0.3*np.cos((x + y)*np.pi/num),
                                y + 0.3*np.sin((x + y)*np.pi/num),
                                (x + y)/num,
                            ),
                            pos2=(
                                x - 0.3*np.cos((x + y)*np.pi/num),
                                y - 0.3*np.sin((x + y)*np.pi/num),
                                (x + y)/num,
                            ),
                            radius1=0.3,
                            colour='chocolate',
                        )
                else:
                    if x > y:
                        self.VL.new_volume(
                            name='tube',
                            pos1=(x, y, 0),
                            pos2=(
                                x + 0.35*np.cos(np.pi*(x + y)/num),
                                y + 0.35*np.sin(np.pi*(x + y)/num),
                                0,
                            ),
                            radius1=0.35,
                            radius2=0.05,
                            colour='purple',
                        )
                    else:
                        self.VL.new_volume(
                            name='tube',
                            pos1=(x, y, 0),
                            pos2=(x, y, 0),
                            radius1=0.2,
                            radius2=0.1,
                            colour='royalblue',
                        )
        self.VL.save('tube')


if __name__ == '__main__':
    unittest.main(verbosity=2)