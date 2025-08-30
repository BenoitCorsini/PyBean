import json
import os
import os.path as osp
import numpy as np
from typing_extensions import Any, Self


class Volume(object):

    def __init__(self, name='shape', pos=0, scale=1, axis=0, rotation=0, overground=True):
        self.name = name
        self.pos = self.to3d(pos)
        self.scale = scale
        self.axis = self.to3d(axis)
        self.rotation = rotation*np.pi/180
        self.overground = overground
        self.projected = False

    @classmethod
    def Sphere(cls, *args, **kwargs):
        return cls('sphere', *args, **kwargs)

    def get_transform(self):
        transform = np.array([
            [1, self.axis[0,2], -self.axis[0,1]],
            [-self.axis[0,2], 1, self.axis[0,0]],
            [self.axis[0,1], -self.axis[0,0], 1],
        ], dtype=float)
        transform *= np.sin(self.rotation)*(np.ones(1) - np.eye(3))
        transform += np.cos(self.rotation)*np.eye(3)
        transform += (1 - np.cos(self.rotation))*(self.axis.T @ self.axis)
        return transform

    @staticmethod
    def to3d(
            pos: Any = 0,
        ) -> np.array:
        # normalize a position into a triplet
        pos = np.array(pos, dtype=float)
        normed = np.zeros(3)
        normed[:min(3, np.size(pos))] = pos
        return normed.reshape((1, 3))

    def move(self, pos, shift):
        if pos is not None:
            self.pos = self.to3d(pos)
            self.projected = False
        if shift is not None:
            self.pos += self.to3d(shift)
            self.projected = False
        return self

    def multiply(self, scale):
        if scale is not None:
            self.projected = False
            if scale >= 0:
                self.scale = scale
            else:
                self.scale *= -scale
        return self

    def rotate(self, axis, rotation):
        if axis is not None:
            self.axis = self.to3d(axis)
        if rotation is not None:
            self.rotation = rotation*np.pi/180
        return self.transform()

    def apply(self, *args, **kwargs):
        return getattr(self, 'apply_' + self.name)(*args, **kwargs)

    def project(self, *args, **kwargs):
        return getattr(self, 'project_' + self.name)(*args, **kwargs)

    def intersect(self, *args, **kwargs):
        return getattr(self, 'intersect_' + self.name)(*args, **kwargs)

    def transform(self):
        return getattr(self, 'transform_' + self.name)(*args, **kwargs)

    def apply_shape(self, pos=None, shift=None, scale=None, axis=None, rotation=None):
        self.move(pos, shift)
        self.multiply(scale)
        self.rotate(axis, rotation)
        return self

    def project_shape(self):
        self.projected = True
        self.loc = self.pos.copy()
        self.depth = np.random.rand()
        self.indices = np.zeros(0, dtype=int)
        self.surface = np.zeros((0, 3))
        self.sun_ratio = np.zeros((0, 1))

    def intersect_shape(self):
        return np.zeros(0, dtype=int)

    def transform_shape(self):
        return self

    def apply_sphere(self, *args, **kwargs):
        return self._apply_shape(*args, **kwargs)

    def project_sphere(self, view):
        self.projected = True
        rad = self.scale/2
        rad2 = rad**2
        self.loc = self.pos.copy()
        if self.overground:
            self.loc[:,-1] = max(self.loc[:,-1], rad)
        self.depth = np.sum((self.loc - view.pos)*view.z)
        hyp2 = np.sum((self.loc - view.pos)**2, axis=-1, keepdims=True)
        adj = np.sum((self.loc - view.pos)*view.rays, axis=-1, keepdims=True)
        self.indices = hyp2 - adj**2 <= rad2
        self.indices *= np.all(adj >= view.screen)
        self.indices = np.where(self.indices)[0]
        adj = adj[self.indices]
        rays = view.rays[self.indices]
        self.surface = view.pos + (adj - (rad2 - hyp2 + adj**2)**0.5)*rays
        self.sun_ratio = (1 + np.sum((self.surface - self.loc)*view.direction, axis=-1)/rad)/2
        if not self.overground:
            overground = self.surface[:,-1] >= 0
            self.indices = self.indices[overground]
            self.surface = self.surface[overground]
            self.sun_ratio = self.sun_ratio[overground]

    def intersect_sphere(self, pos, rays):
        rad2 = (self.scale/2)**2
        hyp2 = np.sum((self.loc - pos)**2, axis=-1, keepdims=True)
        adj = np.sum((self.loc - pos)*rays, axis=-1, keepdims=True)
        return np.where((hyp2 - adj**2 <= rad2)*(adj < 0))[0]

    def transform_sphere(self):
        return self

