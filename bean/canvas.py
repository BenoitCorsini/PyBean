import argparse
import os
import os.path as osp
import inspect
import numpy as np
import numpy.random as npr
import matplotlib.figure as figure
from matplotlib.colors import LinearSegmentedColormap as LSC
from time import time
from typing_extensions import Any, Self


class Canvas(object):

    '''
    fundamental variables and function
    '''

    figsize = (16, 9)
    dpi = 100
    xmin = 0
    xmax = 1
    ymin = 0
    ymax = None
    seed = None

    _canvas_params = {
        'figsize' : int,
        'dpi' : int,
        'xmin' : float,
        'xmax' : float,
        'ymin' : float,
        'ymax' : float,
        'seed' : int,
    }

    _canvas_nargs = {
        'figsize' : 2,
    }

    def _new_canvas(
            self: Self,
        ) -> Self:
        # new canvas instance
        npr.seed(self.seed)
        self.fig = figure.Figure(figsize=self.figsize, dpi=self.dpi)
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.ax = self.fig.add_subplot()
        self.ax.set_xlim(
            self._get_bound('xmin'),
            self._get_bound('xmax'),
        )
        self.ax.set_ylim(
            self._get_bound('ymin'),
            self._get_bound('ymax'),
        )
        self.ax.set_axis_off()
        return self

    '''
    dunder methods
    '''

    def __init__(
            self: Self,
            **kwargs,
        ) -> None:
        # initiate class
        self._start_time = time()
        self._ymax_default = False
        self._parser = argparse.ArgumentParser()
        for key, value in kwargs.items():
            setattr(self, key, value)
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

    def _get_kwargs(
            self: Self,
        ) -> dict:
        # returns the arguments of the parser as a dictionnary
        return vars(self._parser.parse_args())

    def _key_checker(
            self: Self,
            category: str,
            key: Any = None,
        ) -> (Any, bool):
        # checks whether the key is available from the category
        if key is None:
            index = getattr(self, f'_{category}_index', 0)
            key = f'{category}{index}'
            setattr(self, f'_{category}_index', index + 1)
        if key in getattr(self, f'_{category}s', {}):
            if isinstance(key, str) and key.startswith('_'):
                return key, False
            else:
                raise UserWarning(
                    f'key \'{key}\' already used for a {category}.'
                )
                return key, False
        return key, True

    def _get_bound(
            self: Self,
            bound_name: str,
        ) -> float:
        # returns the value of the bound on the given axis
        if bound_name == 'ymax' and self.ymax is None:
            return self.figsize[1]/self.figsize[0]
        else:
            return getattr(self, bound_name)

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
        # transforms a time in (hours, minutes, seconds) string format
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
    def to_bean(
            file: str = None,
        ) -> str:
        # returns the directory of the PyBean library
        bean_dir = osp.dirname(osp.abspath(
            inspect.getfile(inspect.currentframe())
        ))
        if file is None:
            return bean_dir
        else:
            return osp.join(bean_dir, file)

    '''
    general methods
    '''

    def reset(
            self: Self,
        ) -> Self:
        # resets self using _new methods in order of depth
        for method in self._get_new_methods():
            getattr(self, method)()
        return self

    def add_arg(
            self: Self,
            *args,
            **kwargs,
        ) -> Self:
        # adds a parameter to the parser
        self._parser.add_argument(*args, **kwargs)
        return self

    def set_args(
            self: Self,
            include_all: bool = False,
        ) -> Self:
        # collects and sets up the argparse parameters
        if include_all:
            for current_class in self._get_classes():
                class_name = current_class.__name__.lower()
                class_params = getattr(self, f'_{class_name}_params', {})
                class_nargs = getattr(self, f'_{class_name}_nargs', {})
                for param, param_type in class_params.items():
                    assert hasattr(self, param)
                    self.add_arg(
                        f'--{param}',
                        nargs=class_nargs.get(param, None),
                        type=param_type,
                        default=getattr(self, param),
                    )
        kwargs = self._get_kwargs()
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self.reset()

    def save(
            self: Self,
            name: Any = 'image',
            image_dir: str = '.',
            transparent: bool = False,
        ) -> None:
        # saves the current state of the figure
        if not osp.exists(image_dir):
            os.makedirs(image_dir)
        self.fig.savefig(
            osp.join(image_dir, f'{name}.png'),
            transparent=transparent
        )

    def time(
            self: Self,
        ) -> str:
        # computes the current time duration of the algorithm
        return self.time_to_string(time() - self._start_time)

    def help(
            self: Self,
        ) -> None:
        # prints helpful tips
        doc_page = 'NOT READY YET'
        github_page = 'https://github.com/BenoitCorsini/PyBean'
        symbol_page = 'https://www.rapidtables.com'
        symbol_page += '/code/text/unicode-characters.html'
        print('Using the PyBean library \u2714')
        print(f'\u279E Take a look at the documentation: {doc_page}')
        print(f'\u279E Take a look at the Github page: {github_page}')
        print(f'\u279E Take a look at common symbols: {symbol_page}')