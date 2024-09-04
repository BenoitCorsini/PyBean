import numpy as np
from typing_extensions import Any, Self

from .shape import Shape


class Volume(Shape):

    def __init__(
            self: Self,
            **kwargs,
        ) -> None:
        # initiate class
        super().__init__(**kwargs)

    def _new_volume(
            self: Self,
        ) -> Self:
        # new volume instance
        self.add_axis()
        return self

    def test(
            self: Self,
        ) -> None:
        # the main testing function
        print(self)
        print(self._get_classes())
        print(self._get_new_methods())
        print(self.get_kwargs())
        self.save()
