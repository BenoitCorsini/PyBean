import sys
import os
import os.path as osp
import numpy as np
import numpy.random as npr
import cv2
from typing_extensions import Any, Self

from .volume import Volume


'''
Any subsequent motion-based class needs the following functions:
    _add_{motion name}_{volume name}
    _apply_{motion name}_{volume name}
    {motion name}
The latter function being preferably placed in the main Motion class.
'''


class _Motion(Volume):

    '''
    fundamental variables and function
    '''

    _motion_params = {
        'fps' : int,
        'frames_dir' : str,
        'remove_frames' : bool,
        'print_on' : str,
        'levitation_mode' : str,
        'levitation_height' : float,
        'levitation_freq' : float,
        'rotation_mode' : str,
        'rotation_freq' : float,
        'rotation_clockwise' : bool,
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
            if self.remove_frames:
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
            name: Any = 'video',
            video_dir: str = '.',
        ) -> str:
        # transforms the frames into a video
        if not osp.exists(video_dir):
            os.makedirs(video_dir)
        video_file = osp.join(video_dir, f'{name}.mp4')
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
        time = getattr(self, time_dict, {})._add_motionget(key, 1/self.fps)
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

    def _volume_kwargs_levitate(
            self: Self,
            **kwargs,
        ) -> dict:
        # adds the levitation effect to the volumes
        levitate = self.levitation_mode != 'off' and not self.draft
        levitate = kwargs.pop('levitate', levitate)
        if not levitate:
            return kwargs
        pos_params = [key for key in kwargs if key.startswith('pos')]
        volume_key = kwargs['key']
        default_freq_shift = kwargs.pop('levitation_freq_shift', None)
        levitation_freq = kwargs.pop(
            'levitation_freq',
            self.levitation_freq,
        )
        levitation_height = kwargs.pop(
            'levitation_height',
            self.levitation_height,
        )
        for pos_param in pos_params:
            extra_info = pos_param.replace('pos', '', 1)
            freq_shift_key = 'levitation_freq_shift' + extra_info
            if freq_shift_key not in kwargs:
                if default_freq_shift is not None:
                    freq_shift = default_freq_shift
                elif self.levitation_mode == 'random':
                    freq_shift = npr.rand()/self.levitation_freq
                else:
                    freq_shift = 0
                self._volumes[volume_key][freq_shift_key] = freq_shift
            else:
                freq_shift = kwargs.pop(freq_shift_key)
            extra_altitude = (1 - np.cos(
                2*np.pi*(
                    freq_shift + self._frame_index/self.fps
                )*levitation_freq
            ))*levitation_height/2
            kwargs[pos_param] = self._normalize_pos(
                kwargs[pos_param],
                height=extra_altitude,
            )
        return kwargs

    def _volume_kwargs_rotate(
            self: Self,
            **kwargs,
        ) -> dict:
        # adds the rotation effect to the volumes
        rotate = self.rotation_mode != 'off' and not self.draft
        rotate = kwargs.pop('rotate', rotate)
        if not rotate or 'transform' not in kwargs:
            return kwargs
        volume_key = kwargs['key']
        rotation_freq = kwargs.pop(
            'rotation_freq',
            self.rotation_freq,
        )
        if 'rotation_freq_shift' in kwargs:
            freq_shift = kwargs.pop('rotation_freq_shift')
        else:
            if self.rotation_mode == 'random':
                freq_shift = npr.rand()/rotation_freq
            else:
                freq_shift = 0
            self._volumes[volume_key]['rotation_freq_shift'] = freq_shift
        angle = 2*np.pi*(
            freq_shift + self._frame_index/self.fps
        )*rotation_freq
        clockwise = kwargs.pop('rotation_clockwise', self.rotation_clockwise)
        clockwise = 2*float(clockwise) - 1
        rotate_transform = np.array([
            [np.cos(angle), clockwise*np.sin(angle), 0],
            [-clockwise*np.sin(angle), np.cos(angle), 0],
            [0, 0, 1],
        ])
        if kwargs.pop('rotate_relative', False):
            kwargs['transform'] = kwargs['transform'] @ rotate_transform
        else:
            kwargs['transform'] = rotate_transform @ kwargs['transform']
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
                'duration' : self.get_number_of_frames(duration),
                'method' : f'_apply_{method}_{volume_name}',
                'step' : -self.get_number_of_frames(delay),
            }
            if early_stop is not None:
                if isinstance(early_stop, list):
                    motion['early_stops'] = sorted([
                        self.get_number_of_frames(stop)
                        for stop in early_stop
                    ])
                else:
                    motion['early_stops'] = [
                        self.get_number_of_frames(early_stop)
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