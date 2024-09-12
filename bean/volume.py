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

    def _create_round(
            self: Self,
            name: str,
        ) -> dict:
        # creates the volume dictionary for a rounded object
        volume = {
            'main' : f'{name}_main',
            'side' : [
                f'{name}_side{index}'
                for index in range(len(self.round_sides))
            ],
            'shade' : f'{name}_shade',
        }
        for key in volume.values():
            if isinstance(key, str):
                keys = [key]
                alphas = [1]
            else:
                keys = key
                alphas = self.round_sides.values()
            for key, alpha in zip(keys, alphas):
                patch = self.add_raw_path(
                    key=key,
                    vertices=[(0, 0)],
                    lw=0,
                    alpha=alpha,
                    zorder=0,
                    visible=not self.draft
                )
                if key.endswith('_main'):
                    patch.set_visible(True)
                elif key.endswith('_shade'):
                    patch.set_zorder(-1)
                else:
                    patch.set_color('black')
        return volume

    def _create_sphere(
            self: Self,
            name: str,
        ) -> dict:
        # creates the volume dictionary of a sphere
        return self._create_round(name=name)

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
            shade_xy = np.array(xy) + self.shade_delta_height*self._shade_shift()
        else:
            shade_xy = xy
        radius *= self.scale
        path = self.curve_path(xy=xy, a=radius)
        self.apply_to_shape('set_path', key=main, path=path)
        clipper = self.set_shape(key=main, color=colour)
        if not self.draft:
            for key, ratio in zip(side, self.round_sides):
                path = self.merge_curves(*self.crescent_paths(
                    xy=xy,
                    radius=radius,
                    ratio=ratio,
                    theta1=270,
                    theta2=90,
                    angle=self.shade_angle,
                ))
                self.apply_to_shape('set_path', key=key, path=path)
                self.set_shape(key=key, clip_path=clipper)
            path = self.curve_path(xy=xy, a=radius)
            self.apply_to_shape('set_path', key=shade, path=path)
            shade_colour = self.get_cmap(['white', clipper.get_fc()])(
                self.shade_cmap_ratio
            )
            self.set_shape(key=shade, color=shade_colour)

    def _create_tube(
            self: Self,
            name: str,
        ) -> dict:
        # creates the voluem dictionary of a tube
        return self._create_round(name=name)

    def _update_tube(
            self: Self,
            main: str,
            side: list[str],
            shade: str,
            pos1: (float, float, float) = None,
            xy1: (float, float) = (0, 0),
            radius1: float = 1,
            pos2: (float, float, float) = None,
            xy2: (float, float) = (0, 0),
            radius2: float = None,
            colour: str = None,

        ) -> None:
        # update the sphere
        if pos1 is not None:
            xy1 = self._pos_to_xy(pos1)
        if pos2 is not None:
            xy2 = self._pos_to_xy(pos2)
        if radius2 is None:
            radius2 = radius1
        radius1 *= self.scale
        radius2 *= self.scale
        distance = self.distance_from_xy(xy1, xy2)
        if np.abs(radius2 - radius1) > distance:
            if radius2 > radius1:
                xy = xy2
                radius = radius2
            else:
                xy = xy1
                radius = radius1
            return self._update_sphere(
                main=main,
                side=side,
                shade=shade,
                xy=xy,
                radius=radius,
                colour=colour,
            )
        angle = self.angle_from_xy(xy1, xy2)
        around_angle = np.arctan((radius2 - radius1)/distance)*180/np.pi
        curve1 = self.curve_path(
            xy=xy1,
            a=radius1,
            theta1=90 + around_angle,
            theta2=270 - around_angle,
            angle=angle,
        )
        curve2 = self.curve_path(
            xy=xy2,
            a=radius2,
            theta1=270 - around_angle,
            theta2=90 + around_angle,
            angle=angle,
        )
        path = self.merge_curves(curve1, curve2)
        self.apply_to_shape('set_path', key=main, path=path)
        clipper = self.set_shape(key=main, color=colour)
        if not self.draft:
            effective_angle = angle - self.shade_angle
            for key, ratio in zip(side, self.round_sides):
                inners = []
                outers = []
                theta1 = self.normalize_angle(90 + around_angle + effective_angle)
                theta2 = self.normalize_angle(270 - around_angle + effective_angle)
                if abs(theta1) < 90 and abs(theta2) >= 90:
                    inner, outer = self.crescent_paths(
                        xy=xy1,
                        radius=radius1,
                        ratio=ratio,
                        theta1=theta1,
                        theta2=90,
                        angle=self.shade_angle,
                    )
                    inners.append(inner)
                    outers.append(outer)
                    inner, outer = self.crescent_paths(
                        xy=xy2,
                        radius=radius2,
                        ratio=ratio,
                        theta1=270,
                        theta2=theta1,
                        angle=self.shade_angle,
                    )
                    inners.append(inner)
                    outers.append(outer)
                elif abs(theta1) >= 90 and abs(theta2) < 90:
                    inner, outer = self.crescent_paths(
                        xy=xy2,
                        radius=radius2,
                        ratio=ratio,
                        theta1=theta2,
                        theta2=90,
                        angle=self.shade_angle,
                    )
                    inners.append(inner)
                    outers.append(outer)
                    inner, outer = self.crescent_paths(
                        xy=xy1,
                        radius=radius1,
                        ratio=ratio,
                        theta1=270,
                        theta2=theta2,
                        angle=self.shade_angle,
                    )
                    inners.append(inner)
                    outers.append(outer)
                elif abs(theta1) >= 90 and abs(theta2) >= 90:
                    if self.normalize_angle(theta2 - theta1) > 0:
                        inner, outer = self.crescent_paths(
                            xy=xy2,
                            radius=radius2,
                            ratio=ratio,
                            theta1=270,
                            theta2=90,
                            angle=self.shade_angle,
                        )
                        inners.append(inner)
                        outers.append(outer)
                    else:
                        inner, outer = self.crescent_paths(
                            xy=xy1,
                            radius=radius1,
                            ratio=ratio,
                            theta1=270,
                            theta2=90,
                            angle=self.shade_angle,
                        )
                        inners.append(inner)
                        outers.append(outer)
                else:
                    if self.normalize_angle(theta2 - theta1) > 0:
                        inner, outer = self.crescent_paths(
                            xy=xy2,
                            radius=radius2,
                            ratio=ratio,
                            theta1=theta2,
                            theta2=90,
                            angle=self.shade_angle,
                        )
                        inners.append(inner)
                        outers.append(outer)
                        inner, outer = self.crescent_paths(
                            xy=xy1,
                            radius=radius1,
                            ratio=ratio,
                            theta1=theta1,
                            theta2=theta2,
                            angle=self.shade_angle,
                        )
                        inners.append(inner)
                        outers.append(outer)
                        inner, outer = self.crescent_paths(
                            xy=xy2,
                            radius=radius2,
                            ratio=ratio,
                            theta1=270,
                            theta2=theta1,
                            angle=self.shade_angle,
                        )
                        inners.append(inner)
                        outers.append(outer)
                    else:
                        inner, outer = self.crescent_paths(
                            xy=xy1,
                            radius=radius1,
                            ratio=ratio,
                            theta1=theta1,
                            theta2=90,
                            angle=self.shade_angle,
                        )
                        inners.append(inner)
                        outers.append(outer)
                        inner, outer = self.crescent_paths(
                            xy=xy2,
                            radius=radius2,
                            ratio=ratio,
                            theta1=theta2,
                            theta2=theta1,
                            angle=self.shade_angle,
                        )
                        inners.append(inner)
                        outers.append(outer)
                        inner, outer = self.crescent_paths(
                            xy=xy1,
                            radius=radius1,
                            ratio=ratio,
                            theta1=270,
                            theta2=theta2,
                            angle=self.shade_angle,
                        )
                        inners.append(inner)
                        outers.append(outer)
                path = self.merge_curves(*(inners + outers[::-1]))
                self.apply_to_shape('set_path', key=key, path=path)
                self.set_shape(key=key,
                    clip_path=clipper,
                    # fill=False, lw=2
                    )
            # self.apply_to_shape('set_center', key=shade, xy=shade_xy)
            # self.apply_to_shape('set_radius', key=shade, radius=radius)
            # shade_colour = self.get_cmap(['white', clipper.get_fc()])(
            #     self.shade_cmap_ratio
            # )
            # self.set_shape(key=shade, color=shade_colour)

    def new_volume(
            self: Self,
            name: str,
            key: Any = None,
            **kwargs,
        ) -> None:
        # create the basis for a new sphere
        key, available = self.key_checker(key=key, category='volume')
        if available:
            volume = {'name' : name}
            volume.update(kwargs)
            volume.update(getattr(self, f'_create_{name}')(name=key))
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
        self.new_volume(
            name='sphere',
            colour='crimson',
            xy=(0.3, 0.3),
            radius=0.05,
        )
        self.new_volume(
            name='sphere',
            colour='royalblue',
            xy=(0.15, 0.45),
            radius=0.1,
        )
        self.new_volume(
            name='sphere',
            colour='forestgreen',
            xy=(0.85, 0.1),
            radius=0.05,
        )
        self.new_volume(
            name='tube',
            colour='gold',
            xy1=(0.4, 0.1),
            xy2=(0.6, 0.4),
            radius1=0.03,
            radius2=0.03,
        )
        self.new_volume(
            name='tube',
            colour='chocolate',
            xy1=(0.1, 0.1),
            xy2=(0.2, 0.1),
            radius1=0.05,
            radius2=0.01,
        )
        self.new_volume(
            name='tube',
            colour='chocolate',
            xy1=(0.1, 0.2),
            xy2=(0.2, 0.2),
            radius1=0.01,
            radius2=0.05,
        )
        self.new_volume(
            name='tube',
            colour='hotpink',
            xy1=(0.8, 0.4),
            xy2=(0.8, 0.3),
            radius1=0.05,
            radius2=0.01,
        )
        self.new_volume(
            name='tube',
            colour='hotpink',
            xy1=(0.9, 0.4),
            xy2=(0.9, 0.3),
            radius1=0.01,
            radius2=0.05,
        )
        self.new_volume(
            name='tube',
            colour='teal',
            xy1=(0.5, 0.5),
            xy2=(0.4, 0.5),
            radius1=0.05,
            radius2=0.01,
        )
        self.new_volume(
            name='tube',
            colour='teal',
            xy1=(0.5, 0.4),
            xy2=(0.4, 0.4),
            radius1=0.01,
            radius2=0.05,
        )
        self.new_volume(
            name='tube',
            colour='mediumorchid',
            xy1=(0.6, 0.1),
            xy2=(0.6, 0.2),
            radius1=0.05,
            radius2=0.01,
        )
        self.new_volume(
            name='tube',
            colour='mediumorchid',
            xy1=(0.7, 0.1),
            xy2=(0.7, 0.2),
            radius1=0.01,
            radius2=0.05,
        )
        self.save()
        print(self._volumes)
