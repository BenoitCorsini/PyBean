import sys
import os
import os.path as osp
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
            osp.join(frames_dir, file)
            for file in sorted(os.listdir(frames_dir))
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

    '''
    general methods
    '''

    def video(
            self: Self,
            *args,
            **kwargs,
        ) -> None:
        # make and save a video
        sys.stdout.write('\033[F\033[K')
        message = f'Time to create all frames ({self._frame_index}): '
        message += self.time()
        print(message)
        print('Making the video...')
        self.frames_to_video(*args, **kwargs)
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
        if self._frame_index:
            sys.stdout.write('\033[F\033[K')
        self._frame_index += 1
        print(f'Time to create {self._frame_index} frames: ' + self.time())
        return self._frame_index