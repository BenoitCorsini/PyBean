import sys
import unittest
import numpy as np

sys.path.append('.')

from bean import Volume


class VolumeTests(unittest.TestCase):

    vl = Volume()

    '''
    hidden methods
    '''

    def test_only_avoid(self):
        self.vl._volumes = {
            'a1' : {'name' : 'a'},
            'a2' : {'name' : 'a'},
            'b1' : {'name' : 'b'},
            'b2' : {'name' : 'b'},
            'b3' : {'name' : 'b'},
        }
        self.assertEqual(
            self.vl._only_avoid_to_list(),
            ['a1', 'a2', 'b1', 'b2', 'b3']
        )
        self.assertEqual(
            self.vl._only_avoid_to_list('a1'),
            ['a1']
        )
        self.assertEqual(
            self.vl._only_avoid_to_list(['a1']),
            ['a1']
        )
        self.assertEqual(
            self.vl._only_avoid_to_list(['a1', 'a3']),
            ['a1']
        )
        self.assertEqual(
            self.vl._only_avoid_to_list(['a']),
            []
        )
        self.assertEqual(
            self.vl._only_avoid_to_list(['a1', 'b1']),
            ['a1', 'b1']
        )
        self.assertEqual(
            self.vl._only_avoid_to_list([]),
            []
        )
        self.assertEqual(
            self.vl._only_avoid_to_list('a'),
            ['a1', 'a2']
        )
        self.assertEqual(
            self.vl._only_avoid_to_list('b'),
            ['b1', 'b2', 'b3']
        )
        self.assertEqual(
            self.vl._only_avoid_to_list('c'),
            []
        )

    def test_volume_list(self):
        self.vl._volumes = {
            'a1' : {'name' : 'a'},
            'a2' : {'name' : 'a'},
            'b1' : {'name' : 'b'},
            'b2' : {'name' : 'b'},
            'b3' : {'name' : 'b'},
        }
        self.assertEqual(
            self.vl._get_volume_list(),
            ['a1', 'a2', 'b1', 'b2', 'b3']
        )
        self.assertEqual(
            self.vl._get_volume_list(avoid=None),
            []
        )
        self.assertEqual(
            self.vl._get_volume_list(only='a'),
            ['a1', 'a2']
        )
        self.assertEqual(
            self.vl._get_volume_list(avoid='a'),
            ['b1', 'b2', 'b3']
        )
        self.assertEqual(
            self.vl._get_volume_list(only='a', avoid='a1'),
            ['a2']
        )
        self.assertEqual(
            self.vl._get_volume_list(only='a', avoid='b'),
            ['a1', 'a2']
        )
        self.assertEqual(
            self.vl._get_volume_list(only=['a1', 'b1'], avoid='a'),
            ['b1']
        )
        self.assertEqual(
            self.vl._get_volume_list(only=['a1', 'b1', 'b2'], avoid='b'),
            ['a1']
        )
        self.assertEqual(
            self.vl._get_volume_list(only=['a1', 'b1', 'b2'], avoid='b2'),
            ['a1', 'b1']
        )

    '''
    image methods
    '''

    def test_sphere(self):
        self.vl.reset()
        self.vl.depth_shift = 0.05
        self.vl.depth_scale = 0.75
        self.vl.side_scale = 0.8
        num = 10
        self.vl.scale = 1/num
        for y in range(num + 1):
            self.vl._create_volume(
                name='sphere',
                xy=(0.5, 0.5 + y),
                radius=0.4,
                colour='gold',
            )
            for x in range(num + 1):
                if ((x + y) % 2) == 0:
                    self.vl._create_volume(
                        name='sphere',
                        pos=(x, y, (x + y)/num),
                        radius=0.4,
                        colour='forestgreen',
                    )
                else:
                    self.vl._create_volume(
                        name='sphere',
                        pos=(x, y, 0),
                        radius=0.2,
                        colour='royalblue',
                    )
        self.vl.update()
        self.vl.save('image_sphere')

    def test_tubes(self):
        self.vl.reset()
        self.vl.depth_shift = 0.05
        self.vl.depth_scale = 0.75
        self.vl.side_scale = 0.8
        num = 10
        self.vl.scale = 1/num
        for y in range(num + 1):
            self.vl._create_volume(
                name='tube',
                xy1=(0.5, 0.5 + y),
                xy2=(0.5, 0.5 + y),
                radius1=0.4,
                radius2=0.2,
                colour='gold',
            )
            self.vl._create_volume(
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
                        self.vl._create_volume(
                            name='tube',
                            pos1=(x, y, 0),
                            pos2=(x, y, (x + y)/num),
                            radius1=0.2,
                            colour='forestgreen',
                        )
                    else:
                        self.vl._create_volume(
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
                        self.vl._create_volume(
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
                        self.vl._create_volume(
                            name='tube',
                            pos1=(x, y, 0),
                            pos2=(x, y, 0),
                            radius1=0.2,
                            radius2=0.1,
                            colour='royalblue',
                        )
        self.vl.update()
        self.vl.save('image_tube')


if __name__ == '__main__':
    unittest.main(verbosity=2)