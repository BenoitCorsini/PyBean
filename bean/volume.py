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

    def _shade_shift(
            self: Self,
            two_dim: bool = False,
        ) -> np.array:
        # return a vector for shade shifting
        return self.angle_shift(
            angle=self.shade_angle,
            two_dim=two_dim,
        )

    def _pos_to_scale(
            self: Self,
            pos: (float, float, float),
        ) -> float:
        # transforms a position into the corresponding scale
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
        patch = self.add_shape(
            shape_name='Circle',
            key=key,
            xy=(0, 0),
            lw=0,
            zorder=0,
        )
        volume['side'] = []
        for side_index, alpha in enumerate(self.sphere_side.values()):
            key = f'{name}_side{side_index}'
            volume['side'].append(key)
            self.add_raw_path(
                key=key,
                vertices=[(0, 0)],
                lw=0,
                zorder=0,
                color='black',
                alpha=alpha,
                visible=not self.draft,
            )
        key = f'{name}_shade'
        volume['shade'] = key
        self.add_shape(
            shape_name='Circle',
            key=key,
            xy=(0, 0),
            lw=0,
            zorder=-1,
            visible=not self.draft,
        )
        return volume

    def _update_sphere(
            self: Self,
            main: str,
            side: list[str],
            shade: str,
            pos: (float, float, float) = None,
            xy: (float, float) = (0, 0),
            radius: float = 1,
            colour: str = None,

        ) -> None:
        # update the sphere
        if pos is not None:
            xy = self._pos_to_xy(pos)
        radius *= self.scale
        shade_xy = np.array(xy) + self.shade_delta_height*self._shade_shift()
        self.apply_to_shape('set_center', key=main, xy=xy)
        self.apply_to_shape('set_radius', key=main, radius=radius)
        clipper = self.set_shape(key=main, color=colour)
        if not self.draft:
            for key, ratio in zip(side, self.sphere_side):
                path = self.crescent_path(
                    xy=xy,
                    a=radius,
                    theta1=-90,
                    theta2=90,
                    angle=self.shade_angle,
                    ratio=ratio,
                )
                self.apply_to_shape('set_path', key=key, path=path)
                self.set_shape(key=key, clip_path=clipper)
            self.apply_to_shape('set_center', key=shade, xy=shade_xy)
            self.apply_to_shape('set_radius', key=shade, radius=radius)
            shade_colour = self.get_cmap(['white', clipper.get_fc()])(
                self.shade_cmap_ratio
            )
            self.set_shape(key=shade, color=shade_colour)

    def new_sphere(
            self: Self,
            key: Any = None,
            **kwargs,
        ) -> None:
        # create the basis for a new sphere
        key, available = self.key_checker(key=key, category='volume')
        if available:
            volume = {'name' : 'sphere'}
            volume.update(kwargs)
            volume.update(self._create_sphere(name=key))
            self.update_volume(**volume)
            self._volumes[key] = volume
        else:
            volume = self._volumes[key]
        return volume

    def update_volume(
            self: Self,
            name: str,
            **kwargs,
        ) -> None:
        # update the volume
        getattr(self, f'_update_{name}')(**kwargs)

    def test(
            self: Self,
        ) -> None:
        # the main testing function
        print(self)
        print(self._get_classes())
        print(self._get_new_methods())
        print(self.get_kwargs())
        self.new_sphere(
            colour='crimson',
            xy=(0.25, 0.25),
            radius=0.2,
        )
        self.save()
        print(self._volumes)
