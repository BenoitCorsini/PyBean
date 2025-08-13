from typing_extensions import Any, Self

from ._motion1_change_opacity import _MotionChangeOpacity


class _MotionChangeColour(_MotionChangeOpacity):

    '''
    hidden methods
    '''

    def _add_change_colour_(
            self: Self,
            volume: Any,
            start_with: Any = None,
            end_with: Any = None,
            colour_list: list = None,
            **kwargs,
        ) -> None:
        # creates the motion to change the colour of any volume
        if colour_list is None:
            if start_with is None:
                start_with = self._volumes[volume].get('colour', 'white')
            if end_with is None:
                end_with = self._volumes[volume].get('colour', 'white')
            if start_with == end_with:
                return None
            colour_list = [start_with, end_with]
        motion = {
            'volume' : volume,
        }
        motion.update(kwargs)
        motion['cmap'] = self.get_cmap(colour_list)
        self._add_motion(motion)

    def _add_change_colour_sphere(
            self: Self,
            *args,
            **kwargs,
        ) -> None:
        # changes the colour of a sphere
        self._add_change_colour_(*args, **kwargs)

    def _add_change_colour_tube(
            self: Self,
            *args,
            **kwargs,
        ) -> None:
        # changes the colour of a tube
        self._add_change_colour_(*args, **kwargs)

    def _add_change_colour_polyhedron(
            self: Self,
            *args,
            **kwargs,
        ) -> None:
        # changes the colour of a tube
        self._add_change_colour_(*args, **kwargs)

    def _apply_change_colour_(
            self: Self,
            volume: Any,
            step: int,
            duration: int,
            cmap: float,
        ) -> None:
        # changes the colour of any volume
        self._volumes[volume]['colour'] = cmap(float(step/duration))

    def _apply_change_colour_sphere(
            self: Self,
            *args,
            **kwargs
        ) -> None:
        # changes the colour of a sphere
        self._apply_change_colour_(*args, **kwargs)

    def _apply_change_colour_tube(
            self: Self,
            *args,
            **kwargs
        ) -> None:
        # changes the colour of a tube
        self._apply_change_colour_(*args, **kwargs)

    def _apply_change_colour_polyhedron(
            self: Self,
            *args,
            **kwargs
        ) -> None:
        # changes the colour of a tube
        self._apply_change_colour_(*args, **kwargs)