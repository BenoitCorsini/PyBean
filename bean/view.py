import numpy as np
from typing_extensions import Any, Self


class View(object):

    @staticmethod
    def params():
        return [
            'dist',
            'height',
            'angle',
            'shift',
            'rotation',
            'screen',
            'scale',
        ]

    def __init__(self, shape=(2, 2), direction=np.array([0, 0, -1]), **kwargs):
        self.shape = shape
        self.set_sun(direction)
        for param in self.params():
            if param not in kwargs:
                kwargs[param] = None
        self.set_view(**kwargs)

    def __set_view__(self):
        rotation = np.pi*self.rotation/180
        self.pos = np.array([[
            - self.dist*np.sin(rotation) + self.shift*np.cos(rotation),
            - self.dist*np.cos(rotation) - self.shift*np.sin(rotation),
            self.height,
        ]])/self.scale
        if self.angle is None:
            look_dir = (self.dist**2 + self.height**2)**0.5
            look_dir = (
                self.dist/look_dir,
                -self.height/look_dir,
            )
        else:
            angle = np.pi*self.angle/180
            look_dir = (
                np.cos(angle),
                np.sin(angle),
            )
        self.x = np.array([[
            np.cos(rotation),
            -np.sin(rotation),
            0,
        ]])
        self.y = np.array([[
            -look_dir[1]*np.sin(rotation),
            -look_dir[1]*np.cos(rotation),
            look_dir[0],
        ]])
        self.z = np.array([[
            look_dir[0]*np.sin(rotation),
            look_dir[0]*np.cos(rotation),
            look_dir[1],
        ]])
        return self

    def __set_rays__(self):
        y, x = np.divmod(
            np.arange(self.shape[0]*self.shape[1]).reshape((-1, 1)),
            self.shape[1],
        )
        x = x/(self.shape[1] - 1) - 0.5
        y = y[::-1]/(self.shape[1] - 1) - 0.5*(self.shape[0] - 1)/(self.shape[1] - 1)
        self.rays = self.x*x + self.y*y + self.screen*self.z
        self.rays /= np.sum(self.rays**2, axis=-1, keepdims=True)**0.5

    def __update_param__(self, key, value):
        assert key in self.params()
        setattr(self, key, value)
        return self

    def set_sun(self, direction=None):
        if direction is None:
            direction = self.direction
        self.direction = direction.reshape((1, 3))
        return self

    def set_view(self, *args, **kwargs):
        for key, value in zip(self.params(), args):
            kwargs[key] = value
        for key, value in kwargs.items():
            self.__update_param__(key, value)
        self.__set_view__()
        self.__set_rays__()
        return self

