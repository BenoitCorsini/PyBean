import sys
import os
import os.path as osp
import numpy as np
import numpy.random as npr
import cv2
from typing_extensions import Any, Self

from .volume import Volume


class Motion(Volume):

    '''
    fundamental variables and function
    '''

    _motion_params = {
        'fps' : int,
        'frames_dir' : str,
        'print_on' : str,
        'levitation_mode' : str,
        'levitation_height' : float,
        'levitation_freq' : float,
        'movement_frequency' : float,
        'movement_damping' : float,
        'movement_response' : float,
        'movement_batch_size' : int,
        'movement_position_threshold' : float,
        'movement_speed_threshold' : float,
    }

    def _new_motion(
            self: Self,
        ) -> Self:
        # new motion instance
        self._motions = {}
        self._motion_index = 0
        self._frame_index = 0
        if osp.exists(self.frames_dir):
            for file in os.listdir(self.frames_dir):
                if file.endswith('.png'):
                    os.remove(osp.join(self.frames_dir, file))
        else:
            os.makedirs(self.frames_dir)
        return self

    '''
    hidden methods
    '''

    def _add_motion(
            self: Self,
            motion: dict,
        ) -> None:
        # adds a motion to the current dictionary
        self._motions[self._motion_index] = motion
        self._motion_index += 1

    def _frames_to_video(
            self: Self,
            name: str = 'video',
            video_dir: str = '.',
        ) -> str:
        # transforms the frames into a video
        if not osp.exists(video_dir):
            os.makedirs(video_dir)
        video_file = osp.join(video_dir, name + '.mp4')
        frames = [
            osp.join(self.frames_dir, file)
            for file in sorted(os.listdir(self.frames_dir))
        ]
        height, width, _ = cv2.imread(frames[0]).shape
        video = cv2.VideoWriter(
            video_file,
            cv2.VideoWriter_fourcc(*'mp4v'),
            self.fps,
            (width, height)
        )
        for frame in frames:
            video.write(cv2.imread(frame))
        video.release()
        cv2.destroyAllWindows()
        return video_file

    def _time_to_number_of_frames(
            self: Self,
            time: float,
        ) -> int:
        # transforms a time in seconds to a number of frames
        return int(np.ceil(self.fps*time))

    def _key_to_number_of_frames(
            self: Self,
            key: Any,
            time_dict: dict = 'times',
        ) -> int:
        # transforms the time attached to a key to a number of frames
        time = getattr(self, time_dict, {}).get(key, 1/self.fps)
        return self._time_to_number_of_frames(time)

    def _params_to_number_of_frames(
            self: Self,
            nfs: int = 1,
            time: float = None,
            key: Any = None,
            time_dict: dict = 'times',
        ):
        # returns the number of frames corresponding to params
        if key is not None:
            nfs = self._key_to_number_of_frames(key, time_dict)
        elif time is not None:
            nfs = self._time_to_number_of_frames(time)
        return nfs

    def _get_number_of_frames(
            self: Self,
            waiter: Any = None,
            **kwargs,
        ) -> int:
        # gets the number of frames from various possible params
        if waiter is None:
            pass
        elif isinstance(waiter, int):
            kwargs['nfs'] = waiter
        elif isinstance(waiter, float):
            kwargs['time'] = waiter
        else:
            kwargs['key'] = waiter
        return self._params_to_number_of_frames(**kwargs)

    def _volume_kwargs_levitate(
            self: Self,
            kwargs: dict,
        ) -> dict:
        # adds the levitation effect to the volumes
        if self.levitation_mode == 'off' or self.draft:
            return kwargs
        pos_params = [key for key in kwargs if key.startswith('pos')]
        default_freq_shift = kwargs.pop('levit_freq_shift', None)
        for pos_param in pos_params:
            extra_info = pos_param.replace('pos', '', 1)
            freq_shift_key = 'levit_freq_shift' + extra_info
            if freq_shift_key not in kwargs:
                if default_freq_shift is not None:
                    freq_shift = default_freq_shift
                elif self.levitation_mode == 'random':
                    freq_shift = npr.rand()*self.levitation_freq
                else:
                    freq_shift = 0
                volume_key = kwargs['main'][::-1].replace(
                    'niam_',
                    '',
                    1,
                )[::-1]
                self._volumes[volume_key][freq_shift_key] = freq_shift
            else:
                freq_shift = kwargs.pop(freq_shift_key)
            side, depth, altitude = self._normalize_pos(kwargs[pos_param])
            extra_altitude = (1 - np.cos(
                2*np.pi*(
                    freq_shift + self._frame_index/self.fps
                )/self.levitation_freq
            ))*self.levitation_height/2
            kwargs[pos_param] = (
                side,
                depth,
                altitude + extra_altitude,
            )
        return kwargs

    def _create_motion(
            self: Self,
            method: str,
            only: Any = None,
            avoid: Any = [],
            duration: Any = 1,
            delay: Any = 0,
            early_stop: Any = None,
            **kwargs,
        ) -> Self:
        # change the radius of the volume according to the given parameters
        volume_list = self.get_volume_list(only, avoid)
        for volume in volume_list:
            volume_name = self._volumes[volume]['name']
            motion = {
                'volume' : volume,
                'duration' : self._get_number_of_frames(duration),
                'method' : f'_apply_{method}_{volume_name}',
                'step' : -self._get_number_of_frames(delay),
            }
            if early_stop is not None:
                if isinstance(early_stop, list):
                    motion['early_stops'] = sorted([
                        self._get_number_of_frames(stop)
                        for stop in early_stop
                    ])
                else:
                    motion['early_stops'] = [
                        self._get_number_of_frames(early_stop)
                    ]
            motion.update(kwargs)
            getattr(self, f'_add_{method}_{volume_name}')(**motion)
        return self

    def _run_motion(
            self: Self,
            method: str,
            motion_index: int,
            step: int,
            duration: int,
            early_stops: list[int] = None,
            **kwargs,
        ) -> bool:
        # runs a specific motion and returns whether it is finished or not
        finished = False
        if step >= duration - 1:
            step = duration - 1
            finished = True
        self._motions[motion_index]['step'] = step + 1
        if step >= 0:
            getattr(self, method)(step=step + 1, duration=duration, **kwargs)
        if early_stops is not None and not finished:
            if step >= early_stops[0] - 1:
                raise StopIteration
        return finished

    def _add_change_radius_sphere(
            self: Self,
            volume: Any,
            start_with: float = 1,
            end_with: float = 1,
            centred: bool = True,
            **kwargs,
        ) -> None:
        # creates a motion to change the radius of a sphere
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

    def _add_change_radius_tube(
            self: Self,
            volume: Any,
            start_with: Any = 1,
            end_with: Any = 1,
            centred: Any = True,
            **kwargs,
        ) -> None:
        # creates a motion to change the radius of a tube
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

    def _apply_change_radius_sphere(
            self: Self,
            volume: Any,
            step: int,
            duration: int,
            start_radius: float,
            end_radius: float,
            centred: bool,
        ) -> None:
        # changes the radius of a sphere
        delta_radius = (end_radius - start_radius)/duration
        radius = start_radius + step*delta_radius
        pos = self._normalize_pos(self._volumes[volume].get('pos', None))
        if pos is not None and centred:
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

    def _apply_change_radius_tube(
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
        # changes the radius of a tube
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

    def _add_movement_sphere(
            self: Self,
            volume: Any,
            pos: tuple[float] = None,
            path: list = None,
            shifted: bool = False,
            normalize: bool = True,
            **kwargs,
        ) -> None:
        # changes the radius of sphere
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

    def _apply_movement_sphere(
            self: Self,
            volume: Any,
            step: int,
            duration: int,
            pos_list: list,
        ) -> None:
        # changes the radius of sphere
        pos = pos_list[step]
        self._volumes[volume]['pos'] = (
            pos[0],
            pos[1],
            abs(pos[2]),
        )

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
    general methods
    '''

    def frame_time(
            self: Self,
        ):
        # returns time information related to the current frame
        frame_time = self._frame_index/self.fps
        s = self.time_to_string(frame_time)
        s = s.replace('h', ':').replace('m', ':').replace('s', '')
        s += f'{frame_time - int(frame_time):.02f}'[1:]
        return 'Time stamp: ' + s

    def new_frame(
            self: Self,
        ) -> int:
        # creates a new frame
        self.update()
        if self.draft:
            self.show_info(
                None,
                self.frame_time(),
                None,
                str(self._frame_index),
            )
        self.save(
            name=f'{self._frame_index:04d}',
            image_dir=self.frames_dir,
        )
        self._frame_index += 1
        if self.print_on:
            if self._frame_index:
                sys.stdout.write('\033[F\033[K')
            message = f'Time to create {self._frame_index} frames: '
            message += self.time()
            print(message)
        return self._frame_index

    def wait(
            self: Self,
            *args,
            **kwargs,
        ) -> Self:
        # waits before next motion
        for _ in range(self._get_number_of_frames(*args, **kwargs)):
            self.new_frame()
        return self

    def video(
            self: Self,
            *args,
            **kwargs,
        ) -> None:
        # makes and saves a video
        if self.print_on:
            sys.stdout.write('\033[F\033[K')
            message = f'Time to create all frames ({self._frame_index}): '
            message += self.time()
            print(message)
            print('Making the video...')
        self._frames_to_video(*args, **kwargs)
        if self.print_on:
            sys.stdout.write('\033[F\033[K')
            print('Time to make video: ' + self.time())

    def run(
            self: Self,
        ) -> Self:
        # runs through the current motions
        no_early_stop = True
        while self._motions and no_early_stop:
            finished_motions = []
            for index, motion in self._motions.items():
                try:
                    finished = self._run_motion(motion_index=index, **motion)
                except StopIteration:
                    early_stops = motion['early_stops']
                    early_stops.pop(0)
                    if not early_stops:
                        del motion['early_stops']
                    finished = False
                    no_early_stop = False
                if finished:
                    finished_motions.append(index)
            for index in finished_motions:
                del self._motions[index]
            self.new_frame()
        return self

    def change_radius(
            self: Self,
            *args,
            **kwargs,
        ) -> Self:
        # changes a volume radius
        return self._create_motion('change_radius', *args, **kwargs)

    def grow(
            self: Self,
            *args,
            **kwargs,
        ) -> Self:
        # makes a volume appear
        kwargs['start_with'] = 0
        kwargs['end_with'] = 1
        return self.change_radius(*args, **kwargs)

    def schrink(
            self: Self,
            *args,
            **kwargs,
        ) -> Self:
        # makes a volume disappear
        kwargs['start_with'] = 1
        kwargs['end_with'] = 0
        return self.change_radius(*args, **kwargs)

    def change_alpha(
            self: Self,
            *args,
            **kwargs,
        ) -> Self:
        # changes a volume radius
        return self._create_motion('change_alpha', *args, **kwargs)

    def appear(
            self: Self,
            *args,
            use_current_alpha: bool = True,
            **kwargs,
        ) -> Self:
        # makes a volume appear
        kwargs['start_with'] = 0
        kwargs['end_with'] = 1
        if not use_current_alpha:
            kwargs['end_with'] *= -1
        return self.change_alpha(*args, **kwargs)

    def disappear(
            self: Self,
            *args,
            **kwargs,
        ) -> Self:
        # makes a volume disappear
        kwargs['start_with'] = 1
        kwargs['end_with'] = 0
        return self.change_alpha(*args, **kwargs)

    def movement(
            self: Self,
            path: list,
            *args,
            **kwargs,
        ) -> Self:
        # moves a volume according to a path
        kwargs['path'] = path
        kwargs['pos'] = None
        kwargs['shifted'] = False
        return self._create_motion('movement', *args, **kwargs)

    def move_to(
            self: Self,
            pos: tuple[float],
            *args,
            **kwargs,
        ) -> Self:
        # moves a volume towards a specific position
        kwargs['pos'] = pos
        kwargs['shifted'] = False
        return self._create_motion('movement', *args, **kwargs)

    def shift(
            self: Self,
            shift: Any,
            *args,
            **kwargs,
        ) -> Self:
        # shifts a volume
        if isinstance(shift, tuple):
            kwargs['pos'] = shift
        elif isinstance(shift, list):
            kwargs['pos'] = None
            kwargs['path'] = shift
        else:
            if len(shift.shape) == 1:
                kwargs['pos'] = tuple(shift)
            else:
                kwargs['pos'] = None
                kwargs['path'] = [tuple(pos) for pos in shift]
        kwargs['shifted'] = True
        return self._create_motion('movement', *args, **kwargs)

    def jump(
            self: Self,
            height: float,
            *args,
            end_height: float = 0,
            **kwargs,
        ) -> Self:
        # makes a volume jump
        shift = [
            (0, 0, 0),
            (0, 0, height),
            (0, 0, end_height),
        ]
        return self.shift(shift, *args, **kwargs)

    '''
    main method
    '''

    def main(
            self: Self,
        ) -> None:
        # the main running function
        pass
