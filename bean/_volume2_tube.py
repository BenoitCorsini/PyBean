import numpy as np
from typing_extensions import Any, Self

from ._volume1_sphere import _VolumeSphere


class _VolumeTube(_VolumeSphere):

    '''
    hidden methods
    '''

    def _create_tube(
            self: Self,
            available_key: Any,
            **kwargs,
        ) -> dict:
        # creates the volume dictionary of a tube
        return self._round_volume(available_key=available_key)

    def _update_joint_spheres(
            self: Self,
            _main: str,
            _side: list[str],
            _shade: str,
            _text: str,
            pos1: tuple[float] = (0, 0),
            pos2: tuple[float] = (0, 0),
            radius1: float = 1,
            radius2: float = 1,
            colour: str = None,
            shade_colour: str = None,
            slope: str = 'flat',
            visible: bool = True,
            opacity: float = 1,
        ) -> None:
        # updates the volume created by two spheres
        self.set_brush(key=_text, visible=False)
        if not visible:
            self.set_brush(key=_main, visible=False)
            for key in _side:
                self.set_brush(key=key, visible=False)
            self.set_brush(key=_shade, visible=False)
            return None
        variables = {}
        zorder = 0
        for index in [1, 2]:
            pos = locals()[f'pos{index}']
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
                variables[f'shade_pos{index}'] = shade_pos
                variables[f'shade_xy{index}'] = self._pos_to_xy(shade_pos)
                variables[f'shade_radius{index}'] = radius
                variables[f'scaled_radius{index}'] = (
                    radius
                    *self.screen_dist
                    *self.scale
                    *self._pos_to_scale(shade_pos)
                )
            scale = self._pos_to_scale(pos)
            variables[f'radius{index}'] = (
                radius*self.screen_dist*self.scale*scale
            )
            zorder += scale/2
        distance = self.distance_from_xy(variables['xy1'], variables['xy2'])
        delta_radius = variables['radius2'] - variables['radius1']
        is_sphere = np.abs(delta_radius) >= distance
        if is_sphere:
            sphere_index = 1 + int(delta_radius > 0)
            self.apply_to_brush('set_path', key=_main, path=self._curve_path(
                xy=variables[f'xy{sphere_index}'],
                a=variables[f'radius{sphere_index}'],
            ))
            angle = 0
            around_angle = 0
        else:
            angle = self.angle_from_xy(variables['xy1'], variables['xy2'])
            around_angle = np.arcsin(delta_radius/distance)*180/np.pi
            path = self._merge_curves(*[self._curve_path(
                xy=variables[f'xy{index}'],
                a=variables[f'radius{index}'],
                angle=angle,
                theta1=(3 - 2*index)*(90 + around_angle),
                theta2=(2*index - 3)*(90 + around_angle),
            ) for index in [1, 2]])
            self.apply_to_brush('set_path', key=_main, path=path)
        clipper = self.set_brush(
            key=_main,
            color=colour,
            zorder=zorder,
            alpha=opacity,
        )
        if self.draft:
            self.set_brush(key=_text, zorder=zorder, **self._text_params)
            self.apply_to_brush(
                'set_path',
                key=_text,
                path=self.path_from_string(
                    s=_text[:-5],
                    xy=(
                        (variables['xy1'][0] + variables['xy2'][0])/2,
                        (variables['xy1'][1] + variables['xy2'][1])/2,
                    ),
                    height=self._text_height_ratio*(
                        variables['radius1'] + variables['radius2']
                    )/2,
                )
            )
        else:
            side_angle1 = self.angle_from_xy(
                xy1=variables['xy1'],
                xy2=variables['shade_xy1'],
            )
            side_angle2 = self.angle_from_xy(
                xy1=variables['xy2'],
                xy2=variables['shade_xy2'],
            )
            side_angle = (side_angle1 + side_angle2)/2
            theta1 = self.normalize_angle(
                90 + around_angle + angle - side_angle
            )
            theta2 = self.normalize_angle(
                270 - around_angle + angle - side_angle
            )
            dark_index = 1 + int(self.normalize_angle(theta2 - theta1) > 0)
            for key, ratio in zip(_side, self._round_sides):
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
                    paths.append(self._crescent_paths(
                        ratio=ratio,
                        angle=side_angle,
                        **crescent
                    ))
                inners, outers = zip(*paths)
                path = self._merge_curves(*(inners[::-1] + outers))
                self.apply_to_brush('set_path', key=key, path=path)
                self.set_brush(
                    key=key,
                    clip_path=clipper,
                    zorder=zorder,
                    alpha=opacity*self._round_sides[ratio],
                )
            if shade_colour is None:
                shade_colour = self._get_shade_colour(clipper.get_fc())
            self.set_brush(key=_shade, color=shade_colour, alpha=opacity)
            distance = self.distance_from_xy(
                variables['shade_xy1'],
                variables['shade_xy2'],
            )
            delta_radius = (
                variables['scaled_radius2']
                - variables['scaled_radius1']
            )
            if np.abs(delta_radius) >= distance:
                index = 1 + int(delta_radius > 0)
                path = self._curve_path(
                    xy=variables[f'shade_pos{index}'],
                    a=variables[f'shade_radius{index}'],
                )
            else:
                shade_angle = self.angle_from_xy(
                    variables['shade_xy1'],
                    variables['shade_xy2'],
                )
                shade_around_angle = (
                    np.arcsin(delta_radius/distance)*180/np.pi
                )
                path = self._merge_curves(*[self._curve_path(
                    xy=variables[f'shade_pos{index}'],
                    a=variables[f'shade_radius{index}'],
                    theta1=(
                        (3 - 2*index)*(90 + shade_around_angle)
                        + shade_angle
                    ),
                    theta2=(
                        (2*index - 3)*(90 + shade_around_angle)
                        + shade_angle
                    ),
                ) for index in [1, 2]])
            path.vertices = np.array([
                self._pos_to_xy(pos) for pos in path.vertices
            ])
            self.apply_to_brush('set_path', key=_shade, path=path)

    def _update_tube(
            self: Self,
            key1: Any = None,
            key2: Any = None,
            shift1: tuple[float] = (0, 0),
            shift2: tuple[float] = (0, 0),
            radius: Any = 1,
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
            negative_space = space1 + space2 - norm
            radius_ratio = kwargs['radius1'] + kwargs['radius2']
            if not radius_ratio:
                radius_ratio = 1
            radius_ratio = 1 - negative_space/radius_ratio
            radius_ratio = max(0, radius_ratio)
            for index in [1, 2]:
                kwargs[f'radius{index}'] *= radius_ratio
            space1 -= negative_space/2
            space2 -= negative_space/2
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