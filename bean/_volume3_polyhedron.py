import json
import os.path as osp
import numpy as np
from typing_extensions import Any, Self

from ._volume2_tube import _VolumeTube


class _VolumePolyhedron(_VolumeTube):

    '''
    hidden methods
    '''

    def _create_polyhedron(
            self: Self,
            available_key: Any,
            faces: list[list[int]] = [[0]],
            transform: np.array = np.eye(3),
            **kwargs
        ) -> dict:
        # creates the volume dictionary for a polyhedron
        volume = {
            '_main' : [
                f'{available_key}_main{index}'
                for index, _ in enumerate(faces)
            ],
            '_shade' : [
                f'{available_key}_shade{index}'
                for index, _ in enumerate(faces)
            ],
        }
        for shape_type, shape_keys in volume.items():
            for shape_key in shape_keys:
                patch = self.add_brush(
                    brush_name='Polygon',
                    key=shape_key,
                    xy=[(0, 0)],
                    lw=self._polyhedron_lw,
                    zorder=0,
                    joinstyle='round',
                    capstyle='round',
                )
                if shape_type == '_shade':
                    patch.set_visible(not self.draft)
                    patch.set_zorder(-1)
        text_key = f'{available_key}_text'
        self.add_raw_path(key=text_key, visible=False)
        volume['_text'] = text_key
        volume['faces'] = faces
        volume['transform'] = transform
        return volume

    @staticmethod
    def _face_orthogonal(
            face: np.array,
        ) -> np.array:
        # computes the orthogonal direction of a face
        ortho = face[1:] - face[:-1]
        ortho = [
            np.cross(vec1, vec2)
            for (vec1, vec2) in zip(ortho[:-1], ortho[1:])
        ]
        ortho = np.sum(ortho, axis=0)
        norm = np.sum(ortho**2)**0.5
        if not norm:
            norm = 1.
        return ortho/norm

    @staticmethod
    def _polyhedron_sphere(
            precision: int,
        ) -> (np.array, list[list[int]]):
        # returns a polyhedron approximation of a sphere
        file_name = _VolumeTube.to_bean(f'__ps{precision}__.json')
        if osp.exists(file_name):
            with open(file_name) as ps:
                ps_dict = json.load(ps)
                points = ps_dict['points']
                faces = ps_dict['faces']
                ps.close()
        else:
            (
                previous_points,
                previous_faces
            ) = _VolumePolyhedron._polyhedron_sphere(precision - 1)
            points = list(previous_points)
            faces = []
            mids = {}
            new_index = len(points)
            for [a, b, c] in previous_faces:
                for (x, y) in [(a, b), (b, c), (c, a)]:
                    if (x, y) not in mids:
                        mid = np.mean(previous_points[[x, y]], axis=0)
                        mid /= np.sum(mid**2)**0.5
                        points.append(mid)
                        mids[x, y] = new_index
                        mids[y, x] = new_index
                        new_index += 1
                faces.append([a, mids[a, b], mids[a, c]])
                faces.append([b, mids[b, c], mids[b, a]])
                faces.append([c, mids[c, a], mids[c, b]])
                faces.append([mids[a, b], mids[b, c], mids[c, a]])
            points = [tuple(point) for point in points]
            with open(file_name, 'w') as ps:
                json.dump({'points' : points, 'faces' : faces}, ps)
                ps.close()
        return np.array(points), faces

    def _update_polyhedron(
            self: Self,
            _main: list[str],
            _shade: list[str],
            _text: str,
            points: list[tuple[float]] = [(0, 0)],
            faces: list[list[int]] = [[0]],
            centre: tuple[float] = None,
            pos: tuple[float] = None,
            transform: np.array = np.eye(3),
            radius: float = 1,
            colour: str = None,
            shade_colour: str = None,
            visible: bool = True,
            opacity: float = 1,
        ) -> None:
        # updates the sphere
        self.set_brush(key=_text, visible=False)
        if not visible:
            for key in _main:
                self.set_brush(key=key, visible=False)
            self.set_brush(key=_shade, visible=False)
            return None
        points = np.array([self._normalize_pos(point) for point in points])
        if centre is None:
            centre = np.mean(points, axis=0, keepdims=True)
        else:
            centre = np.array(self._normalize_pos(centre)).reshape((1, 3))
        points = 2*radius*(points - centre)
        points = points @ transform.T
        if pos is None:
            shift = np.zeros((1, 3))
        else:
            pos = np.array(self._normalize_pos(pos))
            shift = pos.reshape((1, 3)) - centre
        points = shift + centre + points + np.array([0, 0, 2*radius*centre[0,-1]])
        points[:,2] -= min(np.min(points[:,2]), 0)
        faces = [points[face] for face in faces]
        orthos = [self._face_orthogonal(face) for face in faces]
        centres = [np.mean(face, axis=0) for face in faces]
        if not self.draft:
            shades_xy = [
                [self._pos_to_xy(self._pos_to_shade_pos(pos)) for pos in face]
                for face in faces
            ]
        faces = [
            [self._pos_to_xy(pos) for pos in face]
            for face in faces
        ]
        if colour is None:
            colour = 'grey'
        if not self.draft and shade_colour is None:
            shade_colour = self._get_shade_colour(colour)
        if not self.draft:
            colour = self.get_cmap([colour, 'black'])
        face_colour = colour
        max_zorder = 0
        for key, face, centre, ortho in zip(_main, faces, centres, orthos):
            if not self.draft:
                sun_impact = (1 + np.sum(ortho*self.sun_direction))/2
                face_colour = colour(sun_impact*self._side_cmap_ratio)
            self.apply_to_brush('set_xy', key=key, xy=face)
            zorder = self._pos_to_scale(centre)
            max_zorder = max(max_zorder, zorder)
            self.set_brush(
                key=key,
                color=face_colour,
                zorder=zorder,
                alpha=opacity,
            )
        if self.draft:
            self.set_brush(key=_text, zorder=max_zorder, **self._text_params)
            text_pos = np.mean(points, axis=0)
            height = self._text_height_ratio*radius*self.screen_dist*self.scale
            height *= self._pos_to_scale(text_pos)
            self.apply_to_brush(
                'set_path',
                key=_text,
                path=self.path_from_string(
                    s=_text[:-5],
                    xy=self._pos_to_xy(text_pos),
                    height=height,
                )
            )
        else:
            for key, shade_xy in zip(_shade, shades_xy):
                self.apply_to_brush('set_xy', key=key, xy=shade_xy)
                self.set_brush(key=key, color=shade_colour, alpha=opacity)
