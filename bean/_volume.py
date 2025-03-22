import numpy as np
from typing_extensions import Any, Self

from .brush import Brush


'''
Any subsequent volume-based class needs the following functions:
    _create_{volume name}
    _update_{volume name}
    new_{volume name}
The latter function being preferably placed in the main Volume class.
'''


class _Volume(Brush):

    '''
    fundamental variables and function
    '''

    _volume_params = {
        'draft' : bool,
        'scale' : float,
        'view_pos' : float,
        'view_angle' : float,
        'screen_dist' : float,
        'sun_direction' : float,
        'side_cmap_ratio' : float,
        'shade_darkness_ratio' : float,
        'shade_background_ratio' : float,
        'polyhedron_lw' : float,
    }

    _canvas_nargs = {
        'view_pos' : 3,
        'sun_direction' : 3,
    }

    def _new_volume(
            self: Self,
        ) -> Self:
        # new volume instance
        self._volumes = {}
        self._volume_index = 0
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
        self.sun_direction = np.array(self.sun_direction)
        norm = np.sum(self.sun_direction**2)
        if not norm:
            norm = 1
        self.sun_direction = self.sun_direction/norm**0.5
        return self

    '''
    hidden methods
    '''

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
        return np.array(pos) + np.array([0, 0, height])

    def _pos_to_scale(
            self: Self,
            pos: tuple[float],
            height: float = 0,
        ) -> float:
        # transforms a position into the corresponding scale
        pos = self._normalize_pos(pos, height)*self.scale
        return 1/np.sum((pos - self.view_pos)**2)**0.5

    def _project_on_screen(
            self: Self,
            pos: tuple[float],
            height: float = 0,
        ) -> np.array:
        # project a position relative to the viewer and the screen
        relative_pos = self._normalize_pos(pos, height)
        relative_pos = relative_pos*self.scale - self.view_pos
        return (
            float(np.sum(relative_pos*self.screen_xdir)),
            float(np.sum(relative_pos*self.screen_ydir)),
            float(np.sum(relative_pos*self.screen_zdir)),
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

    def _pos_to_xy(
            self: Self,
            pos: tuple[float],
            height: float = 0,
            screen_thr: float = 2,
        ) -> (float, float):
        # transforms a 3D position into a 2D coordinate
        x, y, z = self._project_on_screen(pos, height)
        if z < self.screen_dist/screen_thr:
            mult = screen_thr*np.exp(self.screen_dist/screen_thr - z)
            if not x and not y:
                y = 1 
        else:
           mult = self.screen_dist/z
        return self._normalize_xy(mult*x, mult*y)

    def _pos_to_shade_pos(
            self: Self,
            pos: tuple[float],
            height: float = 0,
        ) -> (float, float):
        # transforms a 3D position into a 2D coordinate
        if self.sun_direction[2] >= 0:
            return 0, 0
        pos = self._normalize_pos(pos, height)
        ground_dist = pos[2]/self.sun_direction[2]
        pos = pos - ground_dist*self.sun_direction
        return float(pos[0]), float(pos[1])

    def _round_volume(
            self: Self,
            available_key: Any,
        ) -> dict:
        # creates the volume dictionary for a rounded object
        volume = {
            'key' : available_key,
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
            volume = {
                'name' : name,
                'key' : key,
            }
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
        getattr(self, f'_update_{name}')(**self._volume_kwargs(**kwargs))

    def _volume_kwargs(
            self: Self,
            **kwargs,
        ):
        # modifies the parameters used for a volume
        for method in dir(self):
            if method.startswith('_volume_kwargs_'):
                kwargs = getattr(self, method)(**kwargs)
        del kwargs['key']
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

    def _get_shade_colour(
            self: Self,
            colour: Any,
            background: Any = 'white',
            darkness: Any = 'black',
        ) -> Any:
        # obtains the shade colour of a volume on a given background
        shade_colour = self.get_cmap([colour, darkness])
        shade_colour = shade_colour(self.shade_darkness_ratio)
        shade_colour = self.get_cmap([background, shade_colour])
        shade_colour = shade_colour(self.shade_background_ratio)
        return shade_colour