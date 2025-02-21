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
            **kwargs
        ) -> dict:
        # creates the volume dictionary for a polyhedron
        volume = {
            'main' : [
                f'{available_key}_main{index}'
                for index, _ in enumerate(faces)
            ],
            'shade' : f'{available_key}_shade',
        }
        for shape_key in volume.values():
            if isinstance(shape_key, str):
                shape_keys = [shape_key]
            else:
                shape_keys = shape_key
            for shape_key in shape_keys:
                patch = self.add_shape(
                    shape_name='Polygon',
                    key=shape_key,
                    xy=[(0, 0)],
                    lw=0,
                    zorder=0,
                )
                if shape_key.endswith('_shade'):
                    patch.set_visible(not self.draft)
                    patch.set_zorder(-1)
        volume['faces'] = faces
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

    def _update_polyhedron(
            self: Self,
            main: list[str],
            shade: str,
            pos: tuple[float] = None,
            points: list[tuple[float]] = [(0, 0)],
            faces: list[list[int]] = [[0]],
            transform: np.array = np.eye(3),
            radius: float = 1,
            colour: str = None,
            shade_colour: str = None,
            visible: bool = True,
            alpha: float = 1,
        ) -> None:
        # updates the sphere
        if not visible:
            for key in main:
                self.set_shape(key=key, visible=False)
            self.set_shape(key=shade, visible=False)
            return None
        points = np.array([self._normalize_pos(point) for point in points])
        centre = np.mean(points, axis=0, keepdims=True)
        points = radius*(points - centre)
        points = points @ transform.T
        if pos is None:
            shift = np.zeros((1, 3))
        else:
            pos = np.array(self._normalize_pos(pos))
            shift = pos.reshape((1, 3)) - centre
        points = shift + centre + points
        faces = [points[face] for face in faces]
        orthos = [self._face_orthogonal(face) for face in faces]
        centres = [np.mean(face, axis=0) for face in faces]
        if not self.draft:
            shade_xy = [
                [self._pos_to_xy(self._pos_to_shade_pos(pos)) for pos in face]
                for face in faces
            ]
        faces = [
            [self._pos_to_xy(pos) for pos in face]
            for face in faces
        ]
        for key, face, centre, ortho in zip(main, faces, centres, orthos):
            self.apply_to_shape('set_xy', key=key, xy=face)
            self.set_shape(
                key=key,
                color=colour,
                zorder=self._pos_to_scale(centre),
                alpha=alpha,
            )
        return None
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
            side_angle = self.angle_from_xy(
                xy1=xy,
                xy2=shade_xy,
                default_angle=self.shade_angle - 90,
            )
            for key, ratio in zip(side, self.round_sides):
                path = self.merge_curves(*self.crescent_paths(
                    xy=xy,
                    radius=radius,
                    ratio=ratio,
                    theta1=270,
                    theta2=90,
                    angle=side_angle,
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