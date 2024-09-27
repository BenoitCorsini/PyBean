import sys
import unittest

sys.path.append('.')

from bean import Motion


class MotionTests(unittest.TestCase):

    MT = Motion()

    '''
    main method
    '''

    def test_main(self):
        self.MT.reset()
        self.MT.video()


if __name__ == '__main__':
    unittest.main(verbosity=2)