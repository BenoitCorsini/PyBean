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

    def test_repeats(self):
        self.MT.draft = True
        self.MT.print_on = False
        self.MT.fps = 3
        self.MT.frames_dir = 'frames/repeats/'
        self.MT.reset()
        self.MT.show_info('Default repeats (1 frame)')
        self.MT._repeat_frames()
        self.MT.show_info(f'time overrules nfs ({self.MT.fps} frames)')
        self.MT._repeat_frames(nfs=1, time=1)
        self.MT._repeat_frames(nfs=2, key='key overrules nfs (1 frame)')
        self.MT._repeat_frames(time=1, key='key overrules time (1 frame)')
        self.MT._repeat_frames(nfs=2, time=1, key='key overrules both (1 frame)')

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
    general methods
    '''

    def test_wait(self):
        self.MT.draft = True
        self.MT.print_on = False
        self.MT.fps = 3
        self.MT.frames_dir = 'frames/wait/'
        self.MT.reset()
        self.MT.show_info('Default wait (1 frame)')
        self.MT.wait()
        self.MT.show_info('1 wait (1 frame)')
        self.MT.wait(1)
        self.MT.show_info('int(1.5) wait (1 frame)')
        self.MT.wait(int(1.5))
        self.MT.show_info(f'1. wait ({self.MT.fps} frames)')
        self.MT.wait(1.)
        self.MT.show_info(f'float(1) wait ({self.MT.fps} frames)')
        self.MT.wait(float(1))
        self.MT.show_info(f'key wait (1 frame)')
        self.MT.wait('actual key wait (1 frame)')
        self.MT.show_info(f'str(1) wait (1 frame)')
        self.MT.wait(str(1))
        self.MT.show_info(f'int overrules nfs (1 frames)')
        self.MT.wait(1, nfs=2)
        self.MT.show_info(f'time overrules int ({self.MT.fps} frames)')
        self.MT.wait(1, time=1)
        self.MT.wait(1, key='key overrules int (1 frame)')
        self.MT.show_info(f'float overrules time ({self.MT.fps} frames)')
        self.MT.wait(1., time=2)
        self.MT.wait(1., key='key overrules float (1 frame)')
        self.MT.wait('string overrules key (1 frame)', key='it does')


if __name__ == '__main__':
    unittest.main(verbosity=2)