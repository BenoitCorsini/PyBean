from typing_extensions import Any, Self

from ._motion import _Motion


class _MotionChangeAlpha(_Motion):

    '''
    hidden methods
    '''

    def _add_change_alpha_(
            self: Self,
            volume: Any,
            start_with: float = 1,
            end_with: float = 1,
            **kwargs,
        ) -> None:
        # creates the motion to change the alpha of any volume
        if start_with == end_with:
            return None
        motion = {
            'volume' : volume,
        }
        motion.update(kwargs)
        alpha = self._volumes[volume].get('alpha', 1)
        for timing in ['start', 'end']:
            timing_with = locals()[f'{timing}_with']
            if timing_with >= 0:
                motion[f'{timing}_alpha'] = alpha*timing_with
            else:
                motion[f'{timing}_alpha'] = abs(timing_with)
        self._add_motion(motion)

    def _add_change_alpha_sphere(
            self: Self,
            *args,
            **kwargs,
        ) -> None:
        # changes the alpha of a sphere
        self._add_change_alpha_(*args, **kwargs)

    def _add_change_alpha_tube(
            self: Self,
            *args,
            **kwargs,
        ) -> None:
        # changes the alpha of a tube
        self._add_change_alpha_(*args, **kwargs)

    def _apply_change_alpha_(
            self: Self,
            volume: Any,
            step: int,
            duration: int,
            start_alpha: float,
            end_alpha: float,
        ) -> None:
        # changes the alpha of any volume
        alpha = start_alpha + (end_alpha - start_alpha)*step/duration
        self._volumes[volume]['alpha'] = alpha

    def _apply_change_alpha_sphere(
            self: Self,
            *args,
            **kwargs
        ) -> None:
        # changes the alpha of a sphere
        self._apply_change_alpha_(*args, **kwargs)

    def _apply_change_alpha_tube(
            self: Self,
            *args,
            **kwargs
        ) -> None:
        # changes the alpha of a tube
        self._apply_change_alpha_(*args, **kwargs)