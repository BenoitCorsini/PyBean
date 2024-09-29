import sys
import unittest
import numpy as np

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
    main method
    '''

    def test_main(self):
        # self.mt.draft = True
        # self.mt.levitation_mode = 'off'
        self.mt.scale = 0.5
        self.mt.reset()
        self.mt.wait(0.1)
        self.mt.new_sphere(
            'blue sphere',
            pos=(0.2, 0.1, 0),
            radius=0.2,
            colour='royalblue',
        )
        self.mt.wait(1.)
        self.mt.new_sphere(
            'yellow sphere',
            pos=(0.6, 0.3, 0),
            radius=0.2,
            colour='gold',
        )
        self.mt.wait(1.)
        self.mt.new_sphere(
            'green sphere',
            pos=(0.85, 0.15, 0),
            radius=0.2,
            colour='forestgreen',
        )
        self.mt.appear('green sphere', duration=1.)
        self.mt.run()
        self.mt.wait(1.)
        self.mt.new_sphere(
            'red sphere',
            pos=(0.3, 0.5, 0.1),
            radius=0.1,
            colour='crimson',
        )
        self.mt.appear('red sphere', duration=0.2)
        self.mt.run()
        self.mt.wait(7.)
        self.mt.disappear(avoid='blue sphere', duration=1.)
        self.mt.run()
        self.mt.wait(1.)
        self.mt.disappear(duration=0.2)
        self.mt.run()
        self.mt.wait(0.5)
        self.mt.video()


if __name__ == '__main__':
    unittest.main(verbosity=2)