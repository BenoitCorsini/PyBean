import argparse
import os
import os.path as osp
import matplotlib.figure as figure
from matplotlib.colors import LinearSegmentedColormap as LSC
from time import time

from .default import DEFAULT


class Origin(object):
    pass


class Canvas(Origin):

    def __init__(self, **kwargs):
        for key, value in DEFAULT.items():
            setattr(self, key, value)
        for key, value in kwargs.items():
            setattr(self, key, value)
        assert hasattr(self, 'figsize')
        assert hasattr(self, 'dpi')
        assert hasattr(self, 'xmin')
        assert hasattr(self, 'xmax')
        assert hasattr(self, 'ymin')
        assert hasattr(self, 'ymax')
        self.parser = argparse.ArgumentParser()
        self._new_canvas()

    def _new_canvas(self):
        self.start_time = time()
        return self.canvas()

    def _get_new_methods(self):
        new_methods = []
        classes = [self.__class__]
        while classes:
            current_class = classes.pop()
            for method in sorted(current_class.__dict__, reverse=True):
                if method.startswith('_new'):
                    new_methods.append(method)
            classes += list(current_class.__bases__)
        return new_methods[::-1]

    def reset(self):
        for method in self._get_new_methods():
            getattr(self, method)()

    def canvas(self):
        self.fig = figure.Figure(figsize=self.figsize, dpi=self.dpi)
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.ax = self.fig.add_subplot()
        self.ax.set_xlim(self.xmin, self.xmax)
        self.ax.set_ylim(self.ymin, self.ymax)
        self.ax.set_axis_off()
        return self

    def __str__(self):
        s = f'PyBean {self.__class__.__name__}'
        s += f' (figsize={self.figsize},'
        s += f' dpi={self.dpi})'
        if hasattr(self, 'copyright'):
            if 'text' in self.copyright:
                s += '\nCopyright: '
                s += self.copyright['text']
        return s

    def save(self, name='image', image_dir=None, transparent=False):
        if image_dir is None:
            image_dir = '.'
        if not osp.exists(image_dir):
            os.makedirs(image_dir)
        self.fig.savefig(
            osp.join(image_dir, name + '.png'),
            transparent=transparent
        )

    def add_param(self, *args, **kwargs):
        self.parser.add_argument(*args, **kwargs)

    def get_kwargs(self):
        return vars(self.parser.parse_args())

    @staticmethod
    def get_cmap(colour_list):
        return LSC.from_list('pybean cmap', colour_list)

    @staticmethod
    def get_greyscale(start_with_white=True):
        if start_with_white:
            colour_list = ['white', 'black']
        else:
            colour_list = ['black', 'white']
        return LSC.from_list('pybean greyscale', colour_list)

    @staticmethod
    def get_cscale(colour='grey', start_with='white', end_with='black'):
        if (start_with == 'same') & (end_with == 'same'):
            raise UserWarning(f'The cmap is uniformly coloured!')
            colour_list = [colour]*2
        elif start_with == 'same':
            colour_list = [colour, end_with]
        elif end_with == 'same':
            colour_list = [start_with, colour]
        else:
            colour_list = [start_with, colour, end_with]
        return LSC.from_list('pybean cscale', colour_list)

    @staticmethod
    def time_to_string(time):
        hours = int(time/3600)
        minutes = int((time - 60*hours)/60)
        seconds = int(time - 3600*hours - 60*minutes)
        if hours:
            return f'{hours}h{minutes}m{seconds}s'
        elif minutes:
            return f'{minutes}m{seconds}s'
        else:
            return f'{seconds}s'

    def time(self):
        return self.time_to_string(time() - self.start_time)

    def main(self):
        print(self)
        self.save()
        print(self._get_new_methods())
        self.reset()
        self.add_param('--colour', type=str, default='royalblue')
        cmap = self.get_cscale(**self.get_kwargs())
        print(cmap == Canvas.get_cscale(**self.get_kwargs()))
        print(self.time())