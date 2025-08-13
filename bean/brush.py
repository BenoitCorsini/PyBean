import os.path as osp
import numpy as np
import matplotlib.pyplot as plt
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
    copyright_on = None
    axis_on = None
    info_on = None

    copyright_height = 0.07
    copyright_shift = 0.02
    copyright_anchor = 'south west'
    copyright_fp = {
        'fname' : Canvas.path('copyright.otf'),
    }
    copyright_params = {
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
        'copyright_on' : bool,
        'axis_on' : bool,
        'info_on' : bool,
    }

    def _init_brush(
            self: Self,
        ) -> Self:
        # new brush instance
        self._brushs = {}
        self._brush_index = 0
        self._new_copyright()
        self._new_axis()
        self._new_info()
        return self

    '''
    hidden methods
    '''

    def _new_axis(
            self: Self,
        ) -> None:
        # represents the axis along with the coordinates
        step = max(self.height(), self.width())/max(self.figsize)
        self._axis_grid(step)
        self._axis_ticks(step)

    def _new_copyright(
            self: Self,
        ) -> None:
        # adds a copyright stamp to the canvas
        self.new_brush(
            brush_name='PathPatch',
            key='_copyright',
            path=self._copyright_path(),
            visible=self.copyright_on,
            **self.copyright_params
        )

    def _new_info(
            self: Self,
        ) -> None:
        # represents the desired info
        for corner in self._corners():
            self.new_path(
                path=Path([(0, 0)]),
                key=f'_{corner}_info',
                visible=self.info_on,
                **self.info_params
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
            paths.append(self.string_to_path(
                s=self._num_to_string(tick, is_integer, single_decimal),
                xy=(tick - margin, self.ymin + margin),
                anchor='south east',
                height=height,
            ))
        for tick in yticks[1:]:
            paths.append(self.string_to_path(
                s=self._num_to_string(tick, is_integer, single_decimal),
                xy=(self.xmin + margin, tick - margin),
                anchor='north west',
                height=height,
            ))
        self.new_path_from_list(
            paths=paths,
            key='_ticks',
            visible=self.axis_on,
            **getattr(self, 'axis_params', {})
        )

    def _axis_visible(
            self: Self,
            visible: bool,
        ) -> None:
        # makes the axis visible or not
        if self.axis_on is None:
            for key in ['_axis', '_subaxis', '_ticks']:
                self.set(key=key, visible=visible)

    def _copyright_path(
            self: Self,
        ) -> Path:
        # gets the path of the copyright
        xy = self.double(self.copyright_shift)
        xy = self.figxy(xy*np.array([1, self.figsize[1]/self.figsize[0]]))
        return self.string_to_path(
            s=self.copyright,
            xy=xy,
            font_properties=self.copyright_fp,
            anchor=self.copyright_anchor,
            height=self.height()*self.copyright_height,
        )

    def _copyright_visible(
            self: Self,
            visible: bool,
        ) -> None:
        # makes the copyright visible or not
        if hasattr(self, 'copyright') and self.copyright_on is None:
            self.set(key='_copyright', visible=visible)

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
        self.apply(
            key=f'_{corner}_info',
            method='set_path',
            path=self.string_to_path(
                s=info,
                xy=(x, y),
                height=self.info_height,
                anchor=anchor,
            )
        )

    def _info_visible(
            self: Self,
            visible: bool,
        ) -> None:
        # makes the info visible or not
        if self.info_on is None:
            for corner in self._corners():
                self.set(key=f'_{corner}_info', visible=visible)

    def _scale_transform(
            self: Self,
            transform: Affine2D,
            bbox: Bbox,
            height: float = 1,
        ) -> Affine2D:
        # scales the transform to give the bbox a given height
        xy_ratio = self.width()/self.height()
        figsize_ratio = self.figsize[0]/self.figsize[1]
        transform.scale(height/bbox.size[1])
        transform.scale(xy_ratio/figsize_ratio, 1)
        return transform

    '''
    static methods
    '''

    # @staticmethod
    # def _arc_path(
    #         theta1: float = 0,
    #         theta2: float = 360,
    #     ) -> Path:
    #     # creates an arc path
    #     return Path.arc(theta1, theta2)

    # @staticmethod
    # def _curve_path(
    #         xy: (float, float) = (0, 0),
    #         a: float = 1,
    #         b: float = None,
    #         theta1: float = 0,
    #         theta2: float = 360,
    #         reverse: bool = False,
    #         angle: float = 0,
    #     ) -> Path:
    #     # creates a partial ellipse
    #     if b is None:
    #         b = a
    #     if reverse:
    #         theta1, theta2 = 180 - theta2, 180 - theta1
    #         a *= -1
    #     path = Brush._arc_path(theta1, theta2)
    #     transform = Affine2D()
    #     transform.scale(a, b)
    #     transform.rotate(np.pi*angle/180)
    #     transform.translate(*xy)
    #     return path.transformed(transform)

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

    # @staticmethod
    # def _crescent_paths(
    #         xy: (float, float) = (0, 0),
    #         radius: float = 1,
    #         ratio: float = 1,
    #         theta1: float = 0,
    #         theta2: float = 360,
    #         angle: float = 0,
    #     ) -> Path:
    #     # creates the two parts of a crescent
    #     outer = Brush._curve_path(
    #         xy=xy,
    #         a=radius,
    #         theta1=theta1,
    #         theta2=theta2,
    #         angle=angle,
    #     )
    #     inner = Brush._curve_path(
    #         xy=xy,
    #         a=radius*(1 - ratio),
    #         b=radius,
    #         theta1=theta1,
    #         theta2=theta2,
    #         angle=angle,
    #         reverse=True,
    #     )
    #     return inner, outer

    # @staticmethod
    # def _merge_curves(
    #         *curves,
    #     ) -> Path:
    #     # combines multiple curves
    #     vertices = [curve.vertices for curve in curves]
    #     vertices = np.concatenate(vertices)
    #     codes = [curve.codes + (curve.codes == 1) for curve in curves]
    #     codes = np.concatenate(codes)
    #     codes[0] = 1
    #     return Path(vertices=vertices, codes=codes, closed=True)

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
    def _shift_transform(
            transform: Affine2D,
            bbox: Bbox,
            anchor: str = None,
        ) -> Affine2D:
        # shifts the transform to move the bbox according to the anchor
        transform.translate(*(-(bbox.size/2 + bbox.p0)))
        transform.translate(*Brush._shift_from_anchor(
            bbox=bbox,
            anchor=anchor,
        ))
        return transform

    @staticmethod
    def _ticks_to_grid_path(
            xticks: np.array,
            yticks: np.array,
        ) -> Path:
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
    def image_to_matrix(
            file: str,
        ) -> np.array:
        # loads an image as a matrix
        return plt.imread(file)

    '''
    general methods
    '''

    def apply(
            self: Self,
            method: str,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.Patch:
        # applies a given method to a patch
        if key is None:
            key = f'brush{self._brush_index - 1}'
        brush = self._brushs[key]
        getattr(brush, method)(*args, **kwargs)
        return brush

    def grid(
            self: Self,
            key: Any = None,
            left: float = None,
            right: float = None,
            bottom: float = None,
            top: float = None,
            steps: tuple[float] = None,
            blocks: tuple[int] = 1,
            *args,
            **kwargs,
        ) -> patches.PathPatch:
        # creates a grid
        steps = self.double(steps)
        blocks = self.double(blocks)
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
        return self.new_path(
            key=key,
            path=self._ticks_to_grid_path(xticks, yticks),
            *args,
            **kwargs,
        )

    def hide_axis(
            self: Self,
        ) -> None:
        # makes the axis invisible
        self._axis_visible(False)

    def hide_copyright(
            self: Self,
        ) -> None:
        # makes the copyright invisible
        self._copyright_visible(False)

    def hide_info(
            self: Self,
        ) -> None:
        # makes the info visible
        self._info_visible(False)

    def new_brush(
            self: Self,
            brush_name: str,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.Patch:
        # adds a patch to the class
        key, available = self.check_key(key)
        if available:
            brush = self.ax.add_patch(
                getattr(patches, brush_name)(*args, **kwargs)
            )
            self._brushs[key] = brush
        else:
            brush = self._brushs[key]
        return brush

    def new_image(
            self: Self,
            file: str,
            *args,
            **kwargs,
        ) -> patches.Patch:
        # adds an image to the class
        return self.new_image_from_matrix(
            self.image_to_matrix(file),
            *args,
            **kwargs,
        )

    def new_image_from_matrix(
            self: Self,
            matrix: np.array,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.Patch:
        # adds an image from a matrix to the class
        key, available = self.check_key(key)
        if available:
            brush = self.ax.imshow(matrix, *args, **kwargs)
            self._brushs[key] = brush
        else:
            brush = self._brushs[key]
        return brush

    def new_path(
            self: Self,
            path: Path,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.PathPatch:
        # adds a path patch to the class
        return self.new_brush(
            brush_name='PathPatch',
            key=key,
            path=path,
            *args,
            **kwargs,
        )

    def new_path_from_list(
            self: Self,
            paths: list[Path],
            *args,
            **kwargs,
        ) -> patches.PathPatch:
        # adds a path patch from a list of paths to the class
        return self.new_path(
            path=Path.make_compound_path(*paths),
            *args,
            **kwargs,
        )

    def new_path_from_raw(
            self: Self,
            vertices: list = [(0, 0)],
            codes: list = None,
            closed: bool = False,
            *args,
            **kwargs,
        ) -> patches.PathPatch:
        # adds a path patch from raw path parameters to the class
        return self.new_path(
            path=Path(
                vertices=vertices,
                codes=codes,
                closed=closed,
            ),
            *args,
            **kwargs,
        )

    def set(
            self: Self,
            key: Any = None,
            *args,
            **kwargs,
        ) -> patches.Patch:
        # sets parameters to a patch
        return self.apply('set', key, *args, **kwargs)

    def show_axis(
            self: Self,
        ) -> None:
        # makes the axis visible
        self._axis_visible(True)

    def show_copyright(
            self: Self,
        ) -> None:
        # makes the copyright visible
        self._copyright_visible(True)

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

    def string_to_path(
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
            xy=(0, 0),
            s=s,
            size=size,
            prop=FontProperties(**font_properties),
        )
        bbox = path.get_extents()
        transform = Affine2D()
        self._shift_transform(transform, bbox, anchor)
        if height is not None:
            self._scale_transform(transform, bbox, height)
        transform.translate(*xy)
        path = path.transformed(transform)
        return path

