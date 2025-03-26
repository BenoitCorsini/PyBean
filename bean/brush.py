import inspect
import os.path as osp
import numpy as np
import matplotlib.patches as patches
from matplotlib.path import Path
from matplotlib.font_manager import FontProperties
from matplotlib.text import TextPath
from matplotlib.transforms import Affine2D, Bbox
from typing_extensions import Any, Self

from .canvas import Canvas


class Brush(Canvas):

    '''
    fundamental variables and function
    '''

    copyright = '@pybean'
    cpr_on = None
    axis_on = None
    info_on = None

    cpr_height = 0.07
    cpr_shift = 0.02
    cpr_anchor = 'south west'
    cpr_font_properties = {
        'fname' : osp.join(
            osp.dirname(
                osp.abspath(
                    inspect.getfile(
                        inspect.currentframe()
                    )
                )
            ),
            'copyright.otf'
        ),
    }
    cpr_params = {
        'lw' : 1.2,
        'ec' : 'darkgrey',
        'fc' : 'lightgrey',
        'alpha' : 0.25,
        'zorder' : 100,
        'joinstyle' : 'round',
        'capstyle' : 'round',
    }
    axis_sublines = 5
    axis_tick_ratio = 0.6
    axis_params = {
        'color' : 'black',
        'lw' : 1,
        'alpha' : 0.05,
        'zorder' : 98,
        'joinstyle' : 'round',
        'capstyle' : 'round',
    }
    info_margin = 1e-2
    info_height = 2e-2
    info_params = {
        'color' : 'black',
        'lw' : 1,
        'alpha' : 0.5,
        'zorder' : 99,
        'joinstyle' : 'round',
        'capstyle' : 'round',
    }

    _brush_params = {
        'copyright' : str,
        'cpr_on' : bool,
        'axis_on' : bool,
        'info_on' : bool,
    }

    def _new_brush(
            self: Self,
        ) -> Self:
        # new brush instance
        self._brushs = {}
        self._brush_index = 0
        self._add_copyright()
        self._add_axis()
        self._add_info()
        return self

    '''
    hidden methods
    '''

    def _copyright_path(
            self: Self,
        ) -> Path:
        # gets the path of the copyright
        if hasattr(self.cpr_shift, '__len__'):
            xshift = self.cpr_shift[0]
            yshift = self.cpr_shift[1]
        else:
            xshift = self.cpr_shift
            yshift = self.cpr_shift
        xscale = (
            self._get_bound('xmax') - self._get_bound('xmin')
        )*self.figsize[1]/self.figsize[0]
        yscale = self._get_bound('ymax') - self._get_bound('ymin')
        xy = (
            self._get_bound('xmin') + xshift*xscale,
            self._get_bound('ymin') + yshift*yscale,
        )
        height = yscale*self.cpr_height
        return self.path_from_string(
            s=self.copyright,
            xy=xy,
            font_properties=self.cpr_font_properties,
            anchor=self.cpr_anchor,
            height=height,
        )

    def _axis_grid(
            self: Self,
            step: float,
        ) -> None:
        # represents the grid of the axis
        self.grid(
            key='_subaxis',
            steps=step/self.axis_sublines,
            visible=self.axis_on,
            **getattr(self, 'axis_params', {})
        )
        self.grid(
            key='_axis',
            steps=step,
            visible=self.axis_on,
            **getattr(self, 'axis_params', {})
        )

    def _decimal_precision(
            self: Self,
            step: float,
        ) -> (bool, bool):
        # returns whether the ticks are integers, with one decimal, or more
        is_integer = step == int(step)
        is_integer = is_integer and self._get_bound('xmin') == int(self._get_bound('xmin'))
        is_integer = is_integer and self._get_bound('ymin') == int(self._get_bound('ymin'))
        single_decimal = 10*step == int(10*step)
        single_decimal = single_decimal and 10*self._get_bound('xmin') == int(10*self._get_bound('xmin'))
        single_decimal = single_decimal and 10*self._get_bound('ymin') == int(10*self._get_bound('ymin'))
        return is_integer, single_decimal

    def _axis_ticks(
            self: Self,
            step: float,
        ) -> None:
        # represents the ticks of the axis
        paths = []
        margin = (1 - self.axis_tick_ratio)*step/self.axis_sublines/2
        height = self.axis_tick_ratio*step/self.axis_sublines
        xticks = self._get_ticks(axis='x', step=step)
        yticks = self._get_ticks(axis='y', step=step)
        is_integer, single_decimal = self._decimal_precision(step)
        for tick in xticks[1:]:
            paths.append(self.path_from_string(
                s=self._num_to_string(tick, is_integer, single_decimal),
                xy=(tick - margin, self._get_bound('ymin') + margin),
                anchor='south east',
                height=height,
            ))
        for tick in yticks[1:]:
            paths.append(self.path_from_string(
                s=self._num_to_string(tick, is_integer, single_decimal),
                xy=(self._get_bound('xmin') + margin, tick - margin),
                anchor='north west',
                height=height,
            ))
        self.add_paths(
            paths=paths,
            key='_ticks',
            visible=self.axis_on,
            **getattr(self, 'axis_params', {})
        )

    def _scale_transform(
            self: Self,
            transform: Affine2D,
            bbox: Bbox,
            height: float = 1,
        ) -> Affine2D:
        # scales the transform to give the bbox a given height
        xy_ratio = (self._get_bound('xmax') - self._get_bound('xmin'))/(self._get_bound('ymax') - self._get_bound('ymin'))
        figsize_ratio = self.figsize[0]/self.figsize[1]
        transform.scale(height/bbox.size[1])
        transform.scale(xy_ratio/figsize_ratio, 1)
        return transform

    def _add_copyright(
            self: Self,
        ) -> None:
        # adds a copyright stamp to the canvas
        path = self._copyright_path()
        self.add_brush(
            brush_name='PathPatch',
            key='_copyright',
            path=path,
            visible=self.cpr_on,
            **self.cpr_params
        )

    def _copyright_visible(
            self: Self,
            visible: bool,
        ) -> None:
        # makes the copyright visible or not
        if hasattr(self, 'copyright') and self.cpr_on is None:
            self.set_brush(key='_copyright', visible=visible)

    def _add_axis(
            self: Self,
        ) -> None:
        # represents the axis along with the coordinates
        step = max(
            (self._get_bound('xmax') - self._get_bound('xmin')),
            (self._get_bound('ymax') - self._get_bound('ymin')),
        )/max(self.figsize)
        self._axis_grid(step)
        self._axis_ticks(step)

    def _axis_visible(
            self: Self,
            visible: bool,
        ) -> None:
        # makes the axis visible or not
        if self.axis_on is None:
            for key in ['_axis', '_subaxis', '_ticks']:
                self.set_brush(key=key, visible=visible)

    def _add_info(
            self: Self,
        ) -> None:
        # represents the desired info
        for corner in self._corners():
            self.add_path(
                path=Path([(0, 0)]),
                key=f'_{corner}_info',
                visible=self.info_on,
                **self.info_params
            )

    def _info_visible(
            self: Self,
            visible: bool,
        ) -> None:
        # makes the info visible or not
        if self.info_on is None:
            for corner in self._corners():
                self.set_brush(key=f'_{corner}_info', visible=visible)

    def _info_text(
            self: Self,
            info: str,
            corner: str = 'top_right',
        ) -> None:
        # modifies the text of the info
        anchor = ''
        if 'top' in corner:
            y = self._get_bound('ymax') - self.info_margin
            anchor += 'north '
        else:
            y = self._get_bound('ymin') + self.info_margin
            anchor += 'south '
        if 'right' in corner:
            x = self._get_bound('xmax') - self.info_margin
            anchor += 'east'
        else:
            x = self._get_bound('xmin') + self.info_margin
            anchor += 'west'
        self.apply_to_brush(
            key=f'_{corner}_info',
            method='set_path',
            path=self.path_from_string(
                s=info,
                xy=(x, y),
                height=self.info_height,
                anchor=anchor,
            )
        )

    def _get_ticks(
            self: Self,
            axis: str = 'x',
            start: float = None,
            end: float = None,
            step: float = None,
            n_line: int = 1,
        ) -> list[float]:
        # returns the ticks given an axis
        if start is None:
            start = self._get_bound(axis + 'min')
        if end is None:
            end = self._get_bound(axis + 'max')
        if step is None:
            step = (end - start)/n_line
        return np.arange(start, end + step, step)

    '''
    static methods
    '''

    @staticmethod
    def _ticks_to_grid_path(
            xticks: np.array,
            yticks: np.array,
        ) -> dict:
        # transforms x and y ticks into a grid path
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
    def _num_to_string(
            tick: float,
            is_integer: bool,
            single_decimal: bool,
        ) -> str:
        # transforms a tick into a string
        if is_integer:
            return f'{tick:0.0f}'
        elif single_decimal:
            return f'{tick:0.1f}'
        else:
            return f'{tick:0.2f}'

    @staticmethod
    def _shift_transform(
            transform: Affine2D,
            bbox: Bbox,
            anchor: str = None,
        ) -> Affine2D:
        # shifts the transform to move the bbox according to the anchor
        transform.translate(*(-(bbox.size/2 + bbox.p0)))
        transform.translate(*Brush._shift_from_anchor(
            bbox=bbox,
            anchor=anchor
        ))
        return transform

    @staticmethod
    def _corners(
        ) -> list[str]:
        # returns a list of corners in inverse order of importance
        return [
            'bottom_right',
            'bottom_left',
            'top_right',
            'top_left',
        ]

    @staticmethod
    def _shift_from_anchor(
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
                Brush._shift_from_anchor(bbox, anchor) for anchor in anchors
            ]
            return np.sum(shifts, axis=0)
        else:
            return np.array([0, 0])

    @staticmethod
    def _arc_path(
            theta1: float = 0,
            theta2: float = 360,
        ) -> Path:
        # creates an arc path
        return Path.arc(theta1, theta2)

    @staticmethod
    def _curve_path(
            xy: (float, float) = (0, 0),
            a: float = 1,
            b: float = None,
            theta1: float = 0,
            theta2: float = 360,
            reverse: bool = False,
            angle: float = 0,
        ) -> Path:
        # creates a partial ellipse
        if b is None:
            b = a
        if reverse:
            theta1, theta2 = 180 - theta2, 180 - theta1
            a *= -1
        path = Brush._arc_path(theta1, theta2)
        transform = Affine2D()
        transform.scale(a, b)
        transform.rotate(np.pi*angle/180)
        transform.translate(*xy)
        path = path.transformed(transform)
        return path

    @staticmethod
    def _crescent_paths(
            xy: (float, float) = (0, 0),
            radius: float = 1,
            ratio: float = 1,
            theta1: float = 0,
            theta2: float = 360,
            angle: float = 0,
        ) -> Path:
        # creates the two parts of a crescent
        outer = Brush._curve_path(
            xy=xy,
            a=radius,
            theta1=theta1,
            theta2=theta2,
            angle=angle,
        )
        inner = Brush._curve_path(
            xy=xy,
            a=radius*(1 - ratio),
            b=radius,
            theta1=theta1,
            theta2=theta2,
            reverse=True,
            angle=angle,
        )
        return inner, outer

    @staticmethod
    def _merge_curves(
            *curves
        ) -> Path:
        # combines multiple curves
        vertices = [curve.vertices for curve in curves]
        vertices = np.concatenate(vertices)
        codes = [curve.codes + (curve.codes == 1) for curve in curves]
        codes = np.concatenate(codes)
        codes[0] = 1
        return Path(vertices=vertices, codes=codes, closed=True)

    '''
    general methods
    '''

    def add_brush(
            self: Self,
            brush_name: str,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.Patch:
        # adds a patch to the class
        key, available = self._key_checker(key=key, category='brush')
        if available:
            brush = self.ax.add_patch(
                getattr(patches, brush_name)(*args, **kwargs)
            )
            self._brushs[key] = brush
        else:
            brush = self._brushs[key]
        return brush

    def add_path(
            self: Self,
            path: Path,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.PathPatch:
        # adds a path patch to the class
        return self.add_brush(
            brush_name='PathPatch',
            key=key,
            path=path,
            *args,
            **kwargs
        )

    def add_raw_path(
            self: Self,
            vertices: list,
            codes: list = None,
            closed: bool = False,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.PathPatch:
        # adds a path patch from raw path parameters to the class
        return self.add_path(
            key=key,
            path=Path(
                vertices=vertices,
                codes=codes,
                closed=closed,
            ),
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
        # adds a path patch from a list of paths to the class
        return self.add_path(
            key=key,
            path=Path.make_compound_path(*paths),
            *args,
            **kwargs
        )

    def apply_to_brush(
            self: Self,
            method: str,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.Patch:
        # applies a given method to a patch
        if key is None:
            key = f'brush{self._key_index - 1}'
        brush = self._brushs[key]
        getattr(brush, method)(*args, **kwargs)
        return brush

    def set_brush(
            self: Self,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.Patch:
        # sets parameters to a patch
        return self.apply_to_brush('set', key, *args, **kwargs)

    def path_from_string(
            self: Self,
            s: str,
            xy: (float, float) = (0, 0),
            size: float = None,
            font_properties: dict = {},
            anchor: str = None,
            height: float = None,
        ) -> Path:
        # gets the path from a string
        path = TextPath(
            xy=xy,
            s=s,
            size=size,
            prop=FontProperties(**font_properties)
        )
        if height is not None:
            bbox = path.get_extents()
            transform = Affine2D()
            self._shift_transform(transform, bbox, anchor)
            self._scale_transform(transform, bbox, height)
            transform.translate(*xy)
            path = path.transformed(transform)
        return path

    def grid(
            self: Self,
            key: Any = None,
            left: float = None,
            right: float = None,
            top: float = None,
            bottom: float = None,
            steps: tuple[float] = None,
            blocks: tuple[int] = 1,
            *args,
            **kwargs,
        ) -> patches.PathPatch:
        # creates a grid
        if steps is None:
            steps = (None, None)
        elif isinstance(steps, float) or isinstance(steps, int):
            steps = (steps, steps)
        if blocks is None:
            blocks = (None, None)
        elif isinstance(blocks, int):
            blocks = (blocks, blocks)
        xticks = self._get_ticks(
            axis='x',
            start=left,
            end=right,
            step=steps[0],
            n_line=blocks[0],
        )
        yticks = self._get_ticks(
            axis='y',
            start=bottom,
            end=top,
            step=steps[1],
            n_line=blocks[1],
        )
        return self.add_path(
            key=key,
            path=self._ticks_to_grid_path(xticks, yticks),
            *args,
            **kwargs
        )

    def show_copyright(
            self: Self,
        ) -> None:
        # makes the copyright visible
        self._copyright_visible(True)

    def hide_copyright(
            self: Self,
        ) -> None:
        # makes the copyright invisible
        self._copyright_visible(False)

    def show_axis(
            self: Self,
        ) -> None:
        # makes the axis visible
        self._axis_visible(True)

    def hide_axis(
            self: Self,
        ) -> None:
        # makes the axis invisible
        self._axis_visible(False)

    def show_info(
            self: Self,
            top_left_info: str = None,
            top_right_info: str = None,
            bottom_left_info: str = None,
            bottom_right_info: str = None,
        ) -> None:
        # makes the info visible and possibly update the text
        if self.info_on is not False:
            self._info_visible(True)
            for corner in self._corners():
                info = locals()[f'{corner}_info']
                if info is not None:
                    self._info_text(info, corner)

    def hide_info(
            self: Self,
        ) -> None:
        # makes the info visible
        self._info_visible(False)