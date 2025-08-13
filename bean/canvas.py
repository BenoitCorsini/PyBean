import argparse
import os
import os.path as osp
import inspect
import numpy as np
import numpy.random as npr
import matplotlib.figure as figure
from matplotlib.colors import LinearSegmentedColormap, Colormap
from matplotlib import colormaps
from colorsys import hls_to_rgb
from time import time
from typing_extensions import Any, Self


class Canvas(object):

    '''
    fundamental variables and function
    '''

    figsize = (16, 9)
    dpi = 100
    left = 0
    right = None
    bottom = 0
    top = None
    seed = None

    _canvas_params = {
        'figsize' : int,
        'dpi' : int,
        'left' : float,
        'right' : float,
        'bottom' : float,
        'top' : float,
        'seed' : int,
    }

    _canvas_nargs = {
        'figsize' : 2,
    }

    def _init_canvas(
            self: Self,
        ) -> Self:
        # new canvas instance
        npr.seed(self.seed)
        self.fig = figure.Figure(figsize=self.figsize, dpi=self.dpi)
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.ax = self.fig.add_subplot()
        self.ax.set_axis_off()
        self.reframe()
        return self

    '''
    dunder methods
    '''

    def __init__(
            self: Self,
            **kwargs,
        ) -> None:
        # initiate class
        self._start = time()
        self._parser = argparse.ArgumentParser()
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.reset()

    def __repr__(
            self: Self,
        ) -> str:
        # representation of self
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

    def _get_init_methods(
            self: Self,
        ) -> list[str]:
        # get _init  methods in order of depth
        init_methods = []
        for current_class in self._get_classes():
            for method in sorted(current_class.__dict__):
                if method.startswith('_init'):
                    init_methods.append(method)
        return init_methods

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

    def _set_bounds(
            self: Self,
            left: float = None,
            right: float = None,
            bottom: float = None,
            top: float = None,
        ) -> Self:
        # sets the bounds of the figure
        for key in ['left', 'right', 'bottom', 'top']:
            value = locals()[key]
            if value is not None:
                setattr(self, key, value)
        self.xmin = self.left
        self.ymin = self.bottom
        figratio = self.figsize[1]/self.figsize[0]
        if self.top is None and self.right is None:
            self.xmax = self.xmin + 1
            self.ymax = self.ymin + figratio
        elif self.top is None:
            self.xmax = self.right
            self.ymax = self.ymin + (self.xmax - self.xmin)*figratio
        elif self.right is None:
            self.ymax = self.top
            self.xmax = self.xmin + (self.ymax - self.ymin)/figratio
        else:
            self.xmax = self.right
            self.ymax = self.top
        return self

    '''
    static methods
    '''

    @staticmethod
    def _time_to_string(
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
    def cmap(
            colour: Any,
        ) -> Colormap:
        # creates a cmap based on the colour
        if isinstance(colour, str):
            return colormaps[colour]
        else:
            return LinearSegmentedColormap.from_list(
                'pybean cmap',
                colour,
            )

    @staticmethod
    def cscale(
            colour: str = 'grey',
            start_with: str = 'white',
            end_with: str = 'black',
        ) -> Colormap:
        # creates a cmap scaling around a given colour
        colour_list = [colour]
        if not isinstance(start_with, str) or start_with != 'same':
            colour_list = [start_with] + colour_list
        if not isinstance(start_with, str) or end_with != 'same':
            colour_list = colour_list + [end_with]
        if len(colour_list) == 1:
            colour_list = colour_list*2
        return LinearSegmentedColormap.from_list(
            'pybean cscale',
            colour_list,
        )

    @staticmethod
    def double(
            double: Any = None,
        ) -> (Any, Any):
        # transforms an input into two values
        if double is None:
            return None, None
        elif not hasattr(double, '__len__'):
            return double, double
        elif len(double) < 2:
            return double, double
        else:
            return double[:2]

    @staticmethod
    def greyscale(
            start_with_white: bool = True,
        ) -> Colormap:
        # creates a grayscale from white to black or the other way around
        if start_with_white:
            colour_list = ['white', 'black']
        else:
            colour_list = ['black', 'white']
        return LinearSegmentedColormap.from_list(
            'pybean greyscale',
            colour_list,
        )

    @staticmethod
    def hsl(
            hue: float = 0.3528,
            saturation: float = 0.5,
            lightness: float = 0.5,
        ) -> (float, float, float):
        # creates a rgb colour from HSV values
        return hls_to_rgb(hue, lightness, saturation)

    @staticmethod
    def path(
            file: str = None,
        ) -> str:
        # returns the absolute path to the file
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

    def add_arg(
            self: Self,
            *args,
            **kwargs,
        ) -> Self:
        # adds a parameter to the parser
        self._parser.add_argument(*args, **kwargs)
        return self

    def check_key(
            self: Self,
            key: Any = None,
        ) -> (Any, bool):
        # checks whether the key is available from the current class
        return self._key_checker(
            key=key,
            category=self.__class__.__name__.lower(),
        )

    def extent(
            self: Self,
        ) -> (float, float, float, float):
        # returns the extent of the figure
        return (self.xmin, self.xmax, self.ymin, self.ymax)

    def figx(
            self: Self,
            ratio: np.array = 0.5,
        ) -> np.array:
        # returns the horizontal position corresponding to the given ratio
        return self.xmin + ratio*self.width()

    def figxy(
            self: Self,
            ratio: np.array = np.array([0.5, 0.5]),
        ) -> np.array:
        # returns the figure position corresponding to the given ratio
        ratio = np.array(ratio)
        if len(ratio.shape) > 1:
            ratiox, ratioy = ratio.T
            return np.stack([
                self.figx(ratiox),
                self.figy(ratioy),
            ], axis=1)
        else:
            ratiox, ratioy = ratio
            return np.array([
                self.figx(ratiox),
                self.figy(ratioy),
            ])

    def figy(
            self: Self,
            ratio: np.array = 0.5,
        ) -> np.array:
        # returns the vertical position corresponding to the given ratio
        return self.ymin + ratio*self.height()

    def height(
            self: Self,
        ) -> float:
        # returns the height of the figure
        return self.ymax - self.ymin

    def help(
            self: Self,
        ) -> None:
        # prints helpful tips
        doc_page = 'https://www.benoitcorsini.com/files/pybean.pdf'
        github_page = 'https://github.com/BenoitCorsini/PyBean'
        symbol_page = 'https://www.rapidtables.com'
        symbol_page += '/code/text/unicode-characters.html'
        print('Using the PyBean library \u2714')
        print(f'\u279E Take a look at the documentation: {doc_page}')
        print(f'\u279E Take a look at the Github page: {github_page}')
        print(f'\u279E Take a look at common symbols: {symbol_page}')

    def reframe(
            self: Self,
            *args,
            **kwargs,
        ) -> Self:
        # reframes the figure
        self._set_bounds(*args, **kwargs)
        self.ax.set_xlim(self.xmin, self.xmax)
        self.ax.set_ylim(self.ymin, self.ymax)
        return self

    def reset(
            self: Self,
        ) -> Self:
        # resets self using _init_ methods in order of depth
        for method in self._get_init_methods():
            getattr(self, method)()
        return self

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

    def time(
            self: Self,
            start: float = None,
            end: float = None,
        ) -> str:
        # computes the current time, compared to the given start
        if start is None:
            start = self._start
        if end is None:
            end = time()
        return self._time_to_string(end - start)

    def width(
            self: Self,
        ) -> float:
        # returns the width of the figure
        return self.xmax - self.xmin

