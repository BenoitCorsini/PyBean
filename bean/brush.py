import argparse
import os
import os.path as osp
import numpy as np
import matplotlib.figure as figure
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.font_manager import FontProperties
from matplotlib.text import TextPath
from matplotlib.transforms import Affine2D
from time import time

from .canvas import Canvas


class Brush(Canvas):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_copyright()

    def reset(self):
        super().reset()
        self.add_copyright()
        return self

    def add_copyright(self):
        x = self.xmin + (self.xmax - self.xmin)*self.copyright.get('margin', 0)*self.figsize[1]/self.figsize[0]
        y = self.ymin + (self.ymax - self.ymin)*self.copyright.get('margin', 0)
        height = (self.ymax - self.ymin)*self.copyright.get('ratio', 1)
        prop = FontProperties(fname=osp.join(
            osp.dirname(osp.realpath(__file__)),
            self.copyright.get('fname', '@BC.otf')
        ))
        path = self.path_from_string(
            s=self.copyright.get('text', 'Benoit Corsini'),
            x=x,
            y=y,
            height=height,
            prop=prop,
            anchor='south west',
        )
        self.ax.add_patch(patches.PathPatch(
            path=path,
            lw=0,
            color=self.copyright.get('fc', 'black'),
            **self.copyright.get('params', {})
        ))
        self.ax.add_patch(patches.PathPatch(
            path=path,
            lw=self.copyright.get('lw', 0),
            color=self.copyright.get('ec', 'black'),
            fill=False,
            **self.copyright.get('params', {})
        ))

    # https://www.rapidtables.com/code/text/unicode-characters.html
    def path_from_string(self, s, x=0, y=0, height=1, prop=None, anchor=None):
        path = TextPath((0, 0), s, prop=prop)
        bbox = path.get_extents()
        transform = Affine2D()
        transform.translate(*(-(bbox.size/2 + bbox.p0)))
        transform.translate(*self.shift_from_anchor(bbox=bbox, anchor=anchor))
        transform.scale(height/bbox.size[1])
        transform.scale(self.figsize[1]/self.figsize[0]*(self.xmax - self.xmin)/(self.ymax - self.ymin), 1)
        transform.translate(x, y)
        return path.transformed(transform)

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
            anchor = anchor.strip()
            return np.sum([Brush.shift_from_anchor(bbox, anc) for anc in anchor.split(' ')], axis=0)
        else:
            return np.array([0, 0])

    def main(self):
        print(self)
        self.save()