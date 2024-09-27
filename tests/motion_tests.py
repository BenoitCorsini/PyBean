import sys
import unittest

sys.path.append('.')

from bean import Motion


class MotionTests(unittest.TestCase):

    MT = Motion()

    '''
    general methods
    '''

    def test_time_nfs(self):
        for i in range(10):
            self.assertEqual(self.MT.time_to_nfs(i), i*self.MT.fps)
            self.assertEqual(self.MT.time_to_nfs(i + 1e-10), i*self.MT.fps + 1)
            self.assertEqual(self.MT.time_to_nfs(i/self.MT.fps), i)
            self.assertEqual(self.MT.time_to_nfs(i/self.MT.fps + 1e-10), i + 1)

    def test_key_nfs(self):
        self.MT.tests = {'empty' : 0, 'fps' : 1}
        self.MT.partials = {'two' : 2/self.MT.fps, 'small' : 1 + 1e-10}
        self.assertEqual(1, self.MT.key_to_nfs('empty'))
        self.assertEqual(0, self.MT.key_to_nfs('empty', 'tests'))
        self.assertEqual(1, self.MT.key_to_nfs('empty', 'partials'))
        self.assertEqual(1, self.MT.key_to_nfs('fps'))
        self.assertEqual(self.MT.fps, self.MT.key_to_nfs('fps', 'tests'))
        self.assertEqual(1, self.MT.key_to_nfs('fps', 'partials'))
        self.assertEqual(1, self.MT.key_to_nfs('two'))
        self.assertEqual(1, self.MT.key_to_nfs('two', 'tests'))
        self.assertEqual(2, self.MT.key_to_nfs('two', 'partials'))
        self.assertEqual(1, self.MT.key_to_nfs('small'))
        self.assertEqual(1, self.MT.key_to_nfs('small', 'tests'))
        self.assertEqual(self.MT.fps + 1, self.MT.key_to_nfs('small', 'partials'))

    '''
    main method
    '''

    def test_main(self):
        self.MT.reset()
        self.MT.wait()
        self.MT.video()


if __name__ == '__main__':
    unittest.main(verbosity=2)