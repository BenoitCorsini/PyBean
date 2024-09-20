import sys
import unittest
import numpy as np
import numpy.random as npr

sys.path.append('.')

from bean import Canvas


class CanvasTests(unittest.TestCase):

    CV = Canvas()

    '''
    dunder methods
    '''

    def test_string(self):
        self.assertTrue('Canvas' in str(self.CV))

    '''
    hidden methods
    '''

    def test_classes(self):
        classes = self.CV._get_classes()
        self.assertEqual(len(classes), 2)
        self.assertEqual(classes[0].__name__, 'object')
        self.assertEqual(classes[1].__name__, 'Canvas')

    def test_new_methods(self):
        methods = self.CV._get_new_methods()
        self.assertEqual(len(methods), 1)
        self.assertEqual(methods[0], '_new_canvas')

    '''
    static methods
    '''

    def test_cmap(self):
        n_colours = 2
        colour_list = npr.rand(n_colours, 4)
        cmap = self.CV.get_cmap(colour_list)
        for index, colour in enumerate(colour_list):
            self.assertTrue(np.all(
                colour == cmap(index/(n_colours - 1))
            ))

    def test_greyscale(self):
        self.assertEqual(
            self.CV.get_greyscale(True),
            self.CV.get_cmap(['white', 'black'])
        )
        self.assertEqual(
            self.CV.get_greyscale(False),
            self.CV.get_cmap(['black', 'white'])
        )

    def test_cscale(self):
        colour = npr.rand(3)
        self.assertEqual(
            self.CV.get_cscale(colour),
            self.CV.get_cmap(['white', colour, 'black'])
        )
        colour = npr.rand(3)
        self.assertEqual(
            self.CV.get_cscale(colour, start_with='same'),
            self.CV.get_cmap([colour, 'black'])
        )
        colour = npr.rand(3)
        self.assertEqual(
            self.CV.get_cscale(colour, end_with='same'),
            self.CV.get_cmap(['white', colour])
        )
        colour = npr.rand(3)
        start = npr.rand(3)
        end = npr.rand(3)
        self.assertEqual(
            self.CV.get_cscale(colour, start_with=start, end_with=end),
            self.CV.get_cmap([start, colour, end])
        )
        colour = npr.rand(3)
        self.assertEqual(
            self.CV.get_cscale(colour, start_with='same', end_with='same'),
            self.CV.get_cmap([colour]*2)
        )

    def test_time_string(self):
        self.assertEqual(self.CV.time_to_string(0), '0s')
        self.assertEqual(self.CV.time_to_string(59), '59s')
        self.assertEqual(self.CV.time_to_string(60), '1m0s')
        self.assertEqual(self.CV.time_to_string(3599), '59m59s')
        self.assertEqual(self.CV.time_to_string(3600), '1h0m0s')
        self.assertEqual(self.CV.time_to_string(3723), '1h2m3s')

    def test_angle_shift(self):
        angles = [0, 45, 90, 180, 225, 360, 720]
        arrays = [
            np.array([1, 0]),
            np.array([1, 1])*np.sqrt(2)/2,
            np.array([0, 1]),
            np.array([-1, 0]),
            np.array([-1, -1])*np.sqrt(2)/2,
            np.array([1, 0]),
            np.array([1, 0]),
        ]
        for angle, array in zip(angles, arrays):
            one_dim = self.CV.angle_shift(angle)
            two_dim = self.CV.angle_shift(angle, two_dim=True)
            self.assertTrue(np.all(np.abs(one_dim - array) < 1e-10))
            self.assertTrue(np.all(np.abs(two_dim - array) < 1e-10))
            self.assertEqual(one_dim.shape, (2, ))
            self.assertEqual(two_dim.shape, (1, 2))

    def test_xy_angle(self):
        for mult in [0, 1, 2, 10]:
            for shift in [(0, 0), (1, 1), (1/3, -5**0.5)]:
                self.assertEqual(
                    round(self.CV.angle_from_xy(
                        (shift[0], shift[1]),
                        (shift[0] + mult, shift[1]),
                    ), 10),
                    0
                )
                self.assertEqual(
                    round(self.CV.angle_from_xy(
                        (shift[0], shift[1]),
                        (shift[0] + mult, shift[1] + mult),
                    ), 10),
                    45*(mult > 0)
                )
                self.assertEqual(
                    round(self.CV.angle_from_xy(
                        (shift[0], shift[1]),
                        (shift[0] - mult, shift[1]),
                    ), 10),
                    180*(mult > 0)
                )
                self.assertEqual(
                    round(self.CV.angle_from_xy(
                        (shift[0], shift[1]),
                        (shift[0] - mult*3**0.5/2, shift[1] - mult/2),
                    ), 10),
                    -150*(mult > 0)
                )

    def text_xy_distance(self):
        for mult in [0, 1, 2, 10]:
            for shift in [(0, 0), (1, 1), (1/3, -5**0.5)]:
                self.assertEqual(
                    round(self.CV.distance_from_xy(
                        (shift[0], shift[1]),
                        (shift[0] + mult, shift[1]),
                    ), 10),
                    mult
                )
                self.assertEqual(
                    round(self.CV.distance_from_xy(
                        (shift[0], shift[1]),
                        (shift[0] + mult, shift[1] + mult),
                    ), 10),
                    round(mult*2**0.5, 10)
                )
                self.assertEqual(
                    round(self.CV.distance_from_xy(
                        (shift[0], shift[1]),
                        (shift[0] - mult, shift[1]),
                    ), 10),
                    mult
                )
                self.assertEqual(
                    round(self.CV.distance_from_xy(
                        (shift[0], shift[1]),
                        (shift[0] - mult*3**0.5/2, shift[1] - mult/2),
                    ), 10),
                    mult
                )

    def test_normalized_angle(self):
        for angle in [1e-5 - 180, -90, 0, 123, 180]:
            for mult in npr.randint(100, size=10):
                self.assertEqual(
                    round(self.CV.normalize_angle(angle + mult*360), 10),
                    angle
                )
        for angle in [1e-5, 90, 123, 360]:
            for mult in npr.randint(100, size=10):
                self.assertEqual(
                    round(self.CV.normalize_angle(angle + mult*360, 0), 10),
                    angle
                )
        for angle in [1e-5 - 0.6, 0, 123, 359]:
            for mult in npr.randint(100, size=10):
                self.assertEqual(
                    round(self.CV.normalize_angle(
                        angle + mult*360,
                        -0.6,
                    ), 10),
                    angle
                )

    '''
    general methods
    '''

    def test_time(self):
        self.CV.reset()
        self.assertEqual(self.CV.time(), '0s')

    def test_key_checker(self):
        self.CV._pybeans = {}
        for index in range(10):
            key, is_available = self.CV.key_checker(
                category='pybean',
                key=None,
            )
            self.assertTrue(is_available)
            self.assertEqual(key, f'pybean{index}')
            self.assertEqual(self.CV._pybean_index, index + 1)
            self.CV._pybeans[key] = None
            self.CV._pybeans[f'_{key}'] = None
        for index in range(10):
            _, is_available = self.CV.key_checker(
                category='pybean',
                key=f'_pybean{index}',
            )
            self.assertFalse(is_available)
            with self.assertRaises(UserWarning):
                self.CV.key_checker(
                    category='pybean',
                    key=f'pybean{index}',
                )

    '''
    main method
    '''

    def test_main(self):
        self.CV.reset()
        self.CV.save()


if __name__ == '__main__':
    unittest.main(verbosity=2)