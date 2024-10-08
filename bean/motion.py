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

    _volume_params = {
        'fps' : int,
        'frames_dir' : str,
        'print_on' : str,
        'levitation_mode' : str,
        'levitation_height' : float,
        'levitation_freq' : float,
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
        motion['motion_index'] = self._motion_index
        self._motions[self._motion_index] = motion
        self._motion_index += 1

    def _frames_to_video(
            self: Self,
            name: str = 'video',
            video_dir: str = None,
        ) -> str:
        # transforms the frames into a video
        if video_dir is None:
            video_dir = '.'
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
            plot_info: bool = False,
        ):
        # returns the number of frames corresponding to params
        info = f'Waiting {nfs} frame'
        info += '' if nfs <= 1 else 's'
        if key is not None:
            nfs = self._key_to_number_of_frames(key, time_dict)
            info = str(key)
        elif time is not None:
            nfs = self._time_to_number_of_frames(time)
            info = f'Waiting {time}s'
        if self.draft and plot_info:
            self.show_info(info)
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
            side, depth, altitude = kwargs[pos_param]
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
                'step' : 0,
            }
            motion.update(kwargs)
            getattr(self, f'_add_{method}_{volume_name}')(**motion)
        return self

    def _run_motion(
            self: Self,
            method: str,
            motion_index: int,
            step: int,
            duration: int,
            **kwargs,
        ) -> bool:
        # runs a specific motion and returns whether it is finished or not
        finished = False
        if step >= duration:
            step = duration
            finished = True
        self._motions[motion_index]['step'] = step + 1
        getattr(self, method)(step=step, duration=duration, **kwargs)
        return finished

    def _add_change_radius_sphere(
            self: Self,
            volume: Any,
            start_with: float = 1,
            end_with: float = 1,
            centred: bool = True,
            **kwargs,
        ) -> None:
        # changes the radius of sphere
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

    def _apply_change_radius_sphere(
            self: Self,
            volume: Any,
            step: int,
            duration: Any,
            start_radius: float,
            end_radius: float,
            centred: bool,
        ) -> bool:
        # changes the radius of sphere
        delta_radius = (end_radius - start_radius)/duration
        radius = start_radius + step*delta_radius
        pos = self._volumes[volume].get('pos', None)
        if pos is not None and centred:
            if not step:
                if start_radius != self._volumes[volume]['radius']:
                    delta_radius = min(0, start_radius -  end_radius)
                else:
                    delta_radius = 0
            self._volumes[volume]['pos'] = (
                pos[0],
                pos[1],
                pos[2] - delta_radius,
            )
        self._volumes[volume]['radius'] = radius

    def _add_change_alpha_sphere(
            self: Self,
            volume: Any,
            start_with: float = 1,
            end_with: float = 1,
            **kwargs,
        ) -> None:
        # changes the radius of sphere
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

    def _apply_change_alpha_sphere(
            self: Self,
            volume: Any,
            step: int,
            duration: Any,
            start_alpha: float,
            end_alpha: float,
        ) -> bool:
        # changes the radius of sphere
        alpha = start_alpha + (end_alpha - start_alpha)*step/duration
        self._volumes[volume]['alpha'] = alpha

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
        return Self

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
        while self._motions:
            finished_motions = []
            for index, motion in self._motions.items():
                finished = self._run_motion(**motion)
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
            **kwargs,
        ) -> Self:
        # makes a volume appear
        kwargs['start_with'] = 0
        kwargs['end_with'] = 1
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

    '''
    main method
    '''

    def main(
            self: Self,
        ) -> None:
        # the main running function
        pass
