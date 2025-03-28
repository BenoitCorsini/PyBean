from typing_extensions import Any, Self

from ._motion import _Motion


class _MotionChangeOpacity(_Motion):

    '''
    hidden methods
    '''

    def _add_change_opacity_(
            self: Self,
            volume: Any,
            start_with: float = 1,
            end_with: float = 1,
            **kwargs,
        ) -> None:
        # creates the motion to change the opacity of any volume
        if start_with == end_with:
            return None
        motion = {
            'volume' : volume,
        }
        motion.update(kwargs)
        opacity = self._volumes[volume].get('opacity', 1)
        for timing in ['start', 'end']:
            timing_with = locals()[f'{timing}_with']
            if timing_with >= 0:
                motion[f'{timing}_opacity'] = opacity*timing_with
            else:
                motion[f'{timing}_opacity'] = abs(timing_with)
        self._add_motion(motion)

    def _add_change_opacity_sphere(
            self: Self,
            *args,
            **kwargs,
        ) -> None:
        # changes the opacity of a sphere
        self._add_change_opacity_(*args, **kwargs)

    def _add_change_opacity_tube(
            self: Self,
            *args,
            **kwargs,
        ) -> None:
        # changes the opacity of a tube
        self._add_change_opacity_(*args, **kwargs)

    def _add_change_opacity_polyhedron(
            self: Self,
            *args,
            **kwargs,
        ) -> None:
        # changes the opacity of a tube
        self._add_change_opacity_(*args, **kwargs)

    def _apply_change_opacity_(
            self: Self,
            volume: Any,
            step: int,
            duration: int,
            start_opacity: float,
            end_opacity: float,
        ) -> None:
        # changes the opacity of any volume
        opacity = start_opacity + (end_opacity - start_opacity)*step/duration
        self._volumes[volume]['opacity'] = opacity

    def _apply_change_opacity_sphere(
            self: Self,
            *args,
            **kwargs
        ) -> None:
        # changes the opacity of a sphere
        self._apply_change_opacity_(*args, **kwargs)

    def _apply_change_opacity_tube(
            self: Self,
            *args,
            **kwargs
        ) -> None:
        # changes the opacity of a tube
        self._apply_change_opacity_(*args, **kwargs)

    def _apply_change_opacity_polyhedron(
            self: Self,
            *args,
            **kwargs
        ) -> None:
        # changes the opacity of a tube
        self._apply_change_opacity_(*args, **kwargs)