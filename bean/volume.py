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
        if pos is None:
            raise ValueError('None position cannot be projected')
        side, depth, altitude = pos
        return side, depth

    def new_sphere(
            self: Self,
            pos: (float, float, float) = None,
            xy: (float, float) = None,
            key: Any = None,
        ) -> None:
        # create the basis for a new sphere
        if pos is not None:
            xy = self._pos_to_xy(pos)
        key, available = self.key_checker(key=key, category='volume')
        if available:
            volume = {
                'main' : f'{key}_main',
                'shade' : f'{key}_shade',
            }
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
        # self.new_sphere()
        # self.new_sphere()
        # self.new_sphere('other')
        self.save()
        print(self._volumes)
