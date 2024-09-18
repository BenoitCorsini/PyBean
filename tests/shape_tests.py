import sys
import unittest

sys.path.append('.')

from bean import Shape


class ShapeTest(unittest.TestCase):

    def test_true(self):
        self.assertTrue(True)

    def test_equal(self):
        self.assertEqual(1 + 1, 2)

if __name__ == '__main__':
    unittest.main(verbosity=2)