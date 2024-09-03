import sys
import os
import os.path as osp
import cv2
from shutil import rmtree

from .volume import Volume


class Motion(Volume):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame_counter = 0

    def reset(self):
        super().reset()
        self.frame_counter = 0

    def save_video(self, *args, **kwargs):
        sys.stdout.write('\033[F\033[K')
        print(f'Time to create all frames ({self.frame_counter}): ' + self.time())
        print('Making the video...')
        self.frames_to_video(*args, **kwargs)
        sys.stdout.write('\033[F\033[K')
        print('Time to make video: ' + self.time())

    def new_frame(self, frames_dir=None, transparent=False):
        if frames_dir is None:
            frames_dir = self.frames_dir
        if (not self.frame_counter) & (osp.exists(frames_dir)):
            rmtree(frames_dir)
            os.makedirs(frames_dir)
        self.save(name=f'{self.frame_counter:04d}', image_dir=frames_dir, transparent=transparent)
        if self.frame_counter:
            sys.stdout.write('\033[F\033[K')
        self.frame_counter += 1
        print(f'Time to create {self.frame_counter} frames: ' + self.time())
    
    def frames_to_video(self, name='video', frames_dir=None, video_dir=None):
        if frames_dir is None:
            frames_dir = self.frames_dir
        if video_dir is None:
            video_dir = self.video_dir
        if not osp.exists(video_dir):
            os.makedirs(video_dir)
        video_file = osp.join(video_dir, name + '.mp4')
        frames = [osp.join(frames_dir, file) for file in sorted(os.listdir(frames_dir))]
        h, w, _ = cv2.imread(frames[0]).shape
        video = cv2.VideoWriter(
            video_file,
            cv2.VideoWriter_fourcc(*'mp4v'),
            self.fps,
            (w, h)
        )
        for frame in frames:
            image = cv2.imread(frame)
            video.write(image)
        video.release()
        cv2.destroyAllWindows()
        return video_file
