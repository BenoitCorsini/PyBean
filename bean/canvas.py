import argparse
import os
import os.path as osp
import matplotlib.figure as figure
from matplotlib.colors import LinearSegmentedColormap as LSC
from time import time
from typing_extensions import Self

from .default import DEFAULT


canvas_params = {
    'figsize' : int,
    'dpi' : int,
    'xmin' : float,
    'xmax' : float,
    'ymin' : float,
    'ymax' : float,
}
canvas_nargs = {
    'figsize' : 2,
}


class Canvas(object):

    def __init__(
            self: Self,
            **kwargs,
        ) -> None:
        # initiate class
        for key, value in DEFAULT.items():
            setattr(self, key, value)
        self._parser = argparse.ArgumentParser()
        self._canvas_params(**kwargs)
        self._new_canvas()

    def _canvas_params(
            self: Self,
            **kwargs,
        ) -> None:
        # collect and setup the parameters of a canvas
        for param, param_type in canvas_params.items():
            assert hasattr(self, param)
            self.add_param(
                f'--{param}',
                nargs=canvas_nargs.get(param, None),
                type=param_type,
                default=getattr(self, param),
            )
        kwargs.update(self.get_kwargs())
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_param(
            self: Self,
            *args,
            **kwargs,
        ) -> None:
        # add a parameter to the parser
        self._parser.add_argument(*args, **kwargs)

    def get_kwargs(
            self: Self,
        ) -> dict:
        # return the arguments of the parser as a dictionnary
        return vars(self._parser.parse_args())

    def _new_canvas(
            self: Self,
        ) -> Self:
        # new canvas instance
        self.start_time = time()
        return self.canvas()

    def _get_new_methods(
            self: Self,
        ) -> list[str]:
        # get _new methods in order of depth
        new_methods = []
        classes = [self.__class__]
        while classes:
            current_class = classes.pop()
            for method in sorted(current_class.__dict__, reverse=True):
                if method.startswith('_new'):
                    new_methods.append(method)
            classes += list(current_class.__bases__)
        return new_methods[::-1]

    def reset(
            self: Self,
        ) -> Self:
        # reset self using _new methods in order of depth
        for method in self._get_new_methods():
            getattr(self, method)()
        return self

    def canvas(
            self: Self,
        ) -> Self:
        # create a figure and axes, used as canvas
        self.fig = figure.Figure(figsize=self.figsize, dpi=self.dpi)
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.ax = self.fig.add_subplot()
        self.ax.set_xlim(self.xmin, self.xmax)
        self.ax.set_ylim(self.ymin, self.ymax)
        self.ax.set_axis_off()
        return self

    def __str__(
            self: Self,
        ) -> str:
        # string representation of self
        s = f'PyBean {self.__class__.__name__}'
        s += f' (figsize=({self.figsize[0]}, {self.figsize[1]}),'
        s += f' dpi={self.dpi})'
        if hasattr(self, 'copyright'):
            if 'text' in self.copyright:
                s += '\nCopyright: '
                s += self.copyright['text']
        return s

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
    def time_to_string(
            time: float,
        ) -> str:
        # transform a time in (hours, minutes, seconds) string format
        hours = int(time/3600)
        minutes = int((time - 60*hours)/60)
        seconds = int(time - 3600*hours - 60*minutes)
        if hours:
            return f'{hours}h{minutes}m{seconds}s'
        elif minutes:
            return f'{minutes}m{seconds}s'
        else:
            return f'{seconds}s'

    def time(
            self: Self,
        ) -> str:
        # compute the current time duration of the algorithm
        return self.time_to_string(time() - self.start_time)

    def help(
            self: Self,
        ) -> None:
        # print helpful tips
        doc_page = 'www.benoitcorsini.com'
        github_page = 'https://github.com/BenoitCorsini/PyBean'
        symbol_page = 'https://www.rapidtables.com'
        symbol_page += '/code/text/unicode-characters.html'
        print('Using the PyBean library \u2714')
        print(f'\u279E Take a look at the documentation: {doc_page}')
        print(f'\u279E Take a look at the Github page: {github_page}')
        print(f'\u279E Take a look at common symbol codes: {symbol_page}')

    def main(
            self: Self,
        ) -> None:
        # the main testing function
        print(self)
        self.save()
        print(self._get_new_methods())
        self.reset()
        cmap = self.get_cscale()
        print(cmap == Canvas.get_cscale())
        self.help()
        print(self.time())