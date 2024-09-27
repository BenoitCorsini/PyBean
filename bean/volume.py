import numpy as np
from typing_extensions import Any, Self

from .shape import Shape


class Volume(Shape):

    '''
    fundamental variables and function
    '''

    _volume_params = {
        'draft' : bool,
        'scale' : float,
        'horizon_angle' : float,
        'depth_shift' : float,
        'depth_scale' : float,
        'shade_angle' : float,
        'altitude_to_shade' : float,
        'shade_cmap_ratio' : float,
    }

    def _new_volume(
            self: Self,
        ) -> Self:
        # new volume instance
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
            angle=self.shade_angle,
            two_dim=two_dim,
        )

    def _pos_to_scale(
            self: Self,
            pos: (float, float, float),
        ) -> float:
        # transforms a position into the corresponding scale
        _, depth, _ = pos
        depth *= self.scale*self.depth_scale
        depth += self.depth_shift
        return self._depth_exponent**depth

    def _pos_to_xy(
            self: Self,
            pos: (float, float, float),
            height: float = 0,
        ) -> (float, float):
        # transforms a 3D position into a 2D coordinate
        side, depth, altitude = pos
        scale = self._pos_to_scale(pos)
        if self.horizon_angle:
            y = (1 - scale)/(1 - self._depth_exponent)
        else:
            y = depth*self.scale
        x = scale*self.side_scale*(side*self.scale - 0.5) + 0.5
        x = self.xmin + (self.xmax - self.xmin)*x
        y = self.ymin + (self.ymax - self.ymin)*y
        sin = np.sin(self.horizon_angle*np.pi/180)
        y += (altitude + height)*self.scale*scale*sin
        return x, y

    def _pos_to_shade_pos(
            self: Self,
            pos: (float, float, float),
            height: float = 0
        ) -> (float, float):
        # transforms a 3D position into a 2D coordinate
        side, depth, altitude = pos
        shade_shift = self._shade_shift()
        shade_shift *= (height + altitude)*self.altitude_to_shade
        return (
            side + shade_shift[0],
            depth + shade_shift[1],
            0,
        )

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
        # updates the sphere
        if pos is not None:
            xy = self._pos_to_xy(pos, height=radius)
            if not self.draft:
                shade_pos = self._pos_to_shade_pos(pos, height=radius)
            radius *= self.scale
            if not self.draft:
                shade_xy = self._pos_to_xy(shade_pos)
                shade_radius = radius*self._pos_to_scale(shade_pos)
            scale = self._pos_to_scale(pos)
            radius *= scale
            zorder = scale
        else:
            radius *= self.scale
            xy = (xy[0]*self.scale, xy[1]*self.scale)
            zorder = 0
            if not self.draft:
                shade_xy = xy
                shade_radius = radius
        path = self.curve_path(xy=xy, a=radius)
        self.apply_to_shape('set_path', key=main, path=path)
        clipper = self.set_shape(key=main, color=colour, zorder=zorder)
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
                self.set_shape(key=key, clip_path=clipper, zorder=zorder)
            path = self.curve_path(
                xy=shade_xy,
                a=shade_radius,
                b=shade_radius*np.cos(self.horizon_angle*np.pi/180),
            )
            self.apply_to_shape('set_path', key=shade, path=path)
            shade_colour = self.get_cmap(['white', clipper.get_fc()])(
                self.shade_cmap_ratio
            )
            self.set_shape(key=shade, color=shade_colour)

    def _create_tube(
            self: Self,
            name: str,
        ) -> dict:
        # creates the volume dictionary of a tube
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
            slope: str = 'flat',

        ) -> None:
        # updates the tube
        if radius2 is None:
            radius2 = radius1
        variables = {}
        zorder = 0
        for index in [1, 2]:
            pos = locals()[f'pos{index}']
            radius = locals()[f'radius{index}']
            if pos is not None:
                if slope == 'down':
                    height = radius
                elif slope == 'up':
                    height = 2*max(radius1, radius2) - radius
                else:
                    height = max(radius1, radius2)
                variables[f'xy{index}'] = self._pos_to_xy(pos, height=height)
                if not self.draft:
                    shade_pos = self._pos_to_shade_pos(pos, height=height)
                radius *= self.scale
                scale = self._pos_to_scale(pos)
                variables[f'radius{index}'] = radius*scale
                zorder = max(zorder, scale)
                if not self.draft:
                    variables[f'shade_xy{index}'] = self._pos_to_xy(shade_pos)
                    variables[f'shade_radius{index}'] = (
                        radius*self._pos_to_scale(shade_pos)
                    )
            else:
                xy = locals()[f'xy{index}']
                xy = (xy[0]*self.scale, xy[1]*self.scale)
                variables[f'xy{index}'] = xy
                radius *= self.scale
                variables[f'radius{index}'] = radius
                if not self.draft:
                    variables[f'shade_xy{index}'] = xy
                    variables[f'shade_radius{index}'] = radius
        distance = self.distance_from_xy(variables['xy1'], variables['xy2'])
        delta_radius = variables['radius2'] - variables['radius1']
        is_sphere = np.abs(delta_radius) > distance
        if is_sphere:
            sphere_index = 1 + int(delta_radius > 0)
            self.apply_to_shape('set_path', key=main, path=self.curve_path(
                xy=variables[f'xy{sphere_index}'],
                a=variables[f'radius{sphere_index}'],
            ))
            angle = 0
            around_angle = 0
        else:
            angle = self.angle_from_xy(variables['xy1'], variables['xy2'])
            around_angle = np.arcsin(delta_radius/distance)*180/np.pi
            path = self.merge_curves(*[self.curve_path(
                xy=variables[f'xy{index}'],
                a=variables[f'radius{index}'],
                angle=angle,
                theta1=(3 - 2*index)*(90 + around_angle),
                theta2=(2*index - 3)*(90 + around_angle),
            ) for index in [1, 2]])
            self.apply_to_shape('set_path', key=main, path=path)
        clipper = self.set_shape(key=main, color=colour, zorder=zorder)
        if not self.draft:
            theta1 = self.normalize_angle(
                90 + around_angle + angle - self.shade_angle
            )
            theta2 = self.normalize_angle(
                270 - around_angle + angle - self.shade_angle
            )
            dark_index = 1 + int(self.normalize_angle(theta2 - theta1) > 0)
            for key, ratio in zip(side, self.round_sides):
                crescents = []
                if is_sphere or (abs(theta1) >= 90 and abs(theta2) >= 90):
                    crescents.append({
                        'theta1' : 270,
                        'theta2' : 90,
                        'index' : sphere_index if is_sphere else dark_index,
                    })
                elif abs(theta1) < 90 and abs(theta2) < 90:
                    crescents.append({
                        'theta1' : 270,
                        'theta2' : locals()[f'theta{3 - dark_index}'],
                        'index' : dark_index,
                    })
                    crescents.append({
                        'theta1' : locals()[f'theta{3 - dark_index}'],
                        'theta2' : locals()[f'theta{dark_index}'],
                        'index' : 3 - dark_index,
                    })
                    crescents.append({
                        'theta1' : locals()[f'theta{dark_index}'],
                        'theta2' : 90,
                        'index' : dark_index,
                    })
                else:
                    index = 1 + int(abs(theta1) >= 90)
                    crescents.append({
                        'theta1' : 270,
                        'theta2' : locals()[f'theta{index}'],
                        'index' : 3 - index,
                    })
                    crescents.append({
                        'theta1' : locals()[f'theta{index}'],
                        'theta2' : 90,
                        'index' : index,
                    })
                paths = []
                for crescent in crescents:
                    index = crescent.pop('index')
                    for s in ['xy', 'radius']:
                        crescent[s] = variables[f'{s}{index}']
                    paths.append(self.crescent_paths(
                        ratio=ratio,
                        angle=self.shade_angle,
                        **crescent
                    ))
                inners, outers = zip(*paths)
                path = self.merge_curves(*(inners[::-1] + outers))
                self.apply_to_shape('set_path', key=key, path=path)
                self.set_shape(key=key, clip_path=clipper, zorder=zorder)
            shade_colour = self.get_cmap(['white', clipper.get_fc()])(
                self.shade_cmap_ratio
            )
            self.set_shape(key=shade, color=shade_colour)
            distance = self.distance_from_xy(
                variables['shade_xy1'],
                variables['shade_xy2'],
            )
            delta_radius = (
                variables['shade_radius2']
                - variables['shade_radius1']
            )
            cos = np.cos(self.horizon_angle*np.pi/180)
            if np.abs(delta_radius) > distance:
                index = 1 + int(delta_radius > 0)
                self.apply_to_shape(
                    method='set_path',
                    key=shade,
                    path=self.curve_path(
                        xy=variables[f'shade_xy{index}'],
                        a=variables[f'shade_radius{index}'],
                        b=variables[f'shade_radius{index}']*cos,
                    )
                )
            else:
                shade_angle = self.angle_from_xy(
                    variables['shade_xy1'],
                    variables['shade_xy2'],
                )
                shade_around_angle = (
                    np.arcsin(delta_radius/distance)*180/np.pi
                )
                path = self.merge_curves(*[self.curve_path(
                    xy=variables[f'shade_xy{index}'],
                    a=variables[f'shade_radius{index}'],
                    b=variables[f'shade_radius{index}']*cos,
                    theta1=(
                        (3 - 2*index)*(90 + shade_around_angle)
                        + shade_angle
                    ),
                    theta2=(
                        (2*index - 3)*(90 + shade_around_angle)
                        + shade_angle
                    ),
                ) for index in [1, 2]])
                self.apply_to_shape('set_path', key=shade, path=path)

    '''
    general methods
    '''

    def new_volume(
            self: Self,
            name: str,
            key: Any = None,
            **kwargs,
        ) -> None:
        # creates the basis for a new volume
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
        # updates the volume
        getattr(self, f'_update_{name}')(**kwargs)

    '''
    main method
    '''

    def main(
            self: Self,
        ) -> None:
        # the main running function
        pass
