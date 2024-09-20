import argparse
import os
import os.path as osp
import numpy as np
import matplotlib.figure as figure
from matplotlib.colors import LinearSegmentedColormap as LSC
from time import time
from typing_extensions import Any, Self

from .default import DEFAULT


class Canvas(object):

    '''
    fundamental variables
    '''

    _canvas_params = {
        'figsize' : int,
        'dpi' : int,
        'xmin' : float,
        'xmax' : float,
        'ymin' : float,
        'ymax' : float,
    }

    _canvas_nargs = {
        'figsize' : 2,
    }

    '''
    dunder methods
    '''

    def __init__(
            self: Self,
            **kwargs,
        ) -> None:
        # initiate class
        for key, value in DEFAULT.items():
            setattr(self, key, value)
        self._parser = argparse.ArgumentParser()
        self._set_params(**kwargs)
        self.reset()

    def __repr__(
            self: Self,
        ) -> str:
        # string representation of self
        s = f'{self.__class__.__name__}'
        s += f' (figsize=({self.figsize[0]}, {self.figsize[1]}),'
        s += f' dpi={self.dpi})'
        return s

    def __str__(
            self: Self,
        ) -> str:
        # string representation of self
        s = 'PyBean ' + self.__repr__()
        if hasattr(self, 'copyright'):
            if 'text' in self.copyright:
                s += '\nCopyright: '
                s += self.copyright['text']
        return s

    '''
    hidden methods
    '''

    def _get_classes(
            self: Self,
        ) -> list:
        # lists all parents classes from most fundamental to current
        classes = []
        classes_to_explore = [self.__class__]
        while classes_to_explore:
            current_class = classes_to_explore.pop()
            classes.append(current_class)
            classes_to_explore += list(current_class.__bases__)
        return classes[::-1]

    def _new_canvas(
            self: Self,
        ) -> Self:
        # new canvas instance
        self.start_time = time()
        self.fig = figure.Figure(figsize=self.figsize, dpi=self.dpi)
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.ax = self.fig.add_subplot()
        self.ax.set_xlim(self.xmin, self.xmax)
        self.ax.set_ylim(self.ymin, self.ymax)
        self.ax.set_axis_off()
        return self

    def _set_params(
            self: Self,
            **kwargs,
        ) -> None:
        # collect and setup the parameters of the class and its parents
        for current_class in self._get_classes():
            class_name = current_class.__name__.lower()
            class_params = getattr(self, f'_{class_name}_params', {})
            class_nargs = getattr(self, f'_{class_name}_nargs', {})
            for param, param_type in class_params.items():
                assert hasattr(self, param)
                self.add_param(
                    f'--{param}',
                    nargs=class_nargs.get(param, None),
                    type=param_type,
                    default=getattr(self, param),
                )
        kwargs.update(self.get_kwargs())
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _get_new_methods(
            self: Self,
        ) -> list[str]:
        # get _new methods in order of depth
        new_methods = []
        for current_class in self._get_classes():
            for method in sorted(current_class.__dict__):
                if method.startswith('_new'):
                    new_methods.append(method)
        return new_methods

    '''
    static methods
    '''

    @staticmethod
    def get_cmap(
            colour_list: list,
        ) -> LSC:
        # creates a cmap using the list of colours
        return LSC.from_list('pybean cmap', colour_list)

    @staticmethod
    def get_greyscale(
            start_with_white: bool = True,
        ) -> LSC:
        # creates a grayscale from white to black
        if start_with_white:
            colour_list = ['white', 'black']
        else:
            colour_list = ['black', 'white']
        return LSC.from_list('pybean greyscale', colour_list)

    @staticmethod
    def get_cscale(
            colour: str = 'grey',
            start_with: str = 'white',
            end_with: str = 'black',
        ) -> LSC:
        # creates a cmap scaling around a given colour
        colour_list = [colour]
        if not isinstance(start_with, str) or start_with != 'same':
            colour_list = [start_with] + colour_list
        if not isinstance(start_with, str) or end_with != 'same':
            colour_list = colour_list + [end_with]
        if len(colour_list) == 1:
            colour_list = colour_list*2
        return LSC.from_list('pybean cscale', colour_list)

    @staticmethod
    def time_to_string(
            time: float,
        ) -> str:
        # transform a time in (hours, minutes, seconds) string format
        hours = int(time/3600)
        minutes = int((time - 3600*hours)/60)
        seconds = int(time - 3600*hours - 60*minutes)
        if hours:
            return f'{hours}h{minutes}m{seconds}s'
        elif minutes:
            return f'{minutes}m{seconds}s'
        else:
            return f'{seconds}s'

    @staticmethod
    def angle_shift(
            angle: float = 0,
            two_dim: bool = False,
        ) -> np.array:
        # return a vector for shifting in the angle direction
        shift = np.array([
            np.cos(np.pi*angle/180),
            np.sin(np.pi*angle/180),
        ])
        if two_dim:
            shift = shift.reshape((1, 2))
        return shift

    @staticmethod
    def angle_from_xy(
            xy1: (float, float),
            xy2: (float, float),
        ) -> float:
        # computes the angle formed by the two positions
        vector = np.array(xy2) - np.array(xy1)
        norm = np.sum(vector**2)**0.5
        if not norm:
            return 0.
        vector = vector/norm
        angle = np.arccos(vector[0])
        if vector[1] < 0:
            angle *= -1
        return angle*180/np.pi

    @staticmethod
    def distance_from_xy(
            xy1: (float, float),
            xy2: (float, float),
        ) -> float:
        # computes the angle formed by the two positions
        distance = np.array(xy2) - np.array(xy1)
        distance = np.sum(distance**2)**0.5
        return distance

    @staticmethod
    def normalize_angle(
            angle: float,
            lower_bound: float = -180,
        ) -> float:
        # set an angle to (lower_bound, lower_bound + 360]
        while angle <= lower_bound:
            angle += 360
        while angle > lower_bound + 360:
            angle -= 360
        return angle

    '''
    general methods
    '''

    def add_param(
            self: Self,
            *args,
            **kwargs,
        ) -> None:
        # add a parameter to the parser
        self._parser.add_argument(*args, **kwargs)

    def get_kwargs(
            self: Self,
            **kwargs
        ) -> dict:
        # return the arguments of the parser as a dictionnary
        parser_kwargs = vars(self._parser.parse_args())
        parser_kwargs.update(kwargs)
        return parser_kwargs.copy()

    def reset(
            self: Self,
        ) -> Self:
        # reset self using _new methods in order of depth
        for method in self._get_new_methods():
            getattr(self, method)()
        return self

    def save(
            self: Self,
            name: str = 'image',
            image_dir: str = None,
            transparent: bool = False,
        ) -> None:
        # save the current state of the figure
        if image_dir is None:
            image_dir = '.'
        if not osp.exists(image_dir):
            os.makedirs(image_dir)
        self.fig.savefig(
            osp.join(image_dir, name + '.png'),
            transparent=transparent
        )

    def time(
            self: Self,
        ) -> str:
        # compute the current time duration of the algorithm
        return self.time_to_string(time() - self.start_time)

    def key_checker(
            self: Self,
            category: str,
            key: Any = None,
        ) -> (Any, bool):
        # check whether the key is available from the category
        if key is None:
            index = getattr(self, f'_{category}_index', 0)
            key = f'{category}{index}'
            setattr(self, f'_{category}_index', index + 1)
        if key in getattr(self, f'_{category}s', {}):
            if key.startswith('_'):
                return key, False
            else:
                raise UserWarning(
                    f'key \'{key}\' already used for a {category}.'
                )
                return key, False
        return key, True

    def help(
            self: Self,
        ) -> None:
        # print helpful tips
        doc_page = 'NOT READY YET'
        github_page = 'https://github.com/BenoitCorsini/PyBean'
        symbol_page = 'https://www.rapidtables.com'
        symbol_page += '/code/text/unicode-characters.html'
        print('Using the PyBean library \u2714')
        print(f'\u279E Take a look at the documentation: {doc_page}')
        print(f'\u279E Take a look at the Github page: {github_page}')
        print(f'\u279E Take a look at common symbols: {symbol_page}')

    '''
    main method
    '''

    def main(
            self: Self,
        ) -> None:
        # the main running function
        print(self)
        print(self._get_classes())
        print(self._get_new_methods())
        print(self.get_kwargs())
        self.save()
        self.reset()
        cmap = self.get_cscale()
        print(cmap == Canvas.get_cscale())
        print(self.time())
        self.help()