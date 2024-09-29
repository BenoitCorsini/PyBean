import sys
import unittest
import numpy as np
from matplotlib.transforms import Affine2D, Bbox

sys.path.append('.')

from bean import Shape


class ShapeTests(unittest.TestCase):

    sh = Shape()

    '''
    hidden methods
    '''

    def test_get_ticks(self):
        self.assertTrue(np.all(self.sh._get_ticks(
            axis='x',
        ) == np.array([self.sh.xmin, self.sh.xmax])))
        self.assertTrue(np.all(self.sh._get_ticks(
            axis='y',
        ) == np.array([self.sh.ymin, self.sh.ymax])))
        self.assertTrue(np.all(self.sh._get_ticks(
            start=1,
            end=2,
        ) == np.array([1, 2])))
        self.assertTrue(np.all(self.sh._get_ticks(
            start=1,
            end=2,
            step=0.5,
        ) == np.array([1, 1.5, 2])))
        self.assertTrue(np.all(self.sh._get_ticks(
            start=1,
            end=4,
            n_line=3,
        ) == np.array([1, 2, 3, 4])))
        self.assertTrue(np.all(self.sh._get_ticks(
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
        path = self.sh._ticks_to_grid_path(xticks, yticks)
        self.assertTrue(np.all(
            path.vertices == np.array([(0, 0)]*4)
        ))
        self.assertTrue(np.all(
            path.codes == np.array([1, 2]*2)
        ))
        xticks = [0, 1]
        yticks = [0]
        path = self.sh._ticks_to_grid_path(xticks, yticks)
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
        path = self.sh._ticks_to_grid_path(xticks, yticks)
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
        path = self.sh._ticks_to_grid_path(xticks, yticks)
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
        self.assertEqual(self.sh._num_to_string(1.234, False, False), '1.23')
        self.assertEqual(self.sh._num_to_string(1.234, True, False), '1')
        self.assertEqual(self.sh._num_to_string(1.234, False, True), '1.2')
        self.assertEqual(self.sh._num_to_string(1.234, True, True), '1')

    def test_anchor_shift(self):
        bbox = Bbox([[0, 0], [2, 2]])
        self.assertTrue(np.all(self.sh.shift_from_anchor(bbox, 'north')
            == np.array([0, -1])))
        self.assertTrue(np.all(self.sh.shift_from_anchor(bbox, 'east')
            == np.array([-1, 0])))
        self.assertTrue(np.all(self.sh.shift_from_anchor(bbox, 'west')
            == np.array([1, 0])))
        self.assertTrue(np.all(self.sh.shift_from_anchor(bbox, 'south')
            == np.array([0, 1])))
        self.assertTrue(np.all(self.sh.shift_from_anchor(bbox, 'north east')
            == np.array([-1, -1])))
        self.assertTrue(np.all(self.sh.shift_from_anchor(bbox, 'east north')
            == np.array([-1, -1])))
        self.assertTrue(np.all(self.sh.shift_from_anchor(bbox, 'north west')
            == np.array([1, -1])))
        self.assertTrue(np.all(self.sh.shift_from_anchor(bbox, 'west north')
            == np.array([1, -1])))
        self.assertTrue(np.all(self.sh.shift_from_anchor(bbox, 'south east')
            == np.array([-1, 1])))
        self.assertTrue(np.all(self.sh.shift_from_anchor(bbox, 'east south')
            == np.array([-1, 1])))
        self.assertTrue(np.all(self.sh.shift_from_anchor(bbox, 'south west')
            == np.array([1, 1])))
        self.assertTrue(np.all(self.sh.shift_from_anchor(bbox, 'west south')
            == np.array([1, 1])))
        self.assertTrue(np.all(self.sh.shift_from_anchor(bbox, None)
            ==np.array([0, 0])))
        self.assertTrue(np.all(self.sh.shift_from_anchor(bbox, '')
            == np.array([0, 0])))
        self.assertTrue(np.all(self.sh.shift_from_anchor(bbox, 'not good...')
            == np.array([0, 0])))

    '''
    main method
    '''

    def test_main(self):
        self.sh.reset()
        self.sh.add_shape(
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
        self.sh.add_shape(
            key='square',
            shape_name='Rectangle',
            xy=(0.1, 0.1),
            width=0.2,
            height=0.2,
        )
        self.sh.set_shape(
            key='square',
            zorder=0,
            color='gold',
        )
        self.sh.add_raw_path(
            vertices=[(0, 0), (1, 1), (0.5, 0), (1, 1)],
            codes=[1, 2, 1, 2],
            lw=10,
            alpha=0.5,
            zorder=2,
            color='forestgreen',
        )
        self.sh.add_path(
            path=self.sh.curve_path(
                xy=(0, 0),
                a=self.sh.xmax - self.sh.xmin,
                b=self.sh.ymax - self.sh.ymin,
                theta1=10,
                theta2=80,
            ),
            lw=10,
            color='black',
            alpha=0.1,
            zorder=2,
            fill=False,
        )
        self.sh.add_paths(
            paths=self.sh.crescent_paths(
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
        self.sh.add_raw_path(
            key='path',
            vertices=[(0, 0)],
            lw=0,
            color='navy',
            zorder=-1,
        )
        self.sh.apply_to_shape(
            key='path',
            method='set_path',
            path=self.sh.merge_curves(*self.sh.crescent_paths(
                xy=(0.4, 0.3),
                radius=0.2,
                ratio=0.5,
                theta1=250,
                theta2=60,
                angle=200,
            )),
        )
        self.sh.add_copyright()
        self.sh.hide_copyright()
        self.sh.show_copyright()
        self.sh.grid(
            left=0.55,
            right=0.85,
            top=self.sh.ymax,
            bottom=self.sh.ymin,
            n_lines=4,
            lw=10,
            color='crimson',
            zorder=2,
        )
        self.sh.grid(
            left=0.55,
            right=0.85,
            top=self.sh.ymax,
            bottom=self.sh.ymin,
            n_lines=(8, 16),
            lw=2,
            color='darkred',
            zorder=2,
        )
        self.sh.grid(
            left=0.3,
            right=0.45,
            top=self.sh.ymax - 0.1,
            bottom=self.sh.ymax - 0.3,
            steps=4e-2,
            lw=10,
            color='crimson',
            zorder=2,
            capstyle='round',
        )
        self.sh.grid(
            left=0.3,
            right=0.45,
            top=self.sh.ymax - 0.1,
            bottom=self.sh.ymax - 0.3,
            steps=(1e-2, 2e-2),
            lw=2,
            color='darkred',
            zorder=2,
            capstyle='round',
        )
        self.sh.add_axis()
        self.sh.hide_axis()
        self.sh.show_axis()
        self.sh.add_info()
        self.sh.hide_info()
        self.sh.show_info('Testing')
        self.sh.hide_info()
        self.sh.show_info()
        self.sh.save('image_shape')


if __name__ == '__main__':
    unittest.main(verbosity=2)