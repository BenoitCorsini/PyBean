import sys
import unittest
import numpy as np
import cv2

sys.path.append('.')

from bean import Motion


class MotionTests(unittest.TestCase):

    mt = Motion()

    '''
    dunder methods
    '''

    def test_time_nfs(self):
        for i in range(10):
            self.assertEqual(self.mt._time_to_number_of_frames(i), i*self.mt.fps)
            self.assertEqual(self.mt._time_to_number_of_frames(i + 1e-10), i*self.mt.fps + 1)
            self.assertEqual(self.mt._time_to_number_of_frames(i/self.mt.fps), i)
            self.assertEqual(self.mt._time_to_number_of_frames(i/self.mt.fps + 1e-10), i + 1)

    def test_key_nfs(self):
        self.mt.tests = {'empty' : 0, 'fps' : 1}
        self.mt.partials = {'two' : 2/self.mt.fps, 'small' : 1 + 1e-10}
        self.assertEqual(1, self.mt._key_to_number_of_frames('empty'))
        self.assertEqual(0, self.mt._key_to_number_of_frames('empty', 'tests'))
        self.assertEqual(1, self.mt._key_to_number_of_frames('empty', 'partials'))
        self.assertEqual(1, self.mt._key_to_number_of_frames('fps'))
        self.assertEqual(self.mt.fps, self.mt._key_to_number_of_frames('fps', 'tests'))
        self.assertEqual(1, self.mt._key_to_number_of_frames('fps', 'partials'))
        self.assertEqual(1, self.mt._key_to_number_of_frames('two'))
        self.assertEqual(1, self.mt._key_to_number_of_frames('two', 'tests'))
        self.assertEqual(2, self.mt._key_to_number_of_frames('two', 'partials'))
        self.assertEqual(1, self.mt._key_to_number_of_frames('small'))
        self.assertEqual(1, self.mt._key_to_number_of_frames('small', 'tests'))
        self.assertEqual(self.mt.fps + 1, self.mt._key_to_number_of_frames('small', 'partials'))

    def test_nfs_params(self):
        self.assertEqual(1, self.mt._params_to_number_of_frames())
        self.assertEqual(self.mt.fps, self.mt._params_to_number_of_frames(nfs=1, time=1))
        self.assertEqual(1, self.mt._params_to_number_of_frames(nfs=2, key=''))
        self.assertEqual(1, self.mt._params_to_number_of_frames(time=1, key=''))
        self.assertEqual(1, self.mt._params_to_number_of_frames(nfs=2, time=1, key=''))

    def test_get_nfs(self):
        self.assertEqual(1, self.mt._get_number_of_frames())
        self.assertEqual(1, self.mt._get_number_of_frames(1))
        self.assertEqual(1, self.mt._get_number_of_frames(int(1.5)))
        self.assertEqual(self.mt.fps, self.mt._get_number_of_frames(1.))
        self.assertEqual(self.mt.fps, self.mt._get_number_of_frames(float(1)))
        self.assertEqual(1, self.mt._get_number_of_frames(''))
        self.assertEqual(1, self.mt._get_number_of_frames(str(1)))
        self.assertEqual(1, self.mt._get_number_of_frames(1, nfs=2))
        self.assertEqual(self.mt.fps, self.mt._get_number_of_frames(1, time=1))
        self.assertEqual(1, self.mt._get_number_of_frames(1, key=''))
        self.assertEqual(self.mt.fps, self.mt._get_number_of_frames(1., time=2))
        self.assertEqual(1, self.mt._get_number_of_frames(1., key=''))
        self.mt.times = {'test': 1}
        self.assertEqual(self.mt.fps, self.mt._get_number_of_frames('test', key=''))
        self.assertEqual(self.mt.fps, self.mt._get_number_of_frames('test'))
        self.assertEqual(self.mt.fps, self.mt._get_number_of_frames('test', key='test'))
        self.assertEqual(1, self.mt._get_number_of_frames('', key='test'))
        self.assertEqual(self.mt.fps, self.mt._get_number_of_frames(key='test'))

    '''
    static methods
    '''

    def test_path_to_norm(self):
        with self.assertRaises(AssertionError):
            self.mt._path_to_norm(np.array([0, 1]))
        with self.assertRaises(AssertionError):
            self.mt._path_to_norm(np.array([[[0, 1]]]))
        path = np.array([[0]])
        self.assertTrue(np.all(
            self.mt._path_to_norm(path) == np.array([0])
        ))
        path = np.array([[0, 1]])
        self.assertTrue(np.all(
            self.mt._path_to_norm(path) == np.array([0])
        ))
        path = np.array([[0, 1, 2]])
        self.assertTrue(np.all(
            self.mt._path_to_norm(path) == np.array([0])
        ))
        path = np.array([[0], [1]])
        self.assertTrue(np.all(
            self.mt._path_to_norm(path) == np.array([0, 1])
        ))
        path = np.array([[0], [1], [3]])
        self.assertTrue(np.all(
            self.mt._path_to_norm(path) == np.array([0, 1/3, 1])
        ))
        path = np.array([[0], [2], [4]])
        self.assertTrue(np.all(
            self.mt._path_to_norm(path) == np.array([0, 1/2, 1])
        ))
        path = np.array([[0, 0], [2, 0], [4, 0]])
        self.assertTrue(np.all(
            self.mt._path_to_norm(path) == np.array([0, 1/2, 1])
        ))
        path = np.array([[0, 0], [0, 1], [0, 2]])
        self.assertTrue(np.all(
            self.mt._path_to_norm(path) == np.array([0, 1/2, 1])
        ))
        path = np.array([[0, 0, 1], [0, 1, 1], [0, 2, 1]])
        self.assertTrue(np.all(
            self.mt._path_to_norm(path) == np.array([0, 1/2, 1])
        ))
        path = np.array([[0, 9, 0], [0, 9, 1], [0, 9, 2]])
        self.assertTrue(np.all(
            self.mt._path_to_norm(path) == np.array([0, 1/2, 1])
        ))
        path = np.array([[1, 2, 3], [2, 3, 4], [4, 5, 6], [5, 6, 7]])
        self.assertTrue(np.all(
            np.round(self.mt._path_to_norm(path), 10) == np.array([0, 1/4, 3/4, 1])
        ))
        path = np.array([[1, 2, 3], [2, 3, 4], [2, 3, 4], [4, 5, 6], [4, 5, 6], [5, 6, 7]])
        self.assertTrue(np.all(
            np.round(self.mt._path_to_norm(path), 10) == np.array([0, 1/4, 1/4, 3/4, 3/4, 1])
        ))

    def test_normed_path_to_pos(self):
        with self.assertRaises(AssertionError):
            self.mt._normed_path_to_pos(None, None, np.array([0, 0.5]))
        with self.assertRaises(AssertionError):
            self.mt._normed_path_to_pos(None, None, np.array([0.5, 1]))
        with self.assertRaises(AssertionError):
            self.mt._normed_path_to_pos(None, None, np.array([0.5]))
        path = np.array([[1, 2, 3], [2, 3, 4], [4, 5, 6], [5, 6, 7]])
        norm = np.round(self.mt._path_to_norm(path), 10)
        for i in range(17):
            self.assertEqual(
                self.mt._normed_path_to_pos(i/16, path, np.array([0])),
                (1, 2, 3),
            )
            self.assertEqual(
                self.mt._normed_path_to_pos(i/16, path, norm),
                (1 + i/4, 2 + i/4, 3 + i/4),
            )
        path = np.array([[1, 1, 1], [1, 1, 1], [2.5, 2.5, 2.5], [5, 5, 5]])
        norm = np.round(self.mt._path_to_norm(path), 10)
        for i in range(17):
            self.assertEqual(
                self.mt._normed_path_to_pos(i/16, path, np.array([0])),
                (1, 1, 1),
            )
            self.assertEqual(
                self.mt._normed_path_to_pos(i/16, path, norm),
                (1 + i/4, 1 + i/4, 1 + i/4),
            )

    '''
    video methods
    '''

    def test_appear_disappear(self):
        self.mt.draft = True
        self.mt.levitation_mode = 'off'
        self.mt.reset()
        self.mt.show_info('waiting')
        self.mt.wait(0.1)
        self.mt.show_info('blue grows')
        self.mt.new_sphere(
            'blue',
            pos=(0.2, 0.1, 0),
            radius=0.2,
            colour='royalblue',
        ).grow('blue', duration=0.5, centred=False, early_stop=0.1).run()
        self.mt.show_info('pause')
        self.mt.wait(0.1)
        self.mt.show_info('blue and shaded yellow grow, then yellow grows/appears')
        self.mt.new_sphere(
            'yellow',
            pos=(0.6, 0.3, 0),
            radius=0.2,
            colour='gold',
            alpha=0.1,
        ).grow('yellow', duration=0.5).change_alpha('yellow', start_with=1, end_with=-1, duration=0.1, delay=0.4).run()
        self.mt.show_info('pause')
        self.mt.wait(0.1)
        self.mt.show_info('green grows and appears slowly')
        self.mt.new_sphere(
            'green',
            pos=(0.85, 0.15, 0),
            radius=0.2,
            colour='forestgreen',
            alpha=0.5,
        ).appear('green', duration=1.).grow('green', duration=0.5, centred=False).run()
        self.mt.show_info('pause')
        self.mt.wait(0.1)
        self.mt.show_info('all schrink')
        self.mt.change_radius(
            start_with=1,
            end_with=0.5,
            duration=0.1,
        ).run()
        self.mt.show_info('delay, then all grow, stop, grow, stop, grow')
        self.mt.change_radius(
            start_with=1,
            end_with=2,
            duration=0.5,
            delay=0.1,
            early_stop=[0.1, 0.2],
        ).run().wait(0.1).run().wait(0.1).run()
        self.mt.show_info('red appears')
        self.mt.new_sphere(
            'red',
            pos=(0.3, 0.5, 0.1),
            radius=0.1,
            colour='crimson',
        ).grow('red', duration=0.5).run()
        self.mt.show_info('pause')
        self.mt.wait(0.1)
        self.mt.show_info('green disappears')
        self.mt.disappear('green', duration=0.5).run()
        self.mt.show_info('green appears')
        self.mt.appear('green', use_current_alpha=False, duration=0.5).run()
        self.mt.show_info('all but blue schrink')
        self.mt.schrink(avoid='blue', duration=0.5).run()
        self.mt.show_info('pause')
        self.mt.wait(0.1)
        self.mt.update(alpha=1)
        self.mt.show_info('all but blue grow')
        self.mt.change_radius(start_with=1, end_with=-0.2, duration=0.5).run()
        self.mt.show_info('all schrink and disappear')
        self.mt.schrink(duration=0.5).disappear(duration=0.5).run()
        self.mt.show_info('end')
        self.mt.wait(0.1)
        self.mt.video('video_appear')

    def test_movement(self):
        self.mt.draft = False
        self.mt.levitation_mode = 'off'
        self.mt.depth_shift = 0.1
        self.mt.depth_scale = 0.5
        self.mt.side_scale = 0.8
        self.mt.scale = 0.5
        self.mt.reset().wait(1)
        self.mt.show_info('step1')
        self.mt.new_sphere(
            pos=(0.5, 0.5),
            radius=0.1,
            alpha=0.1,
        )
        self.mt.new_sphere(
            pos=(0.5, 0),
            radius=0.1,
            alpha=0.1,
        )
        self.mt.new_sphere(
            'main',
            pos=(0.5, 0),
            radius=0.1,
        ).grow(duration=0.1, centred=False).run()
        self.mt.show_info('step2')
        self.mt.move_to(
            (0.5, 0.5),
            'main',
            duration=0.5,
        ).run().wait(0.1)
        self.mt.show_info('step3')
        self.mt.movement(
            [(0.5, 0.5), (0.5, 0.5, 1)] + [(0.5, 0.5)]*9,
            'main',
            duration=2.,
            normalize=False,
        ).run().wait(0.1)
        self.mt.show_info('step4')
        self.mt.jump(
            1,
            'main',
            duration=0.2,
        ).run().wait(0.1)
        self.mt.show_info('step5')
        self.mt.shift(
            (0.5, 0),
            avoid='main',
            duration=0.5,
            rigid=True,
        )
        self.mt.movement(
            [(0, 0.5), (0.5, 0.5, 1), (1, 0), (0.5, 0, 0.5), (0.5, 0)],
            'main',
            duration=0.5,
            normalize=False,
            initial_speed=(-10, 0, 0),
        ).run().wait(0.1)
        self.mt.video('video_movements')

    def test_tubes(self):
        self.mt.draft = False
        self.mt.levitation_mode = 'off'
        self.mt.depth_shift = 0.1
        self.mt.depth_scale = 0.5
        self.mt.side_scale = 0.8
        num = 4
        self.mt.scale = 1/num
        self.mt.reset()
        self.mt.wait(1)
        for y in range(num + 1):
            for x in range(num + 1):
                self.mt.new_sphere(
                    f'{x}-{y}',
                    pos=(x, y),
                    radius=0.2,
                    alpha=0,
                )
                if y:
                    self.mt.new_tube(
                        f'{x}--{y}-{y}',
                        key1=f'{x}-{y-1}',
                        key2=f'{x}-{y}',
                        radius=0.1,
                        space=0.35,
                        colour='skyblue',
                        alpha=0,
                    ) 
        for y in range(num + 1):
            for x in range(num + 1):
                s = f'{x}-{y}'
                delay = (x + num*y/2)/num**2
                self.mt.appear(s, duration=0.5, delay=delay, use_current_alpha=False)
                self.mt.grow(s, duration=0.5, delay=delay)
                self.mt.jump(2, s, duration=0.5, delay=delay, end_height=1)
                if y:
                    self.mt.appear(f'{x}--{y}-{y}', duration=0.5, delay=delay, use_current_alpha=False)
                    self.mt.grow(f'{x}--{y}-{y}', duration=0.5, delay=delay)
        self.mt.run()
        for y in range(num + 1):
            for x in range(1, num + 1):
                if y > 1:
                    self.mt.new_tube(
                        f'{x}-{x}--{y}',
                        key1=f'{x-1}-{y}',
                        key2=f'{x}-{y}',
                        radius=(0.1, 0.05),
                        space=0.35,
                        colour='skyblue',
                    )
                else:
                    self.mt.new_tube(
                        f'{x}-{x}--{y}',
                        key1=f'{x-1}-{y}',
                        key2=f'{x}-{y}',
                        radius=0.1,
                        space=0.35,
                        colour='skyblue',
                    ) 
        for y in range(num + 1):
            for x in range(1, num + 1):
                self.mt.appear(f'{x}-{x}--{y}', duration=0.25)
                if y == 0:
                    self.mt.grow(f'{x}-{x}--{y}', duration=1.)
                elif y == 1:
                    self.mt.change_radius(f'{x}-{x}--{y}', duration=1., start_with=0, end_with=(1, 0.5))
                elif y == 2:
                    self.mt.change_radius(f'{x}-{x}--{y}', duration=1., start_with=-0.2, end_with=(1, 2))
                elif y == 3:
                    self.mt.change_radius(f'{x}-{x}--{y}', duration=1., start_with=(1, 0), end_with=(1, 2))
                else:
                    self.mt.change_radius(f'{x}-{x}--{y}', duration=1., start_with=-0.5, end_with=(-0.1, 2))
        self.mt.run().wait(0.1)
        for x in range(1, num + 1):
            self.mt.change_radius(f'{x}-{x}--1', duration=0.5, start_with=1, end_with=-0.1)
        self.mt.run().wait(0.1)
        for y in range(num + 1):
            for x in range(num + 1):
                s = f'{x}-{y}'
                delay = (x + num*y/2)/num**2
                self.mt.jump(1, s, duration=0.5, delay=delay, end_height=-2, position_threshold=100, speed_threshold=100, damping=0)
        self.mt.run()
        for y in range(num + 1):
            for x in range(num + 1):
                s = f'{x}-{y}'
                delay = (x + num*y/2)/num**2
                self.mt.schrink(s, duration=0.5, delay=delay, centred=False)
                if x:
                    self.mt.schrink(f'{x}-{x}--{y}', duration=0.5, delay=delay)
                if y:
                    self.mt.schrink(f'{x}--{y}-{y}', duration=0.5, delay=delay)
        self.mt.run()
        self.mt.video('video_edges')



if __name__ == '__main__':
    unittest.main(verbosity=2)