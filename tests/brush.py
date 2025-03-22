import sys
import unittest
import numpy as np
import numpy.random as npr
from matplotlib.transforms import Affine2D, Bbox

sys.path.append('.')

from bean import Brush


class BrushTests(unittest.TestCase):

    bs = Brush()

    '''
    hidden methods
    '''

    def test_decimal_precision(self):
        xmin = self.bs.xmin
        ymin = self.bs.ymin
        for step in range(1, 10):
            self.bs.xmin = step
            self.bs.ymin = step
            self.assertEqual(
                self.bs._decimal_precision(step),
                (True, True)
            )
            self.assertEqual(
                self.bs._decimal_precision(float(step)),
                (True, True)
            )
            self.assertEqual(
                self.bs._decimal_precision(step/10),
                (False, True)
            )
            self.assertEqual(
                self.bs._decimal_precision(step + 0.5),
                (False, True)
            )
            self.assertEqual(
                self.bs._decimal_precision(step/100),
                (False, False)
            )
            self.assertEqual(
                self.bs._decimal_precision(step + 0.05),
                (False, False)
            )
            self.bs.xmin /= 10
            self.assertEqual(
                self.bs._decimal_precision(step),
                (False, True)
            )
            self.assertEqual(
                self.bs._decimal_precision(float(step)),
                (False, True)
            )
            self.assertEqual(
                self.bs._decimal_precision(step/10),
                (False, True)
            )
            self.assertEqual(
                self.bs._decimal_precision(step + 0.5),
                (False, True)
            )
            self.assertEqual(
                self.bs._decimal_precision(step/100),
                (False, False)
            )
            self.assertEqual(
                self.bs._decimal_precision(step + 0.05),
                (False, False)
            )
            self.bs.ymin /= 100
            self.assertEqual(
                self.bs._decimal_precision(step),
                (False, False)
            )
            self.assertEqual(
                self.bs._decimal_precision(float(step)),
                (False, False)
            )
            self.assertEqual(
                self.bs._decimal_precision(step/10),
                (False, False)
            )
            self.assertEqual(
                self.bs._decimal_precision(step + 0.5),
                (False, False)
            )
            self.assertEqual(
                self.bs._decimal_precision(step/100),
                (False, False)
            )
            self.assertEqual(
                self.bs._decimal_precision(step + 0.05),
                (False, False)
            )
        self.bs.xmin = xmin
        self.bs.ymin = ymin

    def test_get_ticks(self):
        self.assertTrue(np.all(self.bs._get_ticks(
            axis='x',
        ) == np.array([self.bs.xmin, self.bs.xmax])))
        self.assertTrue(np.all(self.bs._get_ticks(
            axis='y',
        ) == np.array([self.bs.ymin, self.bs.ymax])))
        self.assertTrue(np.all(self.bs._get_ticks(
            start=1,
            end=2,
        ) == np.array([1, 2])))
        self.assertTrue(np.all(self.bs._get_ticks(
            start=1,
            end=2,
            step=0.5,
        ) == np.array([1, 1.5, 2])))
        self.assertTrue(np.all(self.bs._get_ticks(
            start=1,
            end=4,
            n_line=3,
        ) == np.array([1, 2, 3, 4])))
        self.assertTrue(np.all(self.bs._get_ticks(
            start=0,
            end=1,
            step=0.5,
            n_line=4,
        ) == np.array([0, 0.5, 1])))

    '''
    static methods
    '''

    def test_ticks_path(self):
        xticks = [0]
        yticks = [0]
        path = self.bs._ticks_to_grid_path(xticks, yticks)
        self.assertTrue(np.all(
            path.vertices == np.array([(0, 0)]*4)
        ))
        self.assertTrue(np.all(
            path.codes == np.array([1, 2]*2)
        ))
        xticks = [0, 1]
        yticks = [0]
        path = self.bs._ticks_to_grid_path(xticks, yticks)
        self.assertTrue(np.all(
            path.vertices == np.array([
                (0, 0),
                (0, 0),
                (1, 0),
                (1, 0),
                (0, 0),
                (1, 0),
            ])
        ))
        self.assertTrue(np.all(
            path.codes == np.array([1, 2]*3)
        ))
        xticks = [0]
        yticks = [0, 1]
        path = self.bs._ticks_to_grid_path(xticks, yticks)
        self.assertTrue(np.all(
            path.vertices == np.array([
                (0, 0),
                (0, 1),
                (0, 0),
                (0, 0),
                (0, 1),
                (0, 1),
            ])
        ))
        self.assertTrue(np.all(
            path.codes == np.array([1, 2]*3)
        ))
        xticks = [0, 1]
        yticks = [0, 1]
        path = self.bs._ticks_to_grid_path(xticks, yticks)
        self.assertTrue(np.all(
            path.vertices == np.array([
                (0, 0),
                (0, 1),
                (1, 0),
                (1, 1),
                (0, 0),
                (1, 0),
                (0, 1),
                (1, 1),
            ])
        ))
        self.assertTrue(np.all(
            path.codes == np.array([1, 2]*4)
        ))

    def test_num_string(self):
        self.assertEqual(self.bs._num_to_string(1.234, False, False), '1.23')
        self.assertEqual(self.bs._num_to_string(1.234, True, False), '1')
        self.assertEqual(self.bs._num_to_string(1.234, False, True), '1.2')
        self.assertEqual(self.bs._num_to_string(1.234, True, True), '1')

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
            one_dim = self.bs.angle_shift(angle)
            two_dim = self.bs.angle_shift(angle, two_dim=True)
            self.assertTrue(np.all(np.abs(one_dim - array) < 1e-10))
            self.assertTrue(np.all(np.abs(two_dim - array) < 1e-10))
            self.assertEqual(one_dim.shape, (2, ))
            self.assertEqual(two_dim.shape, (1, 2))

    def test_xy_angle(self):
        for mult in [0, 1, 2, 10]:
            for shift in [(0, 0), (1, 1), (1/3, -5**0.5)]:
                self.assertEqual(
                    round(self.bs.angle_from_xy(
                        (shift[0], shift[1]),
                        (shift[0] + mult, shift[1]),
                    ), 10),
                    0
                )
                self.assertEqual(
                    round(self.bs.angle_from_xy(
                        (shift[0], shift[1]),
                        (shift[0] + mult, shift[1] + mult),
                    ), 10),
                    45*(mult > 0)
                )
                self.assertEqual(
                    round(self.bs.angle_from_xy(
                        (shift[0], shift[1]),
                        (shift[0] - mult, shift[1]),
                    ), 10),
                    180*(mult > 0)
                )
                self.assertEqual(
                    round(self.bs.angle_from_xy(
                        (shift[0], shift[1]),
                        (shift[0] - mult*3**0.5/2, shift[1] - mult/2),
                    ), 10),
                    -150*(mult > 0)
                )

    def text_xy_distance(self):
        for mult in [0, 1, 2, 10]:
            for shift in [(0, 0), (1, 1), (1/3, -5**0.5)]:
                self.assertEqual(
                    round(self.bs.distance_from_xy(
                        (shift[0], shift[1]),
                        (shift[0] + mult, shift[1]),
                    ), 10),
                    mult
                )
                self.assertEqual(
                    round(self.bs.distance_from_xy(
                        (shift[0], shift[1]),
                        (shift[0] + mult, shift[1] + mult),
                    ), 10),
                    round(mult*2**0.5, 10)
                )
                self.assertEqual(
                    round(self.bs.distance_from_xy(
                        (shift[0], shift[1]),
                        (shift[0] - mult, shift[1]),
                    ), 10),
                    mult
                )
                self.assertEqual(
                    round(self.bs.distance_from_xy(
                        (shift[0], shift[1]),
                        (shift[0] - mult*3**0.5/2, shift[1] - mult/2),
                    ), 10),
                    mult
                )

    def test_normalized_angle(self):
        for angle in [1e-5 - 180, -90, 0, 123, 180]:
            for mult in npr.randint(100, size=10):
                self.assertEqual(
                    round(self.bs.normalize_angle(angle + mult*360), 10),
                    angle
                )
        for angle in [1e-5, 90, 123, 360]:
            for mult in npr.randint(100, size=10):
                self.assertEqual(
                    round(self.bs.normalize_angle(angle + mult*360, 0), 10),
                    angle
                )
        for angle in [1e-5 - 0.6, 0, 123, 359]:
            for mult in npr.randint(100, size=10):
                self.assertEqual(
                    round(self.bs.normalize_angle(
                        angle + mult*360,
                        -0.6,
                    ), 10),
                    angle
                )

    def test_anchor_shift(self):
        bbox = Bbox([[0, 0], [2, 2]])
        self.assertTrue(np.all(self.bs.shift_from_anchor(bbox, 'north')
            == np.array([0, -1])))
        self.assertTrue(np.all(self.bs.shift_from_anchor(bbox, 'east')
            == np.array([-1, 0])))
        self.assertTrue(np.all(self.bs.shift_from_anchor(bbox, 'west')
            == np.array([1, 0])))
        self.assertTrue(np.all(self.bs.shift_from_anchor(bbox, 'south')
            == np.array([0, 1])))
        self.assertTrue(np.all(self.bs.shift_from_anchor(bbox, 'north east')
            == np.array([-1, -1])))
        self.assertTrue(np.all(self.bs.shift_from_anchor(bbox, 'east north')
            == np.array([-1, -1])))
        self.assertTrue(np.all(self.bs.shift_from_anchor(bbox, 'north west')
            == np.array([1, -1])))
        self.assertTrue(np.all(self.bs.shift_from_anchor(bbox, 'west north')
            == np.array([1, -1])))
        self.assertTrue(np.all(self.bs.shift_from_anchor(bbox, 'south east')
            == np.array([-1, 1])))
        self.assertTrue(np.all(self.bs.shift_from_anchor(bbox, 'east south')
            == np.array([-1, 1])))
        self.assertTrue(np.all(self.bs.shift_from_anchor(bbox, 'south west')
            == np.array([1, 1])))
        self.assertTrue(np.all(self.bs.shift_from_anchor(bbox, 'west south')
            == np.array([1, 1])))
        self.assertTrue(np.all(self.bs.shift_from_anchor(bbox, None)
            ==np.array([0, 0])))
        self.assertTrue(np.all(self.bs.shift_from_anchor(bbox, '')
            == np.array([0, 0])))
        self.assertTrue(np.all(self.bs.shift_from_anchor(bbox, 'not good...')
            == np.array([0, 0])))

    '''
    main method
    '''

    def test_main(self):
        self.bs.reset()
        self.bs.add_shape(
            key='rectangle',
            shape_name='Rectangle',
            xy=(0.1, 0.1),
            width=0.2,
            height=0.1,
            lw=5,
            color='crimson',
            zorder=1,
            fill=False,
        )
        self.bs.add_shape(
            key='square',
            shape_name='Rectangle',
            xy=(0.1, 0.1),
            width=0.2,
            height=0.2,
        )
        self.bs.set_shape(
            key='square',
            zorder=0,
            color='gold',
        )
        self.bs.add_raw_path(
            vertices=[(0, 0), (1, 1), (0.5, 0), (1, 1)],
            codes=[1, 2, 1, 2],
            lw=10,
            alpha=0.5,
            zorder=2,
            color='forestgreen',
        )
        self.bs.add_path(
            path=self.bs.curve_path(
                xy=(0, 0),
                a=self.bs.xmax - self.bs.xmin,
                b=self.bs.ymax - self.bs.ymin,
                theta1=10,
                theta2=80,
            ),
            lw=10,
            color='black',
            alpha=0.1,
            zorder=2,
            fill=False,
        )
        self.bs.add_paths(
            paths=self.bs.crescent_paths(
                xy=(0.6, 0.3),
                radius=0.2,
                ratio=0.5,
                theta1=250,
                theta2=60,
                angle=20,
            ),
            lw=0,
            color='navy',
            zorder=-1,
        )
        self.bs.add_raw_path(
            key='path',
            vertices=[(0, 0)],
            lw=0,
            color='navy',
            zorder=-1,
        )
        self.bs.apply_to_shape(
            key='path',
            method='set_path',
            path=self.bs.merge_curves(*self.bs.crescent_paths(
                xy=(0.4, 0.3),
                radius=0.2,
                ratio=0.5,
                theta1=250,
                theta2=60,
                angle=200,
            )),
        )
        self.bs.add_copyright()
        self.bs.hide_copyright()
        self.bs.show_copyright()
        self.bs.grid(
            left=0.55,
            right=0.85,
            top=self.bs.ymax,
            bottom=self.bs.ymin,
            n_lines=4,
            lw=10,
            color='crimson',
            zorder=2,
        )
        self.bs.grid(
            left=0.55,
            right=0.85,
            top=self.bs.ymax,
            bottom=self.bs.ymin,
            n_lines=(8, 16),
            lw=2,
            color='darkred',
            zorder=2,
        )
        self.bs.grid(
            left=0.3,
            right=0.45,
            top=self.bs.ymax - 0.1,
            bottom=self.bs.ymax - 0.3,
            steps=4e-2,
            lw=10,
            color='crimson',
            zorder=2,
            capstyle='round',
        )
        self.bs.grid(
            left=0.3,
            right=0.45,
            top=self.bs.ymax - 0.1,
            bottom=self.bs.ymax - 0.3,
            steps=(1e-2, 2e-2),
            lw=2,
            color='darkred',
            zorder=2,
            capstyle='round',
        )
        self.bs.add_axis()
        self.bs.hide_axis()
        self.bs.show_axis()
        self.bs.add_info()
        self.bs.hide_info()
        self.bs.show_info('Testing')
        self.bs.hide_info()
        self.bs.show_info()
        self.bs.save('image_shape')


if __name__ == '__main__':
    unittest.main(verbosity=2)
