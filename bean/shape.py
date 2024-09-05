import os.path as osp
import numpy as np
import matplotlib.patches as patches
from matplotlib.path import Path
from matplotlib.font_manager import FontProperties
from matplotlib.text import TextPath
from matplotlib.transforms import Affine2D, Bbox
from typing_extensions import Any, Self

from .canvas import Canvas


class Shape(Canvas):

    _shape_params = {
        'copyright_on' : bool,
        'axis_on' : bool,
        'lines_per_axis' : int,
        'axis_tick_ratio' : float,
        'info_on' : bool,
        'info_margin' : float,
        'info_height' : float,
    }

    def _new_shape(
            self: Self,
        ) -> Self:
        # new shape instance
        self._shapes = {}
        self._shape_index = 0
        if hasattr(self, 'copyright'):
            self.add_copyright()
        return self

    def _copyright_path(
            self: Self,
        ) -> Path:
        # gets the path of the copyright
        margin = self.copyright.get('margin', 0)
        xscale = (self.xmax - self.xmin)*self.figsize[1]/self.figsize[0]
        yscale = self.ymax - self.ymin
        xy = (
            self.xmin + margin*xscale,
            self.ymin + margin*yscale,
        )
        height = yscale*self.copyright.get('height', 1)
        return self.path_from_string(
            s=self.copyright.get('text', 'PyBean'),
            xy=xy,
            font_properties=self.copyright.get('font_properties', {}),
            anchor='south west',
            height=height,
        )

    def _axis_grid(
            self: Self,
            step: float,
        ) -> None:
        # represents the grid of the axis
        self.grid(
            key='_subaxis',
            steps=step/self.lines_per_axis,
            visible=self.axis_on,
            **getattr(self, 'axis_params', {})
        )
        self.grid(
            key='_axis',
            steps=step,
            visible=self.axis_on,
            **getattr(self, 'axis_params', {})
        )

    def _axis_ticks(
            self: Self,
            step: float,
        ) -> None:
        # represents the ticks of the axis
        paths = []
        margin = (1 - self.axis_tick_ratio)*step/self.lines_per_axis/2
        height = self.axis_tick_ratio*step/self.lines_per_axis
        xticks = self.get_ticks(axis='x', step=step)
        yticks = self.get_ticks(axis='y', step=step)
        is_integer = step == int(step)
        is_integer = is_integer and self.xmin == int(self.xmin)
        is_integer = is_integer and self.ymin == int(self.ymin)
        for tick in xticks[1:]:
            paths.append(self.path_from_string(
                s=self._tick_to_string(tick, is_integer),
                xy=(tick - margin, self.ymin + margin),
                anchor='south east',
                height=height,
            ))
        for tick in yticks[1:]:
            paths.append(self.path_from_string(
                s=self._tick_to_string(tick, is_integer),
                xy=(self.xmin + margin, tick - margin),
                anchor='north west',
                height=height,
            ))
        self.add_paths(
            paths=paths,
            key='_ticks',
            visible=self.axis_on,
            **getattr(self, 'axis_params', {})
        )

    def _copyright_visible(
            self: Self,
            visible: bool,
        ) -> None:
        # makes the copyright visible or not
        if hasattr(self, 'copyright') and self.copyright_on is None:
            for key in ['_copyright_fill', '_copyright_line']:
                self.set_shape(key=key, visible=visible)

    def _axis_visible(
            self: Self,
            visible: bool,
        ) -> None:
        # makes the axis visible or not
        if self.axis_on is None:
            for key in ['_axis', '_subaxis', '_ticks']:
                self.set_shape(key=key, visible=visible)

    def _info_visible(
            self: Self,
            visible: bool,
        ) -> None:
        # makes the info visible or not
        if self.info_on is None:
            self.set_shape(key='_info', visible=visible)

    def _info_text(
            self: Self,
            s: str,
        ) -> None:
        # modifies the text of the info
        self.apply_to_shape(
            key='_info',
            method='set_path',
            path=self.path_from_string(
                s=s,
                xy=(
                    self.xmax - self.info_margin,
                    self.ymax - self.info_margin,
                ),
                height=self.info_height,
                anchor='north east',
            )
        )

    @staticmethod
    def _ticks_to_grid_path(
            xticks: np.array,
            yticks: np.array,
        ) -> dict:
        # transform x and y ticks into a grid path
        xmin, xmax = np.min(xticks), np.max(xticks)
        ymin, ymax = np.min(yticks), np.max(yticks)
        vertices = []
        codes = []
        for xtick in xticks:
            vertices.append((xtick, ymin))
            codes.append(1)
            vertices.append((xtick, ymax))
            codes.append(2)
        for ytick in yticks:
            vertices.append((xmin, ytick))
            codes.append(1)
            vertices.append((xmax, ytick))
            codes.append(2)
        return Path(vertices=vertices, codes=codes, closed=False)

    @staticmethod
    def _tick_to_string(
            tick: float,
            is_integer: bool,
        ) -> str:
        # transforms a tick into a string
        if is_integer:
            return f'{tick:0.0f}'
        else:
            return f'{tick:0.2f}'

    def add_shape(
            self: Self,
            shape_name: str,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.Patch:
        # add a patch to the class
        key, available = self.key_checker(key=key, category='shape')
        if available:
            shape = self.ax.add_patch(
                getattr(patches, shape_name)(*args, **kwargs)
            )
            self._shapes[key] = shape
        else:
            shape = self._shapes[key]
        return shape

    def add_raw_path(
            self: Self,
            vertices: list = None,
            codes: list = None,
            closed: bool = False,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.PathPatch:
        # add a path patch from raw path parameters to the class
        return self.add_shape(
            shape_name='PathPatch',
            key=key,
            path=Path(
                vertices=vertices,
                codes=codes,
                closed=closed,
            ),
            *args,
            **kwargs
        )

    def add_path(
            self: Self,
            path: Path,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.PathPatch:
        # add a path patch to the class
        return self.add_shape(
            shape_name='PathPatch',
            key=key,
            path=path,
            *args,
            **kwargs
        )

    def add_paths(
            self: Self,
            paths: list[Path],
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.PathPatch:
        # add a path patch to the class
        return self.add_shape(
            shape_name='PathPatch',
            key=key,
            path=Path.make_compound_path(*paths),
            *args,
            **kwargs
        )

    def apply_to_shape(
            self: Self,
            method: str,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.Patch:
        # apply a given method to a patch
        if key is None:
            key = f'shape{self._key_index - 1}'
        shape = self._shapes[key]
        return getattr(shape, method)(*args, **kwargs)

    def set_shape(
            self: Self,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.Patch:
        # set parameters to a patch
        return self.apply_to_shape('set', key, *args, **kwargs)

    def path_from_string(
            self: Self,
            s: str,
            xy: tuple = (0, 0),
            size: float = None,
            font_properties: dict = {},
            anchor: str = None,
            height: float = None,
        ) -> Path:
        # get the path from a string
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

    def scale_transform(
            self: Self,
            transform: Affine2D,
            bbox: Bbox,
            height: float = 1,
        ) -> Affine2D:
        # scale the transform to straighthen the text with given height
        xy_ratio = (self.xmax - self.xmin)/(self.ymax - self.ymin)
        figsize_ratio = self.figsize[0]/self.figsize[1]
        transform.scale(height/bbox.size[1])
        transform.scale(xy_ratio/figsize_ratio, 1)
        return transform

    def add_copyright(
            self: Self,
        ) -> None:
        # add a copyright stamp to the canvas
        path = self._copyright_path()
        self.add_shape(
            shape_name='PathPatch',
            key='_copyright_fill',
            path=path,
            lw=0,
            color=self.copyright.get('fc', 'black'),
            visible=self.copyright_on,
            **self.copyright.get('params', {})
        )
        self.add_shape(
            shape_name='PathPatch',
            key='_copyright_line',
            path=path,
            lw=self.copyright.get('lw', 0),
            color=self.copyright.get('ec', 'black'),
            fill=False,
            visible=self.copyright_on,
            **self.copyright.get('params', {})
        )

    def show_copyright(
            self: Self,
        ) -> None:
        # make the copyright visible
        self._copyright_visible(True)

    def hide_copyright(
            self: Self,
        ) -> None:
        # make the copyright invisible
        self._copyright_visible(False)

    def get_ticks(
            self: Self,
            axis: str = 'x',
            start: float = None,
            stop: float = None,
            step: float = None,
            n_line: int = None,
        ) -> list[float]:
        # return the ticks given an axis
        if start is None:
            start = getattr(self, axis + 'min')
        if stop is None:
            stop = getattr(self, axis + 'max')
        if step is None:
            if n_line is None:
                n_line = 1
            step = (stop - start)/n_line
        return np.arange(start, stop + step, step)

    def grid(
            self: Self,
            key: Any = None,
            left: float = None,
            right: float = None,
            top: float = None,
            bottom: float = None,
            steps: tuple[float] = None,
            n_lines: tuple[int] = None,
            *args,
            **kwargs,
        ) -> patches.PathPatch:
        # creates a grid
        if steps is None:
            steps = (None, None)
        elif isinstance(steps, float):
            steps = (steps, steps)
        if n_lines is None:
            n_lines = (None, None)
        elif isinstance(n_lines, int):
            n_lines = (n_lines, n_lines)
        xticks = self.get_ticks(
            axis='x',
            start=left,
            stop=right,
            step=steps[0],
            n_line=n_lines[0],
        )
        yticks = self.get_ticks(
            axis='y',
            start=bottom,
            stop=top,
            step=steps[1],
            n_line=n_lines[1],
        )
        return self.add_path(
            key=key,
            path=self._ticks_to_grid_path(xticks, yticks),
            *args,
            **kwargs
        )

    def add_axis(
            self: Self,
        ) -> None:
        # represents the axis along with the coordinates
        step = max(
            (self.xmax - self.xmin),
            (self.ymax - self.ymin),
        )/max(self.figsize)
        self._axis_grid(step)
        self._axis_ticks(step)

    def show_axis(
            self: Self,
        ) -> None:
        # make the axis visible
        self._axis_visible(True)

    def hide_axis(
            self: Self,
        ) -> None:
        # make the axis invisible
        self._axis_visible(False)

    def add_info(
            self: Self,
        ) -> None:
        # represents the desired info
        self.add_path(
            path=Path([(0, 0)]),
            key='_info',
            visible=self.info_on,
            **self.info_params
        )

    def show_info(
            self: Self,
            s: str = None,
        ) -> None:
        # make the info visible and possibly update the text
        self._info_visible(True)
        if s is not None:
            self._info_text(s)

    def hide_info(
            self: Self,
            s: str = None,
        ) -> None:
        # make the info visible and possibly update the text
        self._info_visible(False)
        if s is not None:
            self._info_text(s)

    @staticmethod
    def shift_transform(
            transform: Affine2D,
            bbox: Bbox,
            anchor: str = None,
        ) -> Affine2D:
        # shift the transform to move the bbox according to the anchor
        transform.translate(*(-(bbox.size/2 + bbox.p0)))
        transform.translate(*Shape.shift_from_anchor(
            bbox=bbox,
            anchor=anchor
        ))
        return transform

    @staticmethod
    def shift_from_anchor(
            bbox: Bbox,
            anchor: str = None,
        ) -> np.array:
        # returns a shifting vector moving the bbox according to the anchor
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

    def test(
            self: Self,
        ) -> None:
        # the main testing function
        print(self)
        print(self._get_classes())
        print(self._get_new_methods())
        print(self.get_kwargs())
        self.add_shape(shape_name='Circle', key='test', xy=(0, 1), radius=0.2)
        self.add_shape(shape_name='Circle', xy=(1, 0), radius=0.5)
        self.set_shape(key='test', color='red')
        self.apply_to_shape(key='test', method='set_center', xy=(0.2, 0.5))
        self.add_raw_path(vertices=[(0, 0), (1, 1)], color='green', lw=10)
        self.grid(left=0.5, right=0.6, bottom=0.1, top=0.4, n_lines=(3, 5), color='red', lw=5)
        self.grid(steps=0.1, color='darkblue', zorder=-1)
        self.grid(color='orange', zorder=-2, lw=30)
        self.add_axis()
        self.set_shape(key='_axis', alpha=1)
        self.add_axis()
        self.show_axis()
        self.hide_copyright()
        self.add_info()
        self.show_info(repr(self))
        self.save()
        print(self._shapes)