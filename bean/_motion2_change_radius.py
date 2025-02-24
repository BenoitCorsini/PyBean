from typing_extensions import Any, Self

from ._motion1_change_alpha import _MotionChangeAlpha


class _MotionChangeRadius(_MotionChangeAlpha):

    '''
    hidden methods
    '''

    def _add_change_radius_one_pos(
            self: Self,
            volume: Any,
            start_with: float = 1,
            end_with: float = 1,
            centred: bool = True,
            **kwargs,
        ) -> None:
        # creates a motion to change the radius of a volume with a single pos
        if start_with == end_with:
            return None
        motion = {
            'volume' : volume,
            'centred' : centred,
        }
        motion.update(kwargs)
        radius = self._volumes[volume].get('radius', 1)
        for timing in ['start', 'end']:
            timing_with = locals()[f'{timing}_with']
            if timing_with >= 0:
                motion[f'{timing}_radius'] = radius*timing_with
            else:
                motion[f'{timing}_radius'] = abs(timing_with)
        self._add_motion(motion)

    def _add_change_radius_two_pos(
            self: Self,
            volume: Any,
            start_with: Any = 1,
            end_with: Any = 1,
            centred: Any = True,
            **kwargs,
        ) -> None:
        # creates a motion to change the radius of a volume with two pos
        if start_with == end_with:
            return None
        if isinstance(centred, bool):
            centred = (centred, centred)
        motion = {
            'volume' : volume,
            'centred1' : centred[0],
            'centred2' : centred[1],
        }
        motion.update(kwargs)
        radius = self._volumes[volume].get('radius', 1)
        variables = {}
        if isinstance(radius, int) or isinstance(radius, float):
            radius = (radius, radius)
        for timing in ['start', 'end']:
            timing_with = locals()[f'{timing}_with']
            if isinstance(timing_with, int) or isinstance(timing_with, float):
                timing_with = (timing_with, timing_with)
            for index in [0, 1]:
                motion_key = f'{timing}_radius{1 + index}'
                if timing_with[index] >= 0:
                    motion[motion_key] = radius[index]*timing_with[index]
                else:
                    motion[motion_key] = abs(timing_with[index])
        self._add_motion(motion)

    def _add_change_radius_sphere(
            self: Self,
            *args,
            **kwargs
        ) -> None:
        # creates a motion to change the radius of a sphere
        self._add_change_radius_one_pos(*args, **kwargs)

    def _add_change_radius_tube(
            self: Self,
            *args,
            **kwargs
        ) -> None:
        # creates a motion to change the radius of a tube
        self._add_change_radius_two_pos(*args, **kwargs)

    def _add_change_radius_polyhedron(
            self: Self,
            *args,
            **kwargs
        ) -> None:
        # creates a motion to change the radius of a polyhedron
        self._add_change_radius_one_pos(*args, **kwargs)

    def _apply_change_radius_one_pos(
            self: Self,
            volume: Any,
            step: int,
            duration: int,
            start_radius: float,
            end_radius: float,
            centred: bool,
        ) -> None:
        # changes the radius of a volume with a singe pos
        delta_radius = (end_radius - start_radius)/duration
        radius = start_radius + step*delta_radius
        pos = self._normalize_pos(self._volumes[volume]['pos'])
        if centred:
            if step:
                delta_altitude = delta_radius
            elif start_radius != self._volumes[volume]['radius']:
                delta_altitude = min(0, start_radius -  end_radius)
            else:
                delta_altitude = 0
            self._volumes[volume]['pos'] = (
                pos[0],
                pos[1],
                pos[2] - delta_altitude,
            )
        self._volumes[volume]['radius'] = radius

    def _apply_change_radius_two_pos(
            self: Self,
            volume: Any,
            step: int,
            duration: int,
            start_radius1: float,
            end_radius1: float,
            centred1: bool,
            start_radius2: float,
            end_radius2: float,
            centred2: bool,
        ) -> None:
        # changes the radius of a volume with two pos
        radius = self._volumes[volume]['radius']
        if isinstance(radius, int) or isinstance(radius, float):
            radius = (radius, radius)
        variables = {}
        for index in [1, 2]:
            start_radius = locals()[f'start_radius{index}']
            end_radius = locals()[f'end_radius{index}']
            delta_radius = (end_radius - start_radius)/duration
            radius = start_radius + step*delta_radius
            if self._volumes[volume].get(f'key{index}', None) is not None:
                pos = None
            else:
                pos = self._normalize_pos(
                    self._volumes[volume].get(f'shift{index}', None)
                )
            if pos is not None and centred:
                if step:
                    delta_altitude = delta_radius
                elif start_radius != radius[index - 1]:
                    delta_altitude = min(0, start_radius -  end_radius)
                else:
                    delta_altitude = 0
                self._volumes[volume][f'shift{index}'] = (
                    pos[0],
                    pos[1],
                    pos[2] - delta_altitude,
                )
            variables[f'radius{index}'] = radius
        self._volumes[volume]['radius'] = (
            variables['radius1'],
            variables['radius2'],
        )

    def _apply_change_radius_sphere(
            self: Self,
            *args,
            **kwargs
        ) -> None:
        # changes the radius of a sphere
        self._apply_change_radius_one_pos(*args, **kwargs)

    def _apply_change_radius_tube(
            self: Self,
            *args,
            **kwargs
        ) -> None:
        # changes the radius of a tube
        self._apply_change_radius_two_pos(*args, **kwargs)

    def _apply_change_radius_polyhedron(
            self: Self,
            *args,
            **kwargs
        ) -> None:
        # changes the radius of a tube
        self._apply_change_radius_one_pos(*args, **kwargs)