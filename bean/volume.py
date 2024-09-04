from .shape import Shape


class Volume(Shape):

    def __init__(
            self: Self,
            **kwargs,
        ) -> None:
        # initiate class
        super().__init__(**kwargs)
        self._new_volume()

    def _new_shape(
            self: Self,
        ) -> Self:
        # new volume instance
        return self
