import numpy as np
from typing_extensions import Any, Self

from ._motion2_change_radius import _MotionChangeRadius


class _MotionMovement(_MotionChangeRadius):

    '''
    static methods
    '''

    @staticmethod
    def _path_to_norm(
            path: np.array,
        ) -> np.array:
        assert len(path.shape) == 2
        if path.shape[0] <= 1:
            return np.array([0])
        norm = np.sum((path[1:] - path[:-1])**2, axis=-1)**0.5
        norm = np.concatenate([
            np.array([0]),
            np.cumsum(norm),
        ])
        divider = norm[-1]
        if not divider:
            divider = 1
        return norm/divider

    @staticmethod
    def _normed_path_to_pos(
            ratio: float,
            path: np.array = np.array([[0], [0]]),
            norm: np.array = np.array([0]),
        ) -> (float, float, float):
        assert norm[0] == 0
        assert norm[-1] == 1 or norm[-1] == 0
        if norm[-1] == 0:
            return tuple(path[0])
        ratio = max(0, min(1, ratio))
        start = np.where(norm <= ratio)[0][-1]
        end = np.where(norm >= ratio)[0][0]
        divider = norm[end] - norm[start]
        if not divider:
            divider = 1
        ratio = (ratio - norm[start])/divider
        start = path[start]
        end = path[end]
        pos = start + ratio*(end - start)
        return pos[0], pos[1], pos[2]

    '''
    hidden methods
    '''

    def _smooth_movement(
            self: Self,
            duration: int,
            path: np.array,
            norm: np.array,
            initial_speed: Any = (0, 0, 0),
            frequency: float = None,
            damping: float = None,
            response: float = None,
            batch_size: int = None,
            position_threshold: float = None,
            speed_threshold: float = None,
            rigid: bool = False,
            **kwargs
        ) -> dict:
        # see https://www.youtube.com/watch?v=KPoeNZZ6H4s
        if frequency is None:
            frequency = self.movement_frequency
        if damping is None:
            damping = self.movement_damping
        if response is None:
            response = self.movement_response
        if batch_size is None:
            batch_size = self.movement_batch_size
        if position_threshold is None:
            position_threshold = self.movement_position_threshold
        position_threshold = position_threshold**2
        if speed_threshold is None:
            speed_threshold = self.movement_speed_threshold
        speed_threshold = speed_threshold**2
        k1 = damping/np.pi/frequency
        k2 = 1/(2*np.pi*frequency)**2
        k3 = response*damping/2/np.pi/frequency
        positions = []
        current_pos = path[0].astype(float)
        current_speed = np.array(initial_speed).astype(float)
        current_puller = path[0]
        for index in range(duration + 1):
            for batch_index in range(batch_size):
                next_puller = np.array(self._normed_path_to_pos(
                    ratio=(index + batch_index/batch_size)/duration,
                    path=path,
                    norm=norm,
                ))
                if rigid:
                    current_pos = next_puller
                    current_speed = np.zeros(3)
                else:
                    current_pos += current_speed/self.fps/batch_size
                    current_speed += k3*(next_puller - current_puller) + (
                        next_puller - current_pos - k1*current_speed
                    )/self.fps/batch_size/k2
                current_puller = next_puller.copy()
            positions.append(current_pos.copy())
        end_pos = path[-1]
        while (
                np.sum((current_pos - end_pos)**2) > position_threshold
                or
                np.sum(current_speed**2) > speed_threshold
            ) and not rigid:
            for batch_index in range(batch_size):
                current_pos += current_speed/self.fps/batch_size
                current_speed += (
                    end_pos - current_pos - k1*current_speed
                )/self.fps/batch_size/k2
            positions.append(current_pos.copy())
        positions.append(end_pos.copy())
        kwargs['duration'] = len(positions) - 1
        kwargs['pos_list'] = [tuple(pos) for pos in positions]
        return kwargs

    def _add_movement_one_pos(
            self: Self,
            volume: Any,
            pos: tuple[float] = None,
            path: list = None,
            shifted: bool = False,
            normalize: bool = True,
            **kwargs,
        ) -> None:
        # creates the movement of a volume with a single pos
        origin = self._normalize_pos(self._volumes[volume].get('pos', (0, 0)))
        if pos is not None:
            if shifted:
                path = [(0, 0), pos]
            else:
                path = [origin, pos]
        assert path is not None
        path = np.stack([self._normalize_pos(pos) for pos in path])
        if shifted:
            path = np.array(origin).reshape(1, 3) + path
        path[:,-1] = path[:,-1]*(path[:,-1] > 0)
        if normalize:
            norm = self._path_to_norm(path)
        else:
            norm = len(path)
            if norm <= 1:
                norm = 2
            norm = np.arange(norm)/(norm - 1)
        motion = {
            'volume' : volume,
            'path' : path,
            'norm' : norm,
        }
        motion.update(kwargs)
        self._add_motion(self._smooth_movement(**motion))

    def _add_movement_sphere(
            self: Self,
            *args,
            **kwargs,
        ) -> None:
        # creates the movement of a sphere
        self._add_movement_one_pos(*args, **kwargs)

    def _add_movement_polyhedron(
            self: Self,
            *args,
            **kwargs,
        ) -> None:
        # creates the movement of a polyhedron
        self._add_movement_one_pos(*args, **kwargs)

    def _apply_movement_one_pos(
            self: Self,
            volume: Any,
            step: int,
            duration: int,
            pos_list: list,
        ) -> None:
        # moves a volume with a single pos
        pos = pos_list[step]
        self._volumes[volume]['pos'] = (
            pos[0],
            pos[1],
            abs(pos[2]),
        )

    def _apply_movement_sphere(
            self: Self,
            *args,
            **kwargs
        ) -> None:
        # moves a sphere
        self._apply_movement_one_pos(*args, **kwargs)

    def _apply_movement_polyhedron(
            self: Self,
            *args,
            **kwargs
        ) -> None:
        # moves a sphere
        self._apply_movement_one_pos(*args, **kwargs)

    def _add_rotate_polyhedron(
            self: Self,
            volume: Any,
            pos: tuple[float] = None,
            path: list = None,
            shifted: bool = False,
            normalize: bool = True,
            **kwargs,
        ) -> None:
        # creates the rotation for a polyhedron
        origin = self._normalize_pos(self._volumes[volume].get('pos', (0, 0)))
        if pos is not None:
            if shifted:
                path = [(0, 0), pos]
            else:
                path = [origin, pos]
        assert path is not None
        path = np.stack([self._normalize_pos(pos) for pos in path])
        if shifted:
            path = np.array(origin).reshape(1, 3) + path
        path[:,-1] = path[:,-1]*(path[:,-1] > 0)
        if normalize:
            norm = self._path_to_norm(path)
        else:
            norm = len(path)
            if norm <= 1:
                norm = 2
            norm = np.arange(norm)/(norm - 1)
        motion = {
            'volume' : volume,
            'path' : path,
            'norm' : norm,
        }
        motion.update(kwargs)
        self._add_motion(self._smooth_movement(**motion))

