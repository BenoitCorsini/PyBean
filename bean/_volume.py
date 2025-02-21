import numpy as np
from typing_extensions import Any, Self

from .shape import Shape


'''
Any subsequent volume-based class needs the following functions:
    _create_{volume name}
    _update_{volume name}
    new_{volume name}
The latter function being preferably placed in the main Volume class.
'''


class _Volume(Shape):

    '''
    fundamental variables and function
    '''

    _volume_params = {
        'draft' : bool,
        'scale' : float,
        'view_pos' : float,
        'view_angle' : float,
        'screen_dist' : float,
        'horizon_angle' : float,
        'depth_scale' : float,
        'depth_shift' : float,
        'side_scale' : float,
        'shade_angle' : float,
        'altitude_to_shade' : float,
        'shade_cmap_ratio' : float,
    }

    _canvas_nargs = {
        'view_pos' : 3,
    }

    def _new_volume(
            self: Self,
        ) -> Self:
        # new volume instance
        self.view_pos = np.array(self.view_pos)
        self.screen_xdir = np.array([1, 0, 0]),
        self.screen_ydir = np.array([
            0,
            -np.sin(self.view_angle*np.pi/180),
            np.cos(self.view_angle*np.pi/180),
        ])
        self.screen_zdir = np.array([
            0,
            np.cos(self.view_angle*np.pi/180),
            np.sin(self.view_angle*np.pi/180),
        ])
        self._volumes = {}
        self._volume_index = 0
        self._depth_exponent = 1 - np.tan(self.horizon_angle*np.pi/180)
        self.add_axis()
        self.add_info()
        if self.draft:
            self.hide_copyright()
            self.show_axis()
            self.show_info(repr(self))
        else:
            self.show_copyright()
            self.hide_axis()
            self.hide_info()
        return self

    '''
    hidden methods
    '''

    def _shade_shift(
            self: Self,
            two_dim: bool = False,
        ) -> np.array:
        # returns a vector for shade shifting
        return self.angle_shift(
            angle=self.shade_angle - 90,
            two_dim=two_dim,
        )

    def _normalize_pos(
            self: Self,
            pos: tuple[float],
            height: float = 0,
        ) -> np.array:
        # normalize a position into a triplet
        if '__len__' not in dir(pos):
            raise ValueError(f'Position is not a tuple: {pos}')
        elif len(pos) == 2:
            pos = pos[0], pos[1], 0
        elif len(pos) != 3:
            raise ValueError(f'Position with a wrong length: {pos}')
        return (np.array(pos) + np.array([0, 0, height]))*self.scale

    def _project_to_screen(
            self: Self,
            pos: tuple[float],
            height: float = 0,
        ) -> np.array:
        # project a position relative to the viewer and the screen
        relative_pos = self._normalize_pos(pos, height) - self.view_pos
        return (
            np.sum(relative_pos*self.screen_xdir),
            np.sum(relative_pos*self.screen_ydir),
            np.sum(relative_pos*self.screen_zdir),
        )

    def _normalize_xy(
            self: Self,
            x: float,
            y: float,
        ) -> np.array:
        # normalize an xy coordinate into the frame
        return (
            self.xmin + (self.xmax - self.xmin)*(0.5 + x),
            (self.ymin + self.ymax)/2 + (self.xmax - self.xmin)*y,
        )

    def _pos_to_scale(
            self: Self,
            pos: tuple[float],
            height: float = 0,
        ) -> float:
        # transforms a position into the corresponding scale
        pos = self._normalize_pos(pos)
        return 1/np.sum((pos - self.view_pos)**2)**0.5

    def _pos_to_xy(
            self: Self,
            pos: tuple[float],
            height: float = 0,
            screen_thr: float = 2,
        ) -> (float, float):
        # transforms a 3D position into a 2D coordinate
        x, y, z = self._project_to_screen(pos, height)
        if z < self.screen_dist/screen_thr:
            mult = screen_thr*np.exp(self.screen_dist/screen_thr - z)
            if not x and not y:
                y = 1 
        else:
           mult = self.screen_dist/z
        return self._normalize_xy(mult*x, mult*y)

        # side, depth, altitude = self._normalize_pos(pos)
        # scale = self._pos_to_scale(pos)
        # if self.horizon_angle:
        #     y = (1 - scale)/(1 - self._depth_exponent)
        # else:
        #     y = depth*self.scale*self.depth_scale + self.depth_shift
        # x = scale*self.side_scale*(side*self.scale - 0.5) + 0.5
        # x = self.xmin + (self.xmax - self.xmin)*x
        # y = self.ymin + (self.ymax - self.ymin)*y
        # sin = np.sin(self.horizon_angle*np.pi/180)
        # y += (altitude + height)*self.scale*scale*sin
        # return x, y

    def _pos_to_shade_pos(
            self: Self,
            pos: tuple[float],
            height: float = 0,
        ) -> (float, float):
        # transforms a 3D position into a 2D coordinate
        side, depth, altitude = self._normalize_pos(pos)
        shade_shift = self._shade_shift()
        shade_shift *= (height + altitude)*self.altitude_to_shade
        return (
            side + shade_shift[0],
            depth + shade_shift[1],
        )

    def _round_volume(
            self: Self,
            available_key: Any,
        ) -> dict:
        # creates the volume dictionary for a rounded object
        volume = {
            'main' : f'{available_key}_main',
            'side' : [
                f'{available_key}_side{index}'
                for index in range(len(self.round_sides))
            ],
            'shade' : f'{available_key}_shade',
        }
        for shape_key in volume.values():
            if isinstance(shape_key, str):
                shape_keys = [shape_key]
                alphas = [1]
            else:
                shape_keys = shape_key
                alphas = self.round_sides.values()
            for shape_key, alpha in zip(shape_keys, alphas):
                patch = self.add_raw_path(
                    key=shape_key,
                    vertices=[(0, 0)],
                    lw=0,
                    alpha=alpha,
                    zorder=0,
                    visible=not self.draft
                )
                if shape_key.endswith('_main'):
                    patch.set_visible(True)
                elif shape_key.endswith('_shade'):
                    patch.set_zorder(-1)
                else:
                    patch.set_color('black')
        return volume

    def _create_volume(
            self: Self,
            name: str,
            key: Any = None,
            **kwargs,
        ) -> Self:
        # creates the basis for a new volume
        key, available = self.key_checker(key=key, category='volume')
        if available:
            volume = {'name' : name}
            volume.update(kwargs)
            volume.update(
                getattr(self, f'_create_{name}')(
                    available_key=key,
                    **kwargs,
                )
            )
            self._volumes[key] = volume
        else:
            volume = self._volumes[key]
        return self

    def _update_volume(
            self: Self,
            name: str,
            **kwargs,
        ) -> None:
        # updates the volume
        getattr(self, f'_update_{name}')(**self._volume_kwargs(kwargs))

    def _volume_kwargs(
            self: Self,
            kwargs: dict,
        ):
        # modifies the parameters used for a volume
        kwargs = kwargs.copy()
        for method in dir(self):
            if method.startswith('_volume_kwargs_'):
                kwargs = getattr(self, method)(kwargs)
        return kwargs

    def _only_avoid_to_list(
            self: Self,
            only_avoid: Any = None,
        ) -> list:
        # transforms an only/avoid parameter into a list
        if only_avoid is None:
            only_avoid = list(self._volumes)
        elif isinstance(only_avoid, list):
            only_avoid = [
                volume for volume in only_avoid
                if volume in self._volumes
            ]
        elif only_avoid in self._volumes:
            only_avoid = [only_avoid]
        elif isinstance(only_avoid, str):
            only_avoid = [
                volume for (volume, info) in self._volumes.items()
                if info['name'] == only_avoid
            ]
        else:
            message = 'The value of only and avoid must be either '
            message += 'None, a key, a string, or a list: '
            message += str(only_avoid)
            raise ValueError(message)
        return only_avoid