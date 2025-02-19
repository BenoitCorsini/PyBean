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
            n_faces: int = 1,
        ) -> dict:
        # creates the volume dictionary for a polyhedron
        volume = {
            'main' : [
                f'{available_key}_main{index}' for index in range(n_faces)
            ],
            'shade' : f'{available_key}_shade',
        }
        for shape_key in volume.values():
            if isinstance(shape_key, str):
                shape_keys = [shape_key]
            else:
                shape_keys = shape_key
            for shape_key in shape_keys:
                patch = self.add_raw_path(
                    key=shape_key,
                    vertices=[(0, 0)],
                    lw=0,
                    zorder=0,
                )
                if shape_key.endswith('_shade'):
                    patch.set_visible(not self.draft)
                    patch.set_zorder(-1)
        return volume

