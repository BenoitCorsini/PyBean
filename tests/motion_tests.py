import sys
import unittest
import numpy as np

sys.path.append('.')

from bean import Motion


class MotionTests(unittest.TestCase):

    MT = Motion()

    '''
    dunder methods
    '''

    def test_time_nfs(self):
        for i in range(10):
            self.assertEqual(self.MT._time_to_number_of_frames(i), i*self.MT.fps)
            self.assertEqual(self.MT._time_to_number_of_frames(i + 1e-10), i*self.MT.fps + 1)
            self.assertEqual(self.MT._time_to_number_of_frames(i/self.MT.fps), i)
            self.assertEqual(self.MT._time_to_number_of_frames(i/self.MT.fps + 1e-10), i + 1)

    def test_key_nfs(self):
        self.MT.tests = {'empty' : 0, 'fps' : 1}
        self.MT.partials = {'two' : 2/self.MT.fps, 'small' : 1 + 1e-10}
        self.assertEqual(1, self.MT._key_to_number_of_frames('empty'))
        self.assertEqual(0, self.MT._key_to_number_of_frames('empty', 'tests'))
        self.assertEqual(1, self.MT._key_to_number_of_frames('empty', 'partials'))
        self.assertEqual(1, self.MT._key_to_number_of_frames('fps'))
        self.assertEqual(self.MT.fps, self.MT._key_to_number_of_frames('fps', 'tests'))
        self.assertEqual(1, self.MT._key_to_number_of_frames('fps', 'partials'))
        self.assertEqual(1, self.MT._key_to_number_of_frames('two'))
        self.assertEqual(1, self.MT._key_to_number_of_frames('two', 'tests'))
        self.assertEqual(2, self.MT._key_to_number_of_frames('two', 'partials'))
        self.assertEqual(1, self.MT._key_to_number_of_frames('small'))
        self.assertEqual(1, self.MT._key_to_number_of_frames('small', 'tests'))
        self.assertEqual(self.MT.fps + 1, self.MT._key_to_number_of_frames('small', 'partials'))

    def test_nfs_params(self):
        self.assertEqual(1, self.MT._params_to_number_of_frames())
        self.assertEqual(self.MT.fps, self.MT._params_to_number_of_frames(nfs=1, time=1))
        self.assertEqual(1, self.MT._params_to_number_of_frames(nfs=2, key=''))
        self.assertEqual(1, self.MT._params_to_number_of_frames(time=1, key=''))
        self.assertEqual(1, self.MT._params_to_number_of_frames(nfs=2, time=1, key=''))

    def test_get_nfs(self):
        self.assertEqual(1, self.MT._get_number_of_frames())
        self.assertEqual(1, self.MT._get_number_of_frames(1))
        self.assertEqual(1, self.MT._get_number_of_frames(int(1.5)))
        self.assertEqual(self.MT.fps, self.MT._get_number_of_frames(1.))
        self.assertEqual(self.MT.fps, self.MT._get_number_of_frames(float(1)))
        self.assertEqual(1, self.MT._get_number_of_frames(''))
        self.assertEqual(1, self.MT._get_number_of_frames(str(1)))
        self.assertEqual(1, self.MT._get_number_of_frames(1, nfs=2))
        self.assertEqual(self.MT.fps, self.MT._get_number_of_frames(1, time=1))
        self.assertEqual(1, self.MT._get_number_of_frames(1, key=''))
        self.assertEqual(self.MT.fps, self.MT._get_number_of_frames(1., time=2))
        self.assertEqual(1, self.MT._get_number_of_frames(1., key=''))
        self.MT.times = {'test': 1}
        self.assertEqual(self.MT.fps, self.MT._get_number_of_frames('test', key=''))
        self.assertEqual(self.MT.fps, self.MT._get_number_of_frames('test'))
        self.assertEqual(self.MT.fps, self.MT._get_number_of_frames('test', key='test'))
        self.assertEqual(1, self.MT._get_number_of_frames('', key='test'))
        self.assertEqual(self.MT.fps, self.MT._get_number_of_frames(key='test'))


if __name__ == '__main__':
    unittest.main(verbosity=2)