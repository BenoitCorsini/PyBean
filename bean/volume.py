import numpy as np
from typing_extensions import Any, Self

from .shape import Shape


class Volume(Shape):

    _volume_params = {
        'draft' : bool,
        'scale' : float,
        'shade_angle' : float,
        'shade_delta_height' : float,
    }

    def _new_volume(
            self: Self,
        ) -> Self:
        # new volume instance
        self._volumes = {}
        self._volume_index = 0
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

    def _pos_to_scale(
            self: Self,
            pos: (float, float, float),
        ) -> float:
        # transforms a position into the corresponding scale
        if pos is None:
            raise ValueError('None position cannot be projected')
        return self.scale

    def _pos_to_xy(
            self: Self,
            pos: (float, float, float),
        ) -> (float, float):
        # transforms a 3D position into a 2D coordinate
        side, depth, altitude = pos
        return side, depth

    def _create_sphere(
            self: Self,
            name: str,
        ) -> dict:
        # creates the voluem dictionary of a sphere
        volume = {}
        key = f'{name}_main'
        volume['main'] = key
        self.add_shape(
            shape_name='Circle',
            key=key,
            xy=(0, 0),
            lw=0,
            zorder=0,
        )
        volume['side'] = []
        for side_index, _ in enumerate(self.sphere_side):
            key = f'{name}_side{side_index}'
            volume['side'].append(key)
            self.add_raw_path(
                key=key,
                vertices=[(0, 0)],
                lw=0,
                zorder=0,
            )
        key = f'{name}_shade'
        volume['shade'] = key
        self.add_shape(
            shape_name='Circle',
            key=key,
            xy=(0, 0),
            lw=0,
            zorder=-1,
        )
        return volume

    def new_sphere(
            self: Self,
            pos: (float, float, float) = None,
            xy: (float, float) = (0, 0),
            radius: float = 1,
            key: Any = None,
        ) -> None:
        # create the basis for a new sphere
        key, available = self.key_checker(key=key, category='volume')
        if available:
            volume = {
                'type' : 'sphere',
                'pos' : pos,
                'xy' : xy,
                'radius' : radius,
            }
            volume = self._create_sphere(name=key)
            self._volumes[key] = volume
        else:
            volume = self._volumes[key]
        return volume

    def test(
            self: Self,
        ) -> None:
        # the main testing function
        print(self)
        print(self._get_classes())
        print(self._get_new_methods())
        print(self.get_kwargs())
        self.new_sphere()
        # self.new_sphere()
        # self.new_sphere('other')
        self.save()
        print(self._volumes)
