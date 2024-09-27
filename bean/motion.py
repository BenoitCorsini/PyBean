import sys
import os
import os.path as osp
import numpy as np
import cv2
from typing_extensions import Any, Self

from .volume import Volume


class Motion(Volume):

    '''
    fundamental variables
    '''

    _volume_params = {
        'fps' : int,
        'frames_dir' : str,
        'print_on' : str,
    }

    '''
    hidden methods
    '''

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

    def _repeat_frames(
            self: Self,
            nfs: int = 1,
            time: float = None,
            key: Any = None,
            time_dict: dict = 'times',
        ) -> int:
        # repeat a given number of frames
        if key is not None:
            nfs = self.key_to_nfs(key, time_dict)
            if self.draft:
                self.show_info(str(key))
        elif time is not None:
            nfs = self.time_to_nfs(time)
        for _ in range(nfs):
            output = self.new_frame()
        return output

    '''
    general methods
    '''

    def time_to_nfs(
            self: Self,
            time: float,
        ) -> int:
        # transforms a time in seconds to a number of frames
        return int(np.ceil(self.fps*time))

    def key_to_nfs(
            self: Self,
            key: Any,
            time_dict: dict = 'times',
        ) -> int:
        # transforms the time attached to a key to a number of frames
        time = getattr(self, time_dict, {}).get(key, 1/self.fps)
        return self.time_to_nfs(time)

    def wait(
            self: Self,
            waiter: Any = None,
            **kwargs,
        ) -> int:
        # wait before next motion
        if waiter is None:
            pass
        elif isinstance(waiter, int):
            kwargs['nfs'] = waiter
        elif isinstance(waiter, float):
            kwargs['time'] = waiter
        else:
            kwargs['key'] = waiter
        return self._repeat_frames(**kwargs)

    def video(
            self: Self,
            *args,
            **kwargs,
        ) -> None:
        # make and save a video
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

    def new_frame(
            self: Self,
        ) -> int:
        # creates a new frame
        self.save(
            name=f'{self._frame_index:04d}',
            image_dir=self.frames_dir,
        )
        self._frame_index += 1
        if self.print_on:
            if self._frame_index:
                sys.stdout.write('\033[F\033[K')
            print(f'Time to create {self._frame_index} frames: ' + self.time())
        return self._frame_index