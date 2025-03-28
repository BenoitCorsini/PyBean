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

    draft = False
    scale = 1
    view_pos = (0.5, -1.5, 2)
    view_angle = -45
    screen_dist = 1.5
    sun_direction = (0.5, 0.25, -1)
    _side_cmap_ratio = 0.7
    _shade_darkness_ratio = 0.5
    _shade_background_ratio = 0.1
    _round_sides = {
        0.49 : 0.05,
        0.25 : 0.07,
        0.09 : 0.12,
        0.02 : 0.25,
    }
    _polyhedron_lw = 1
    _text_height_ratio = 0.5
    _text_params = {
        'lw' : 1,
        'fc' : 'white',
        'ec' : 'black',
        'joinstyle' : 'round',
        'capstyle' : 'round',
        'visible' : True,
    }

    _volume_params = {
        'draft' : bool,
    }

    def _new_volume(
            self: Self,
        ) -> Self:
        # new volume instance
        self._volumes = {}
        self._volume_index = 0
        self._view_pos = np.array(self.view_pos)
        self._screen_xdir = np.array([1, 0, 0]),
        self._screen_ydir = np.array([
            0,
            -np.sin(self.view_angle*np.pi/180),
            np.cos(self.view_angle*np.pi/180),
        ])
        self._screen_zdir = np.array([
            0,
            np.cos(self.view_angle*np.pi/180),
            np.sin(self.view_angle*np.pi/180),
        ])
        self._sun_dir = np.array(self.sun_direction)
        norm = np.sum(self._sun_dir**2)
        if not norm:
            norm = 1
        self._sun_dir = self._sun_dir/norm**0.5
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
        return 1/np.sum((pos - self._view_pos)**2)**0.5

    def _project_on_screen(
            self: Self,
            pos: tuple[float],
            height: float = 0,
        ) -> np.array:
        # project a position relative to the viewer and the screen
        relative_pos = self._normalize_pos(pos, height)
        relative_pos = relative_pos*self.scale - self._view_pos
        return (
            float(np.sum(relative_pos*self._screen_xdir)),
            float(np.sum(relative_pos*self._screen_ydir)),
            float(np.sum(relative_pos*self._screen_zdir)),
        )

    def _normalize_xy(
            self: Self,
            x: float,
            y: float,
        ) -> np.array:
        # normalize an xy coordinate into the frame
        return (
            self._get_bound('xmin') + (self._get_bound('xmax') - self._get_bound('xmin'))*(0.5 + x),
            (self._get_bound('ymin') + self._get_bound('ymax'))/2 + (self._get_bound('xmax') - self._get_bound('xmin'))*y,
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
        if self._sun_dir[2] >= 0:
            return 0, 0
        pos = self._normalize_pos(pos, height)
        ground_dist = pos[2]/self._sun_dir[2]
        pos = pos - ground_dist*self._sun_dir
        return float(pos[0]), float(pos[1])

    def _round_volume(
            self: Self,
            available_key: Any,
        ) -> dict:
        # creates the volume dictionary for a rounded object
        volume = {
            'key' : available_key,
            '_main' : f'{available_key}_main',
            '_side' : [
                f'{available_key}_side{index}'
                for index in range(len(self._round_sides))
            ],
            '_shade' : f'{available_key}_shade',
            '_text' : f'{available_key}_text'
        }
        for shape_key in volume.values():
            if isinstance(shape_key, str):
                shape_keys = [shape_key]
                alphas = [1]
            else:
                shape_keys = shape_key
                alphas = self._round_sides.values()
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
        key, available = self._key_checker(key=key, category='volume')
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
        self._update_volume(**volume)
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
        shade_colour = shade_colour(self._shade_darkness_ratio)
        shade_colour = self.get_cmap([background, shade_colour])
        shade_colour = shade_colour(self._shade_background_ratio)
        return shade_colour




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

