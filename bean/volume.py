from typing_extensions import Any, Self

from ._volume3_polyhedron import _VolumePolyhedron


class Volume(_VolumePolyhedron):

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

    def new_polyhedron(
            self: Self,
            *args,
            **kwargs,
        ) -> Self:
        # creates the basis for a new polyhedron
        return self._create_volume('polyhedron', *args, **kwargs)

    def new_pylone(
            self: Self,
            basic_face: list[float, float],
            pylone_height: float = 1,
            *args,
            **kwargs,
        ) -> Self:
        # creates the basis for a new pylone
        n_points = len(basic_face)
        kwargs['points'] = [
            (x, y, pylone_height) for (x, y) in basic_face
        ]
        kwargs['points'] += [
            (x, y, 0) for (x, y) in basic_face
        ]
        kwargs['faces'] = [
            list(range(n_points)),
            list(range(n_points, 2*n_points))[::-1],
        ]
        for index in range(n_points):
            next_index = (index + 1) % n_points
            kwargs['faces'].append([
                next_index,
                index,
                index + n_points,
                next_index + n_points,
            ])
        return self._create_volume('polyhedron', *args, **kwargs)

    def new_cube(
            self: Self,
            *args,
            **kwargs,
        ) -> Self:
        # creates the basis for a new cube
        kwargs['points'] = [
            (0, 0, 0),
            (1, 0, 0),
            (1, 1, 0),
            (0, 1, 0),
            (0, 0, 1),
            (1, 0, 1),
            (1, 1, 1),
            (0, 1, 1),
        ]
        kwargs['faces'] = [
            [3, 2, 1, 0],
            [4, 5, 6, 7],
            [0, 1, 5, 4],
            [2, 3, 7, 6],
            [3, 0, 4, 7],
            [1, 2, 6, 5],
        ]
        return self._create_volume('polyhedron', *args, **kwargs)

    def new_pyramid(
            self: Self,
            pyramid_height: float = 1,
            *args,
            **kwargs,
        ) -> Self:
        # creates the basis for a new pyramid
        kwargs['points'] = [
            (0, 0, 0),
            (1, 0, 0),
            (1, 1, 0),
            (0, 1, 0),
            (0.5, 0.5, pyramid_height),
        ]
        kwargs['faces'] = [
            [3, 2, 1, 0],
            [0, 1, 4],
            [1, 2, 4],
            [2, 3, 4],
            [3, 0, 4],
        ]
        return self._create_volume('polyhedron', *args, **kwargs)

    def new_polysphere(
            self: Self,
            precision: int = 0,
            *args,
            **kwargs,
        ) -> Self:
        # creates the basis for a new pyramid
        points, faces = self._polyhedron_sphere(precision)
        kwargs['points'] = 0.5 + points/2
        kwargs['faces'] = faces
        return self._create_volume('polyhedron', *args, **kwargs)

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