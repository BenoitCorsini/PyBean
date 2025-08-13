import itertools
import numpy as np
from matplotlib.path import Path
from typing_extensions import Any, Self

from .brush import Brush
from .polyhedron import Polyhedron


class Volume(Brush):

    '''
    fundamental variables and function
    '''

    draft = False
    scale = 1
    view_dist = 4
    view_height = 2
    view_angle = -25
    view_rotation = 0
    view_screen = 2
    sun_direction = (0.5, 0.25, -1)
    shade_colour = Brush.hsl(saturation=0, lightness=0)
    shade_opacity = 1e-1
    overlay_colour = Brush.hsl(saturation=0, lightness=0)
    overlay_opacity = 5e-2
    _sun_colour = Brush.hsl(hue=0.17, saturation=1, lightness=0.8)
    _sun_lightness = 0.3
    _sun_darkness = 0.9
    _screen_thr = 2

    _volume_params = {
        'draft' : bool,
    }

    def _init_volume(
            self: Self,
        ) -> Self:
        # new volume instance
        self._volumes = {}
        self._volume_index = 0
        self.__set_view__()
        self.set_sun()
        return self

    '''
    hidden methods
    '''

    def set_view(self, dist=None, height=None, angle=None, rotation=None, screen=None):
        if dist is not None:
            self.view_dist = dist
        if height is not None:
            self.view_height = height
        if angle is not None:
            self.view_angle = angle
        if rotation is not None:
            self.view_rotation = rotation
        if screen is not None:
            self.view_screen = screen
        self.__set_view__()
        return self

    def __set_view__(self):
        rotation = np.pi*self.view_rotation/180
        self.view_pos = np.array([[
            -self.view_dist*np.sin(rotation),
            -self.view_dist*np.cos(rotation),
            self.view_height,
        ]])
        if self.view_angle is None:
            look_dir = (self.view_dist**2 + self.view_height**2)**0.5
            look_dir = (
                self.view_dist/look_dir,
                -self.view_height/look_dir,
            )
        else:
            angle = np.pi*self.view_angle/180
            look_dir = (
                np.cos(angle),
                np.sin(angle),
            )
        self._screenx = np.array([[
            np.cos(rotation),
            -np.sin(rotation),
            0,
        ]])
        self._screeny = np.array([[
            -look_dir[1]*np.sin(rotation),
            -look_dir[1]*np.cos(rotation),
            look_dir[0],
        ]])
        self._screenz = np.array([[
            look_dir[0]*np.sin(rotation),
            look_dir[0]*np.cos(rotation),
            look_dir[1],
        ]])
        return self

    @staticmethod
    def _expand(points):
        points = np.array(points)
        if len(points.shape) < 2:
            return points.reshape((1, np.size(points)))
        else:
            return points

    def set_sun(self, sun_direction=None):
        if sun_direction is None:
            sun_direction = self.sun_direction
        self.sun_direction = Polyhedron._unitary(self._expand(sun_direction))
        return self

    def _project(
            self: Self,
            pos: np.array = np.zeros(3),
        ) -> np.array:
        # project a position relative to the viewer and the screen
        pos = self._expand(pos) - self.view_pos
        return np.stack([
            np.sum(pos*self._screenx, axis=1),
            np.sum(pos*self._screeny, axis=1),
            np.sum(pos*self._screenz, axis=1),
        ], axis=1)

    def _xy(
            self: Self,
            pos: np.array = np.zeros(3),
        ) -> np.array:
        # transforms a 3D position into a 2D coordinate
        x, y, z = self._project(pos).T
        pre_screen = (z < self.view_screen/self._screen_thr)*self._screen_thr
        post_screen = (z >= self.view_screen/self._screen_thr)
        mult = pre_screen*np.exp(self.view_screen/self._screen_thr - z)
        mult += post_screen*self.view_screen/z
        return self.figxy(np.stack([
            0.5 + mult*x,
            0.5 + mult*y*self.figsize[0]/self.figsize[1],
        ], axis=1))

    def _to_shade(
            self: Self,
            pos: np.array = np.zeros(3),
        ) -> np.array:
        # transforms a 3D position into its projection on the ground
        pos = self._expand(pos)
        if self.sun_direction[:,2] >= 0:
            return np.zeros_like(pos)
        ground_dist = pos[:,2:]/self.sun_direction[:,2]
        return pos - ground_dist*self.sun_direction

    def _face_brush(self, key):
        self.new_brush(
            brush_name='Polygon',
            key=key,
            xy=[(0, 0)],
            lw=1,
            capstyle='round',
            joinstyle='round',
        )

    def _shade_brush(self, key):
        self.new_path_from_raw(
            key=key,
            vertices=[(0, 0)],
            lw=0,
            capstyle='round',
            joinstyle='round',
            zorder=0,
        )


    '''
    general methods
    '''

    def _volume(
            self: Self,
            key: Any = None,
            polyhedron: Polyhedron = None,
            pos: tuple[float] = None,
            scale: float = None,
            axis: np.array = None,
            angle: float = None,
            **kwargs,
        ) -> Self:
        # creates a new volume
        key, available = self.check_key(key)
        if available:
            main = [
                f'{key}_main{index}'
                for index in range(len(polyhedron))
            ]
            shade = f'{key}_shade'
            overlay = [{
                volume_key : f'{key}_overlay{index}_{volume_key}'
                for volume_key in self._volumes
            } for index in range(len(polyhedron))]
            volume = {
                'key' : key,
                'polyhedron' : polyhedron.modify(
                    pos=pos,
                    scale=scale,
                    axis=axis,
                    angle=angle,
                ),
                'main' : main,
                'shade' : shade,
                'overlay' : overlay
            }
            for brush_key in main:
                self._face_brush(brush_key)
            self._shade_brush(shade)
            for face_info in overlay:
                for brush_key in face_info.values():
                    self._shade_brush(brush_key)
            for param in itertools.product(['shade', 'overlay'], ['colour', 'opacity']):
                param = f'{param[0]}_{param[1]}'
                kwargs[param] = kwargs.get(param, getattr(self, param))
            volume.update(**kwargs)
            for other_key, other_volume in self._volumes.items():
                for index in range(len(other_volume['polyhedron'])):
                    overlay_key = f'{other_key}_overlay{index}_{key}'
                    other_volume['overlay'][index].update({
                        key : overlay_key
                    })
                    self._shade_brush(overlay_key)
            self._volumes[key] = volume
        else:
            volume = self._volumes[key]
        self._update_volume(**volume)
        self._overlay([volume['key']])
        return self

    def _ortho_to_colour(self, ortho, colour):
        ratio = np.sum(ortho*self.sun_direction, axis=1)
        ratio = 0.5 + ratio/2
        ratio *= self._sun_darkness - self._sun_lightness
        ratio += self._sun_lightness
        return self.cscale(colour, start_with=self._sun_colour)(ratio)

    def _update_volume(
            self: Self,
            name: str,
            key: Any,
            polyhedron: Polyhedron,
            main: list[Any],
            shade: Any,
            overlay: list[Any],
            colour: Any = Brush.hsl(),
            shade_colour: Any = 'black',
            overlay_colour: Any = 'black',
            opacity: float = 1,
            shade_opacity: float = 1,
            overlay_opacity: float = 1,
            visible: bool = True,
        ) -> Self:
        # updates a given volume
        points = self.scale*polyhedron.get_points()
        centres = self.scale*polyhedron.get_centres()
        orthos = polyhedron.get_orthos()
        xy = self._xy(points)
        shade_xy = self._xy(self._to_shade(points))
        if self.view_height >= 0:
            zorders = 1/(self.view_screen + self._project(centres)[:,2])
        else:
            zorders = -(self.view_screen + self._project(centres)[:,2])
        colours = self._ortho_to_colour(orthos, colour)
        visibles = np.sum(orthos*(centres - self.view_pos), axis=1) <= 0
        positive_sun = np.sum(orthos*self.sun_direction, axis=1) <= 0
        shade_vertices = []
        shade_codes = []
        for brush_key, (index, face) in zip(main, enumerate(polyhedron)):
            self.set(
                key=brush_key,
                xy=xy[face],
                zorder=zorders[index],
                color=colours[index],
                alpha=opacity,
                visible=visible and visibles[index],
            )
            for overlay_volume, overlay_key in overlay[index].items():
                self.set(
                    key=overlay_key,
                    zorder=zorders[index],
                    color=self._volumes[overlay_volume]['overlay_colour'],
                    alpha=self._volumes[overlay_volume].get('opacity', 1)*self._volumes[overlay_volume]['overlay_opacity'],
                    visible=self._volumes[overlay_volume].get('opacity', True) and visibles[index],
                )
            if not positive_sun[index]:
                face = face[::-1]
            shade_vertices.append(shade_xy[face + [0]])
            shade_codes += [1] + [2]*(len(face) - 1) + [79]
        self.set(
            key=shade,
            path=Path(
                vertices=np.concatenate(shade_vertices),
                codes=shade_codes,
            ),
            color=shade_colour,
            alpha=opacity*shade_opacity,
            visible=visible,
        )

    def new_cube(
            self: Self,
            key: Any = None,
            **kwargs,
        ) -> Self:
        # creates a new cube
        self._volume(name='cube', key=key, polyhedron=Polyhedron.cube(), **kwargs)

    def new_pyramid(
            self: Self,
            key: Any = None,
            height: float = 1,
            base: np.array = None,
            **kwargs,
        ) -> Self:
        # creates a new cube
        self._volume(name='pyramid', key=key, polyhedron=Polyhedron.pyramid(height, base), **kwargs)

    def new_polysphere(
            self: Self,
            key: Any = None,
            precision: int = -1,
            **kwargs,
        ) -> Self:
        # creates a new cube
        self._volume(name='polysphere', key=key, polyhedron=Polyhedron.polysphere(precision), **kwargs)

    def _list(
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

    def volumes(
            self: Self,
            only: Any = None,
            avoid: Any = [],
        ) -> list:
        # returns the list of all volumes satifying the conditions
        only = self._list(only) 
        avoid = self._list(avoid) 
        return [volume for volume in only if volume not in avoid]

    def update(
            self: Self,
            only: Any = None,
            avoid: Any = [],
            pos: tuple[float] = None,
            scale: float = None,
            axis: np.array = None,
            angle: float = None,
            **kwargs,
        ) -> list:
        # returns the list of all volumes satifying the conditions
        volumes = self.volumes(only, avoid)
        for volume in volumes:
            self._volumes[volume]['polyhedron'].modify(
                pos=pos,
                scale=scale,
                axis=axis,
                angle=angle,
            )
            self._volumes[volume].update(**kwargs)
            self._update_volume(**self._volumes[volume])
        self._overlay(volumes)

    def _overlay(self, volumes):
        if not volumes:
            return None
        for vol1 in self._volumes.values():
            key1 = vol1['key']
            poly1 = vol1['polyhedron']
            pts1 = self.scale*poly1.get_points()
            xy1 = self._xy(pts1)
            centres = self.scale*poly1.get_centres()
            orthos = poly1.get_orthos()
            for vol2 in self._volumes.values():
                key2 = vol2['key']
                poly2 = vol2['polyhedron']
                pts2 = self.scale*poly2.get_points()
                if key1 == key2:
                    continue
                if key1 not in volumes and key2 not in volumes:
                    continue
                for index, face in enumerate(poly1):
                    centre = centres[index].reshape((1, 3))
                    ortho = orthos[index].reshape((1, 3))
                    sun_ortho = np.sum(self.sun_direction*ortho)
                    if sun_ortho >= 0:
                        continue
                    positive = np.sum(ortho*poly2.orthos, axis=1) >= 0
                    overlay_vertices = []
                    overlay_codes = []
                    overlay_key = f'{key1}_overlay{index}_{key2}'
                    for over_index, over_face in enumerate(poly2):
                        if positive[over_index]:
                            over_face = over_face[::-1]
                        over_pts = pts2[over_face]
                        projs = centre - over_pts
                        projs = np.sum(projs*ortho, axis=1, keepdims=True)
                        projs /= sun_ortho
                        not_ignore = projs[:,0] >= 0
                        projs = over_pts + projs*self.sun_direction
                        projs = projs[not_ignore,:]
                        if not np.size(projs):
                            continue
                        overlay_vertices.append(self._xy(projs))
                        overlay_vertices.append(np.zeros((1, 2)))
                        overlay_codes += [1] + [2]*(len(projs) - 1) + [79]
                    if not overlay_codes:
                        continue
                    self.set(
                        key=f'{key1}_overlay{index}_{key2}',
                        path=Path(
                            vertices=np.concatenate(overlay_vertices),
                            codes=overlay_codes,
                        ),
                        clip_path=self._brushs[f'{key1}_main{index}'],
                    )




