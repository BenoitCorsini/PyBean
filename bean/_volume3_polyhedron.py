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
            'shade' : [
                f'{available_key}_shade{index}'
                for index, _ in enumerate(faces)
            ],
        }
        for shape_type, shape_keys in volume.items():
            for shape_key in shape_keys:
                patch = self.add_shape(
                    shape_name='Polygon',
                    key=shape_key,
                    xy=[(0, 0)],
                    lw=0,
                    zorder=0,
                )
                if shape_type == 'shade':
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
            pass
            # shade_xy = [
            #     [self._pos_to_xy(self._pos_to_shade_pos(pos)) for pos in face]
            #     for face in faces
            # ]
        faces = [
            [self._pos_to_xy(pos) for pos in face]
            for face in faces
        ]
        if colour is None:
            colour = (lambda x : None)
        else:
            colour = self.get_cmap([colour, 'black'])
        for key, face, centre, ortho in zip(main, faces, centres, orthos):
            sun_impact = (1 + np.sum(ortho*self.sun_direction))/2
            self.apply_to_shape('set_xy', key=key, xy=face)
            self.set_shape(
                key=key,
                color=colour(sun_impact*self.side_cmap_ratio),
                zorder=self._pos_to_scale(centre),
                alpha=alpha,
            )