import os.path as osp
import numpy as np
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties
from matplotlib.text import TextPath
from matplotlib.transforms import Affine2D

from .canvas import Canvas


class Shape(Canvas):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._new_shape()

    def _new_shape(self):
        self._shapes = {}
        self._key_index = 0
        if hasattr(self, 'copyright'):
            self.add_copyright()

    def add_shape(self, shape_name, key=None, *args, **kwargs):
        shape = self.ax.add_patch(
            getattr(patches, shape_name)(*args, **kwargs)
        )
        if key is None:
            key = f'shape{self._key_index}'
            self._key_index += 1
        if key in self._shapes:
            raise UserWarning(f'key \'{key}\' already used for a new shape.')
            self._shapes[key].set_visible(False)
        self._shapes[key] = shape
        return shape

    def apply_to_shape(self, method, key, *args, **kwargs):
        shape = self._shapes[key]
        return getattr(shape, method)(*args, **kwargs)

    def set_shape(self, key, *args, **kwargs):
        return self.apply_to_shape('set', key, *args, **kwargs)

    def add_copyright(self):
        margin = self.copyright.get('margin', 0)
        xscale = (self.xmax - self.xmin)*self.figsize[1]/self.figsize[0]
        yscale = self.ymax - self.ymin
        xy = (
            self.xmin + margin*xscale,
            self.ymin + margin*yscale,
        )
        height = yscale*self.copyright.get('height', 1)
        path = self.path_from_string(
            s=self.copyright.get('text', 'PyBean'),
            xy=xy,
            font_properties=self.copyright.get('font_properties', {}),
            anchor='south west',
            height=height,
        )
        self.add_shape(
            key='copyright_fill',
            shape_name='PathPatch',
            path=path,
            lw=0,
            color=self.copyright.get('fc', 'black'),
            **self.copyright.get('params', {})
        )
        self.add_shape(
            key='copyright_line',
            shape_name='PathPatch',
            path=path,
            lw=self.copyright.get('lw', 0),
            color=self.copyright.get('ec', 'black'),
            fill=False,
            **self.copyright.get('params', {})
        )

    # https://www.rapidtables.com/code/text/unicode-characters.html
    def path_from_string(self,
                         s,
                         xy=(0, 0),
                         size=None,
                         font_properties={},
                         anchor=None,
                         height=None):
        path = TextPath(
            xy=xy,
            s=s,
            size=size,
            prop=FontProperties(**font_properties)
        )
        if height is not None:
            bbox = path.get_extents()
            transform = Affine2D()
            self.shift_transform(transform, bbox, anchor)
            self.scale_transform(transform, bbox, height)
            transform.translate(*xy)
            path = path.transformed(transform)
        return path

    @staticmethod
    def shift_transform(transform, bbox, anchor):
        transform.translate(*(-(bbox.size/2 + bbox.p0)))
        transform.translate(*Shape.shift_from_anchor(
            bbox=bbox,
            anchor=anchor
        ))
        return transform

    @staticmethod
    def shift_from_anchor(bbox, anchor=None):
        if anchor is None:
            return np.array([0, 0])
        elif anchor == 'north':
            return np.array([0, - bbox.size[1]/2])
        elif anchor == 'south':
            return np.array([0, bbox.size[1]/2])
        elif anchor == 'east':
            return np.array([- bbox.size[0]/2, 0])
        elif anchor == 'west':
            return np.array([bbox.size[0]/2, 0])
        elif ' ' in anchor:
            anchors = anchor.strip().split(' ')
            shifts = [
                Shape.shift_from_anchor(bbox, anchor) for anchor in anchors
            ]
            return np.sum(shifts, axis=0)
        else:
            return np.array([0, 0])

    def scale_transform(self, transform, bbox, height):
        xy_ratio = (self.xmax - self.xmin)/(self.ymax - self.ymin)
        figsize_ratio = self.figsize[0]/self.figsize[1]
        transform.scale(height/bbox.size[1])
        transform.scale(xy_ratio/figsize_ratio, 1)
        return transform

    def main(self):
        print(self)
        print(self._get_new_methods())
        self.add_shape(shape_name='Circle', key='test', xy=(0, 1), radius=0.5)
        self.add_shape(shape_name='Circle', xy=(1, 0), radius=0.5)
        self.save()
        self.reset()