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

    def test_shade_shift(self):
        self.vl.shade_angle = 90
        shift = self.vl._shade_shift()
        self.assertEqual(shift[0], 1)
        self.assertEqual(round(shift[1], 10), 0)
        self.vl.shade_angle = 180
        shift = self.vl._shade_shift()
        self.assertEqual(round(shift[0], 10), 0)
        self.assertEqual(shift[1], 1)
        self.vl.shade_angle = -90
        shift = self.vl._shade_shift()
        self.assertEqual(shift[0], -1)
        self.assertEqual(round(shift[1], 10), 0)
        for angle in range(360):
            self.vl.shade_angle = angle
            shift = self.vl._shade_shift()
            self.assertEqual(round(np.sum(shift**2), 10), 1)

    def test_normalize_pos(self):
        with self.assertRaises(ValueError):
            self.vl._normalize_pos(0)
        with self.assertRaises(ValueError):
            self.vl._normalize_pos('test')
        with self.assertRaises(ValueError):
            self.vl._normalize_pos((0, 0, 0, 0))
        with self.assertRaises(ValueError):
            self.vl._normalize_pos([0]*4)
        for x in range(10):
            for y in range(10):
                self.assertEqual(
                    self.vl._normalize_pos((x, y)),
                    (x, y, 0)
                )
                self.assertEqual(
                    self.vl._normalize_pos([x, y]),
                    (x, y, 0)
                )
                self.assertEqual(
                    self.vl._normalize_pos(np.array([x, y])),
                    (x, y, 0)
                )
                for z in range(10):
                    self.assertEqual(
                        self.vl._normalize_pos((x, y, z)),
                        (x, y, z)
                    )
                    self.assertEqual(
                        self.vl._normalize_pos([x, y, z]),
                        (x, y, z)
                    )
                    self.assertEqual(
                        self.vl._normalize_pos(np.array([x, y, z])),
                        (x, y, z)
                    )

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
        with self.assertRaises(ValueError):
            self.vl._only_avoid_to_list(0)

    '''
    general methods
    '''

    def test_volume_list(self):
        self.vl._volumes = {
            'a1' : {'name' : 'a'},
            'a2' : {'name' : 'a'},
            'b1' : {'name' : 'b'},
            'b2' : {'name' : 'b'},
            'b3' : {'name' : 'b'},
        }
        self.assertEqual(
            self.vl.get_volume_list(),
            ['a1', 'a2', 'b1', 'b2', 'b3']
        )
        self.assertEqual(
            self.vl.get_volume_list(avoid=None),
            []
        )
        self.assertEqual(
            self.vl.get_volume_list(only='a'),
            ['a1', 'a2']
        )
        self.assertEqual(
            self.vl.get_volume_list(avoid='a'),
            ['b1', 'b2', 'b3']
        )
        self.assertEqual(
            self.vl.get_volume_list(only='a', avoid='a1'),
            ['a2']
        )
        self.assertEqual(
            self.vl.get_volume_list(only='a', avoid='b'),
            ['a1', 'a2']
        )
        self.assertEqual(
            self.vl.get_volume_list(only=['a1', 'b1'], avoid='a'),
            ['b1']
        )
        self.assertEqual(
            self.vl.get_volume_list(only=['a1', 'b1', 'b2'], avoid='b'),
            ['a1']
        )
        self.assertEqual(
            self.vl.get_volume_list(only=['a1', 'b1', 'b2'], avoid='b2'),
            ['a1', 'b1']
        )

    '''
    image methods
    '''

    # def test_sphere(self):
    #     self.vl.depth_shift = 0.05
    #     self.vl.depth_scale = 0.75
    #     self.vl.side_scale = 0.8
    #     num = 10
    #     self.vl.scale = 1/num
    #     self.vl.reset()
    #     for y in range(num + 1):
    #         for x in range(num + 1):
    #             if ((x + y) % 2) == 0:
    #                 self.vl._create_volume(
    #                     name='sphere',
    #                     pos=(x, y, (x + y)/num),
    #                     radius=0.4,
    #                     colour='forestgreen',
    #                 )
    #             else:
    #                 self.vl._create_volume(
    #                     name='sphere',
    #                     pos=(x, y, 0),
    #                     radius=0.2,
    #                     colour='royalblue',
    #                 )
    #     self.vl.update()
    #     self.vl.save('image_sphere')

    # def test_tubes(self):
    #     self.vl.reset()
    #     self.vl.depth_shift = 0.05
    #     self.vl.depth_scale = 0.75
    #     self.vl.side_scale = 0.8
    #     num = 10
    #     self.vl.scale = 1/num
    #     for y in range(num + 1):
    #         for x in range(num + 1):
    #             if ((x + y) % 2) == 0:
    #                 if x > y:
    #                     self.vl._create_volume(
    #                         name='tube',
    #                         shift1=(x, y),
    #                         shift2=(x, y, (x + y)/num),
    #                         radius=0.2,
    #                         colour='forestgreen',
    #                     )
    #                 else:
    #                     self.vl._create_volume(
    #                         name='tube',
    #                         shift1=(
    #                             x + 0.3*np.cos((x + y)*np.pi/num),
    #                             y + 0.3*np.sin((x + y)*np.pi/num),
    #                             (x + y)/num,
    #                         ),
    #                         shift2=(
    #                             x - 0.3*np.cos((x + y)*np.pi/num),
    #                             y - 0.3*np.sin((x + y)*np.pi/num),
    #                             (x + y)/num,
    #                         ),
    #                         radius=0.3,
    #                         colour='chocolate',
    #                     )
    #             else:
    #                 if x > y:
    #                     self.vl._create_volume(
    #                         name='tube',
    #                         shift1=(x, y),
    #                         shift2=(
    #                             x + 0.35*np.cos(np.pi*(x + y)/num),
    #                             y + 0.35*np.sin(np.pi*(x + y)/num),
    #                         ),
    #                         radius=(0.35, 0.05),
    #                         colour='purple',
    #                     )
    #                 else:
    #                     self.vl._create_volume(
    #                         name='tube',
    #                         shift1=(x, y),
    #                         shift2=(x, y),
    #                         radius=(0.2, 0.1),
    #                         colour='royalblue',
    #                     )
    #     self.vl.update()
    #     self.vl.save('image_tube')

    # def test_edge(self):
    #     self.vl.depth_shift = 0.05
    #     self.vl.depth_scale = 0.6
    #     self.vl.side_scale = 0.8
    #     num = 4
    #     self.vl.scale = 1/num
    #     self.vl.reset()
    #     for x in range(num + 1):
    #         for y in range(num + 1):
    #             self.vl.new_sphere(
    #                 f'{x}-{y}',
    #                 pos=(x, y, 0),
    #                 radius=0.1,
    #             )
    #     for x in range(num):
    #         for y in range(num + 1):
    #             collapse = True
    #             if x == 0 or x == 1:
    #                 space = 0.15 + 0.1*y
    #                 collapse = bool(x)
    #             elif x == 2:
    #                 space = (0.15, 0.5)
    #             elif x == 3:
    #                 space = (0.15, 0.15 - 0.05*y/num)
    #             else:
    #                 space = 0.15
    #             if x == 3:
    #                 radius = (0.05, 0.05 - 0.05*y/num)
    #             else:
    #                 radius = 0.05
    #             key1 = f'{x}-{y}'
    #             key2 = f'{x + 1}-{y}'
    #             self.vl.new_tube(
    #                 key1=key1,
    #                 key2=key2,
    #                 radius=radius,
    #                 space=space,
    #                 colour='gold',
    #                 collapse=collapse,
    #             )
    #     for x in range(num + 1):
    #         for y in range(num):
    #             collapse = True
    #             if x == 0 or x == 1:
    #                 space = -0.49 - 0.02*y
    #                 collapse = bool(x)
    #             elif x == 2:
    #                 space = 0
    #             else:
    #                 space = -0.15
    #             if x == 2:
    #                 shift1 = (y/(num - 1), y/(num - 1))
    #                 shift2 = (0, 0)
    #             elif x == 3:
    #                 shift1 = (0, 0, y/num)
    #                 shift2 = (0, 0, y/num)
    #             else:
    #                 shift1 = (0, 0)
    #                 shift2 = (0, 0)
    #             key1 = f'{x}-{y}'
    #             key2 = f'{x}-{y + 1}'
    #             self.vl.new_tube(
    #                 key1=key1,
    #                 key2=key2,
    #                 radius=0.05,
    #                 space=space,
    #                 shift1=shift1,
    #                 shift2=shift2,
    #                 colour='orange',
    #                 collapse=collapse,
    #                 alpha=0.5,
    #             )
    #     self.vl.update()
    #     self.vl.save('image_edge')

    def test_polyhedron(self):
        self.vl.depth_shift = 0.05
        self.vl.depth_scale = 0.75
        self.vl.side_scale = 0.8
        num = 10
        self.vl.scale = 1/num
        self.vl.reset()
        self.vl.update()
        self.vl.save('image_polyhedron')


if __name__ == '__main__':
    unittest.main(verbosity=2)