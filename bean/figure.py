import argparse
import os
import os.path as osp
import numpy as np
import matplotlib.figure as figure
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from matplotlib.transforms import Affine2D
from time import time

from .params import PARAMS


class Figure(object):

    def __init__(self, default_params=PARAMS, **kwargs):
        for key, value in default_params.items():
            setattr(self, key, value)
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.parser = argparse.ArgumentParser()
        self.reset()

    def new_param(self, *args, **kwargs):
        self.parser.add_argument(*args, **kwargs)

    def get_kwargs(self):
        return vars(self.parser.parse_args())

    def reset(self):
        self.start_time = time()
        self.__figure__()

    def __figure__(self):
        self.fig = figure.Figure(figsize=self.figsize, dpi=self.dpi)
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.ax = self.fig.add_subplot()
        self.ax.set_xlim(self.xmin, self.xmax)
        self.ax.set_ylim(self.ymin, self.ymax)
        self.ax.set_axis_off()
        self.__copyright__()

    @staticmethod
    def is_patch(obj):
        return isinstance(obj, patches.Patch)

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
            return np.sum([Figure.shift_from_anchor(bbox, anc) for anc in anchor.split(' ')], axis=0)
        else:
            return np.array([0, 0])

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

    def __copyright__(self):
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

    def save(self, name='image', image_dir=None, transparent=False):
        if image_dir is None:
            image_dir = self.image_dir
        if not osp.exists(image_dir):
            os.makedirs(image_dir)
        self.fig.savefig(osp.join(image_dir, name + '.png'), transparent=transparent)

    @staticmethod
    def rgb_to_hex(r, g, b):
        return f'#{r:02x}{g:02x}{b:02x}'

    @staticmethod
    def get_cmap(colour_list):
        return LinearSegmentedColormap.from_list(f'cmap of Benoit', colour_list)

    @staticmethod
    def get_greyscale(start_with_white=True):
        if start_with_white:
            colour_list = ['white', 'black']
        else:
            colour_list = ['black', 'white']
        return LinearSegmentedColormap.from_list(f'greyscale of Benoit', colour_list)

    @staticmethod
    def get_cmap_from_colour(colour='grey', start_with='white', end_with='black'):
        if (start_with == 'same') & (end_with == 'same'):
            raise UserWarning(f'The cmap is uniformly coloured!')
            colour_list = [colour]*2
        elif start_with == 'same':
            colour_list = [colour, end_with]
        elif end_with == 'same':
            colour_list = [start_with, colour]
        else:
            colour_list = [start_with, colour, end_with]
        return Figure.get_cmap(colour_list)

    @staticmethod
    def time_to_string(time):
        s = ''
        hours = int(time/3600)
        minutes = int((time - 60*hours)/60)
        seconds = int(time - 3600*hours - 60*minutes)
        if hours:
            s = f'{hours}h{minutes}m{seconds}s'
        elif minutes:
            s = f'{minutes}m{seconds}s'
        else:
            s = f'{seconds}s'
        return s

    def time(self):
        return self.time_to_string(time() - self.start_time)