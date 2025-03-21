import sys
import unittest
import numpy as np
import numpy.random as npr

sys.path.append('.')

from bean import Canvas


class CanvasTests(unittest.TestCase):

    cv = Canvas()

    '''
    dunder methods
    '''

    def test_string(self):
        self.assertTrue('Canvas' in str(self.cv))

    '''
    hidden methods
    '''

    def test_classes(self):
        classes = self.cv._get_classes()
        self.assertEqual(len(classes), 2)
        self.assertEqual(classes[0].__name__, 'object')
        self.assertEqual(classes[1].__name__, 'Canvas')

    def test_new_methods(self):
        methods = self.cv._get_new_methods()
        self.assertEqual(len(methods), 1)
        self.assertEqual(methods[0], '_new_canvas')

    def test_key_checker(self):
        self.cv._pybeans = {}
        for index in range(10):
            key, is_available = self.cv._key_checker(
                category='pybean',
                key=None,
            )
            self.assertTrue(is_available)
            self.assertEqual(key, f'pybean{index}')
            self.assertEqual(self.cv._pybean_index, index + 1)
            self.cv._pybeans[key] = None
            self.cv._pybeans[f'_{key}'] = None
        for index in range(10):
            _, is_available = self.cv._key_checker(
                category='pybean',
                key=f'_pybean{index}',
            )
            self.assertFalse(is_available)
            with self.assertRaises(UserWarning):
                self.cv._key_checker(
                    category='pybean',
                    key=f'pybean{index}',
                )

    def test_get_bound(self):
        self.cv.figsize = (4, 3)
        self.cv.ymax = None
        self.cv.reset()
        for bound_name in ['xmin', 'xmax', 'ymin']:
            self.assertEqual(
                getattr(self.cv, bound_name),
                self.cv._get_bound(bound_name)
            )
        self.assertEqual(self.cv._get_bound('ymax'), 0.75)
        self.cv.ymax = 1
        self.assertEqual(self.cv._get_bound('ymax'), 1)
        self.cv.figsize = (1, 1)
        self.cv.ymax = None
        self.cv.reset()
        for bound_name in ['xmin', 'xmax', 'ymin']:
            self.assertEqual(
                getattr(self.cv, bound_name),
                self.cv._get_bound(bound_name)
            )
        self.assertEqual(self.cv._get_bound('ymax'), 1)

    '''
    static methods
    '''

    def test_cmap(self):
        n_colours = 2
        colour_list = npr.rand(n_colours, 4)
        cmap = self.cv.get_cmap(colour_list)
        for index, colour in enumerate(colour_list):
            self.assertTrue(np.all(
                colour == cmap(index/(n_colours - 1))
            ))

    def test_greyscale(self):
        self.assertEqual(
            self.cv.get_greyscale(True),
            self.cv.get_cmap(['white', 'black'])
        )
        self.assertEqual(
            self.cv.get_greyscale(False),
            self.cv.get_cmap(['black', 'white'])
        )

    def test_cscale(self):
        colour = npr.rand(3)
        self.assertEqual(
            self.cv.get_cscale(colour),
            self.cv.get_cmap(['white', colour, 'black'])
        )
        colour = npr.rand(3)
        self.assertEqual(
            self.cv.get_cscale(colour, start_with='same'),
            self.cv.get_cmap([colour, 'black'])
        )
        colour = npr.rand(3)
        self.assertEqual(
            self.cv.get_cscale(colour, end_with='same'),
            self.cv.get_cmap(['white', colour])
        )
        colour = npr.rand(3)
        start = npr.rand(3)
        end = npr.rand(3)
        self.assertEqual(
            self.cv.get_cscale(colour, start_with=start, end_with=end),
            self.cv.get_cmap([start, colour, end])
        )
        colour = npr.rand(3)
        self.assertEqual(
            self.cv.get_cscale(colour, start_with='same', end_with='same'),
            self.cv.get_cmap([colour]*2)
        )

    def test_time_string(self):
        self.assertEqual(self.cv.time_to_string(0), '0s')
        self.assertEqual(self.cv.time_to_string(59), '59s')
        self.assertEqual(self.cv.time_to_string(60), '1m0s')
        self.assertEqual(self.cv.time_to_string(3599), '59m59s')
        self.assertEqual(self.cv.time_to_string(3600), '1h0m0s')
        self.assertEqual(self.cv.time_to_string(3723), '1h2m3s')

    '''
    general methods
    '''

    def test_time(self):
        self.cv.reset()
        self.assertEqual(self.cv.time(), '0s')

    '''
    main method
    '''

    def test_main(self):
        self.cv.reset()
        self.cv.save('image_canvas')


if __name__ == '__main__':
    unittest.main(verbosity=2)