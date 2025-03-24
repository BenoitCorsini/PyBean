from typing_extensions import Any, Self

from ._motion3_movement import _MotionMovement


class Motion(_MotionMovement):

    '''
    general methods
    '''

    def get_number_of_frames(
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
        for _ in range(self.get_number_of_frames(*args, **kwargs)):
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

    def rotate(
            self: Self,
            *args,
            **kwargs,
        ) -> Self:
        # moves a volume towards a specific position
        return self._create_motion('rotate', *args, **kwargs)

    '''
    main method
    '''

    def main(
            self: Self,
        ) -> None:
        # the main running function
        pass