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

    '''
    fundamental variables and function
    '''

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
            self.show_copyright()
        self.add_axis()
        self.add_info()
        return self

    '''
    hidden methods
    '''

    def _copyright_path(
            self: Self,
        ) -> Path:
        # gets the path of the copyright
        xshift = self.copyright.get('xshift', 0.5)
        yshift = self.copyright.get('yshift', 0.5)
        xscale = (self.xmax - self.xmin)*self.figsize[1]/self.figsize[0]
        yscale = self.ymax - self.ymin
        xy = (
            self.xmin + xshift*xscale,
            self.ymin + yshift*yscale,
        )
        height = yscale*self.copyright.get('height', 1)
        return self.path_from_string(
            s=self.copyright.get('text', 'PyBean'),
            xy=xy,
            font_properties=self.copyright.get('font_properties', {}),
            anchor=self.copyright.get('anchor', None),
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

    def _decimal_precision(
            self: Self,
            step: float,
        ) -> (bool, bool):
        # returns whether the ticks are integers, with one decimal, or more
        is_integer = step == int(step)
        is_integer = is_integer and self.xmin == int(self.xmin)
        is_integer = is_integer and self.ymin == int(self.ymin)
        single_decimal = 10*step == int(10*step)
        single_decimal = single_decimal and 10*self.xmin == int(10*self.xmin)
        single_decimal = single_decimal and 10*self.ymin == int(10*self.ymin)
        return is_integer, single_decimal

    def _axis_ticks(
            self: Self,
            step: float,
        ) -> None:
        # represents the ticks of the axis
        paths = []
        margin = (1 - self.axis_tick_ratio)*step/self.lines_per_axis/2
        height = self.axis_tick_ratio*step/self.lines_per_axis
        xticks = self._get_ticks(axis='x', step=step)
        yticks = self._get_ticks(axis='y', step=step)
        is_integer, single_decimal = self._decimal_precision(step)
        for tick in xticks[1:]:
            paths.append(self.path_from_string(
                s=self._num_to_string(tick, is_integer, single_decimal),
                xy=(tick - margin, self.ymin + margin),
                anchor='south east',
                height=height,
            ))
        for tick in yticks[1:]:
            paths.append(self.path_from_string(
                s=self._num_to_string(tick, is_integer, single_decimal),
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

    def _scale_transform(
            self: Self,
            transform: Affine2D,
            bbox: Bbox,
            height: float = 1,
        ) -> Affine2D:
        # scales the transform to give the bbox a given height
        xy_ratio = (self.xmax - self.xmin)/(self.ymax - self.ymin)
        figsize_ratio = self.figsize[0]/self.figsize[1]
        transform.scale(height/bbox.size[1])
        transform.scale(xy_ratio/figsize_ratio, 1)
        return transform

    def _copyright_visible(
            self: Self,
            visible: bool,
        ) -> None:
        # makes the copyright visible or not
        if hasattr(self, 'copyright') and self.copyright_on is None:
            self.set_shape(key='_copyright', visible=visible)

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
            for corner in self._corners():
                self.set_shape(key=f'_{corner}_info', visible=visible)

    def _info_text(
            self: Self,
            info: str,
            corner: str = 'top_right',
        ) -> None:
        # modifies the text of the info
        anchor = ''
        if 'top' in corner:
            y = self.ymax - self.info_margin
            anchor += 'north '
        else:
            y = self.ymin + self.info_margin
            anchor += 'south '
        if 'right' in corner:
            x = self.xmax - self.info_margin
            anchor += 'east'
        else:
            x = self.xmin + self.info_margin
            anchor += 'west'
        self.apply_to_shape(
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
            start = getattr(self, axis + 'min')
        if end is None:
            end = getattr(self, axis + 'max')
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
        transform.translate(*Shape.shift_from_anchor(
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
            'top_left',
            'bottom_left',
            'top_right',
        ]

    @staticmethod
    def angle_shift(
            angle: float = 0,
            two_dim: bool = False,
        ) -> np.array:
        # returns a vector for shifting in the angle direction
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
            default_angle: float = 0.
        ) -> float:
        # computes the angle formed by the two positions
        vector = np.array(xy2) - np.array(xy1)
        norm = np.sum(vector**2)**0.5
        if not norm:
            return default_angle
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
        # sets an angle to (lower_bound, lower_bound + 360]
        while angle <= lower_bound:
            angle += 360
        while angle > lower_bound + 360:
            angle -= 360
        return angle

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

    @staticmethod
    def arc_path(
            theta1: float,
            theta2: float,
        ) -> Path:
        # creates an arc path
        return Path.arc(theta1, theta2)

    @staticmethod
    def curve_path(
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
        path = Shape.arc_path(theta1, theta2)
        transform = Affine2D()
        transform.scale(a, b)
        transform.rotate(np.pi*angle/180)
        transform.translate(*xy)
        path = path.transformed(transform)
        return path

    @staticmethod
    def crescent_paths(
            xy: (float, float) = (0, 0),
            radius: float = 1,
            ratio: float = 1,
            theta1: float = 0,
            theta2: float = 360,
            angle: float = 0,
        ) -> Path:
        # creates the two parts of a crescent
        outer = Shape.curve_path(
            xy=xy,
            a=radius,
            theta1=theta1,
            theta2=theta2,
            angle=angle
        )
        inner = Shape.curve_path(
            xy=xy,
            a=radius*(1 - ratio),
            b=radius,
            theta1=theta1,
            theta2=theta2,
            reverse=True,
            angle=angle
        )
        return inner, outer

    @staticmethod
    def merge_curves(
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

    def add_shape(
            self: Self,
            shape_name: str,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.Patch:
        # adds a patch to the class
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
        # adds a path patch from raw path parameters to the class
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
        # adds a path patch to the class
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
        # adds a path patch from a list of paths to the class
        return self.add_path(
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
        # applies a given method to a patch
        if key is None:
            key = f'shape{self._key_index - 1}'
        shape = self._shapes[key]
        getattr(shape, method)(*args, **kwargs)
        return shape

    def set_shape(
            self: Self,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.Patch:
        # sets parameters to a patch
        return self.apply_to_shape('set', key, *args, **kwargs)

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

    def add_copyright(
            self: Self,
        ) -> None:
        # adds a copyright stamp to the canvas
        path = self._copyright_path()
        self.add_shape(
            shape_name='PathPatch',
            key='_copyright',
            path=path,
            visible=self.copyright_on,
            **self.copyright.get('params', {})
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
        xticks = self._get_ticks(
            axis='x',
            start=left,
            end=right,
            step=steps[0],
            n_line=n_lines[0],
        )
        yticks = self._get_ticks(
            axis='y',
            start=bottom,
            end=top,
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
        # makes the axis visible
        self._axis_visible(True)

    def hide_axis(
            self: Self,
        ) -> None:
        # makes the axis invisible
        self._axis_visible(False)

    def add_info(
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

    def show_info(
            self: Self,
            top_right_info: str = None,
            bottom_left_info: str = None,
            top_left_info: str = None,
            bottom_right_info: str = None,
        ) -> None:
        # makes the info visible and possibly update the text
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

    '''
    main method
    '''

    def main(
            self: Self,
        ) -> None:
        # the main running function
        pass