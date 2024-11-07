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

    # def test_movement(self):
    #     # self.mt.draft = True
    #     # self.mt.levitation_mode = 'off'
    #     self.mt.reset().wait(0.1)
    #     self.mt.new_sphere(
    #         pos=(0.5, 0, 0),
    #         radius=0.1,
    #     ).grow(duration=0.5, centred=False).run().wait(0.1)
    #     self.mt.video()


if __name__ == '__main__':
    unittest.main(verbosity=2)