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
        'depth_scale' : float,
        'depth_shift' : float,
        'side_scale' : float,
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
        self._side_angle = 180*np.arctan(self.altitude_to_shade)/np.pi
        self._side_angle *= np.cos(self.shade_angle*np.pi/180)
        self._side_angle -= 90
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

    def _normalize_pos(
            self: Self,
            pos: tuple[float],
        ) -> (float, float, float):
        # normalize a position into a triplet
        if '__len__' not in dir(pos):
            raise ValueError(f'Position is not a tuple: {pos}')
        elif len(pos) == 2:
            return pos[0], pos[1], 0
        elif len(pos) != 3:
            raise ValueError(f'Position with a wrong length: {pos}')
        return tuple(pos)

    def _pos_to_scale(
            self: Self,
            pos: tuple[float],
        ) -> float:
        # transforms a position into the corresponding scale
        _, depth, _ = self._normalize_pos(pos)
        depth *= self.scale*self.depth_scale
        depth += self.depth_shift
        return self._depth_exponent**depth

    def _pos_to_xy(
            self: Self,
            pos: tuple[float],
            height: float = 0,
        ) -> (float, float):
        # transforms a 3D position into a 2D coordinate
        side, depth, altitude = self._normalize_pos(pos)
        scale = self._pos_to_scale(pos)
        if self.horizon_angle:
            y = (1 - scale)/(1 - self._depth_exponent)
        else:
            y = depth*self.scale*self.depth_scale + self.depth_shift
        x = scale*self.side_scale*(side*self.scale - 0.5) + 0.5
        x = self.xmin + (self.xmax - self.xmin)*x
        y = self.ymin + (self.ymax - self.ymin)*y
        sin = np.sin(self.horizon_angle*np.pi/180)
        y += (altitude + height)*self.scale*scale*sin
        return x, y

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

    def _create_sphere(
            self: Self,
            available_key: Any,
        ) -> dict:
        # creates the volume dictionary of a sphere
        return self._round_volume(available_key=available_key)

    def _create_tube(
            self: Self,
            available_key: Any,
        ) -> dict:
        # creates the volume dictionary of a tube
        return self._round_volume(available_key=available_key)

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
            volume.update(getattr(self, f'_create_{name}')(available_key=key))
            self._volumes[key] = volume
        else:
            volume = self._volumes[key]
        return self

    def _update_sphere(
            self: Self,
            main: str,
            side: list[str],
            shade: str,
            pos: tuple[float] = (0, 0),
            radius: float = 1,
            colour: str = None,
            shade_colour: str = None,
            visible: bool = True,
            alpha: float = 1,
        ) -> None:
        # updates the sphere
        if not visible:
            self.set_shape(key=main, visible=False)
            for key in side:
                self.set_shape(key=key, visible=False)
            self.set_shape(key=shade, visible=False)
            return None
        xy = self._pos_to_xy(pos, height=radius)
        if not self.draft:
            shade_pos = self._pos_to_shade_pos(pos, height=radius)
        radius *= self.scale*self.side_scale
        if not self.draft:
            shade_xy = self._pos_to_xy(shade_pos)
            shade_radius = radius*self._pos_to_scale(shade_pos)
        scale = self._pos_to_scale(pos)
        radius *= scale
        zorder = scale
        path = self.curve_path(xy=xy, a=radius)
        self.apply_to_shape('set_path', key=main, path=path)
        clipper = self.set_shape(
            key=main,
            color=colour,
            zorder=zorder,
            alpha=alpha,
        )
        if not self.draft:
            for key, ratio in zip(side, self.round_sides):
                path = self.merge_curves(*self.crescent_paths(
                    xy=xy,
                    radius=radius,
                    ratio=ratio,
                    theta1=270,
                    theta2=90,
                    angle=self._side_angle,
                ))
                self.apply_to_shape('set_path', key=key, path=path)
                self.set_shape(
                    key=key,
                    clip_path=clipper,
                    zorder=zorder,
                    alpha=alpha*self.round_sides[ratio],
                )
            path = self.curve_path(
                xy=shade_xy,
                a=shade_radius,
                b=shade_radius*np.cos(self.horizon_angle*np.pi/180),
            )
            self.apply_to_shape('set_path', key=shade, path=path)
            if shade_colour is None:
                shade_colour = self.get_cmap(['white', clipper.get_fc()])(
                    self.shade_cmap_ratio
                )
            self.set_shape(key=shade, color=shade_colour, alpha=alpha)

    def _update_joint_spheres(
            self: Self,
            main: str,
            side: list[str],
            shade: str,
            pos1: tuple[float] = (0, 0),
            pos2: tuple[float] = (0, 0),
            radius1: float = 1,
            radius2: float = 1,
            colour: str = None,
            shade_colour: str = None,
            slope: str = 'flat',
            visible: bool = True,
            alpha: float = 1,
        ) -> None:
        # updates the volume created by two spheres
        if not visible:
            self.set_shape(key=main, visible=False)
            for key in side:
                self.set_shape(key=key, visible=False)
            self.set_shape(key=shade, visible=False)
            return None
        variables = {}
        zorder = 0
        for index in [1, 2]:
            pos = self._normalize_pos(locals()[f'pos{index}'])
            radius = locals()[f'radius{index}']
            if slope == 'down':
                height = radius
            elif slope == 'up':
                height = 2*max(radius1, radius2) - radius
            else:
                height = max(radius1, radius2)
            variables[f'xy{index}'] = self._pos_to_xy(pos, height=height)
            if not self.draft:
                shade_pos = self._pos_to_shade_pos(pos, height=height)
            radius *= self.scale*self.side_scale
            scale = self._pos_to_scale(pos)
            variables[f'radius{index}'] = radius*scale
            zorder += scale/2
            if not self.draft:
                variables[f'shade_xy{index}'] = self._pos_to_xy(shade_pos)
                variables[f'shade_radius{index}'] = (
                    radius*self._pos_to_scale(shade_pos)
                )
        distance = self.distance_from_xy(variables['xy1'], variables['xy2'])
        delta_radius = variables['radius2'] - variables['radius1']
        is_sphere = np.abs(delta_radius) >= distance
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
        clipper = self.set_shape(
            key=main,
            color=colour,
            zorder=zorder,
            alpha=alpha,
        )
        if not self.draft:
            theta1 = self.normalize_angle(
                90 + around_angle + angle - self._side_angle
            )
            theta2 = self.normalize_angle(
                270 - around_angle + angle - self._side_angle
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
                        angle=self._side_angle,
                        **crescent
                    ))
                inners, outers = zip(*paths)
                path = self.merge_curves(*(inners[::-1] + outers))
                self.apply_to_shape('set_path', key=key, path=path)
                self.set_shape(
                    key=key,
                    clip_path=clipper,
                    zorder=zorder,
                    alpha=alpha*self.round_sides[ratio],
                )
            if shade_colour is None:
                shade_colour = self.get_cmap(['white', clipper.get_fc()])(
                    self.shade_cmap_ratio
                )
            self.set_shape(key=shade, color=shade_colour, alpha=alpha)
            distance = self.distance_from_xy(
                variables['shade_xy1'],
                variables['shade_xy2'],
            )
            delta_radius = (
                variables['shade_radius2']
                - variables['shade_radius1']
            )
            cos = np.cos(self.horizon_angle*np.pi/180)
            if np.abs(delta_radius) >= distance:
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

    def _update_tube(
            self: Self,
            key1: Any = None,
            key2: Any = None,
            shift1: tuple[float] = (0, 0),
            shift2: tuple[float] = (0, 0),
            radius: Any = 0,
            space: Any = 0,
            collapse: bool = True,
            **kwargs,
        ) -> None:
        # updates the tube
        if isinstance(radius, tuple) or isinstance(radius, list):
            kwargs['radius1'], kwargs['radius2'] = radius
        else:
            kwargs['radius1'] = radius
            kwargs['radius2'] = radius
        if isinstance(space, tuple) or isinstance(space, list):
            space1, space2 = space
        else:
            space1 = space
            space2 = space
        for index in [1, 2]:
            key = locals()[f'key{index}']
            kwargs[f'pos{index}'] = np.array(self._normalize_pos(
                self._volumes.get(key, {}).get('pos', (0, 0))
            ))
        vect = kwargs['pos2'] - kwargs['pos1']
        norm = np.sum(vect**2)**0.5
        if space1 < 0:
            space1 *= -norm
        if space2 < 0:
            space2 *= -norm
        if collapse and norm < space1 + space2:
            kwargs['visible'] = False
        if not norm:
            norm = 1
        vect = vect/norm
        for index in [1, 2]:
            key = locals()[f'key{index}']
            height_shift = self._volumes.get(key, {})
            height_shift = height_shift.get(
                'height',
                height_shift.get('radius', 0)
            )
            kwargs[f'pos{index}'] = tuple(
                kwargs[f'pos{index}']
                + (3 - 2*index)*locals()[f'space{index}']*vect
                + np.array(self._normalize_pos(
                    locals()[f'shift{index}']
                ))
                + np.array([
                    0, 0, max(0, height_shift - kwargs[f'radius{index}'])
                ])
            )
        kwargs['slope'] = 'down'
        self._update_joint_spheres(**kwargs)

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
            message ++ str(only_avoid)
            raise ValueError(message)
        return only_avoid

    '''
    general methods
    '''

    def get_volume_list(
            self: Self,
            only: Any = None,
            avoid: Any = [],
        ) -> list:
        # returns the list of all volumes satifying the conditions
        only = self._only_avoid_to_list(only) 
        avoid = self._only_avoid_to_list(avoid) 
        return [volume for volume in only if volume not in avoid]

    def new_sphere(
            self: Self,
            *args,
            **kwargs,
        ) -> Self:
        # creates the basis for a new sphere
        return self._create_volume('sphere', *args, **kwargs)

    def new_tube(
            self: Self,
            *args,
            **kwargs,
        ) -> Self:
        # creates the basis for a new sphere
        return self._create_volume('tube', *args, **kwargs)

    def update(
            self: Self,
            only: Any = None,
            avoid: Any = [],
            **kwargs,
        ) -> Self:
        # updates the state of the image
        volume_list = self.get_volume_list(only, avoid)
        for volume in volume_list:
            volume_kwargs = self._volumes[volume]
            volume_kwargs.update(kwargs)
            self._update_volume(**volume_kwargs)
        return self

    '''
    main method
    '''

    def main(
            self: Self,
        ) -> None:
        # the main running function
        pass
