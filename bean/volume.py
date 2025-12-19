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

    def dig(self):
        overground = self.surface[:,-1] >= 0
        self.indices = self.indices[overground]
        self.surface = self.surface[overground]
        self.sun_ratio = self.sun_ratio[overground]

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

    def _method(self, name, *args, **kwargs):
        return getattr(self, self.name + '_' + name)(*args, **kwargs)

    def apply(self, *args, **kwargs):
        return self._method('apply', *args, **kwargs)

    def project(self, *args, **kwargs):
        self._method('project', *args, **kwargs)
        if not self.overground:
            self.dig()

    def intersect(self, *args, **kwargs):
        return self._method('intersect', *args, **kwargs)

    def transform(self, *args, **kwargs):
        return self._method('transform', *args, **kwargs)

    @classmethod
    def Volume(cls, *args, **kwargs):
        return cls('volume', *args, **kwargs)

    def volume_apply(self, pos=None, shift=None, scale=None, axis=None, rotation=None):
        self.move(pos, shift)
        self.multiply(scale)
        self.rotate(axis, rotation)
        return self

    def volume_project(self, view):
        self.projected = True
        self.loc = self.pos.copy()
        self.depth = np.random.rand()
        self.indices = []
        self.surface = np.zeros((0, 3))
        self.sun_ratio = np.zeros(0)
        return self

    def volume_intersect(self, pos, rays):
        return []

    def volume_transform(self):
        return self

    @classmethod
    def Sphere(cls, *args, **kwargs):
        return cls('sphere', *args, **kwargs)

    def sphere_apply(self, *args, **kwargs):
        return self._apply_shape(*args, **kwargs)

    def sphere_project(self, view):
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
        return self

    def sphere_intersect(self, pos, rays):
        rad2 = (self.scale/2)**2
        hyp2 = np.sum((self.loc - pos)**2, axis=-1, keepdims=True)
        adj = np.sum((self.loc - pos)*rays, axis=-1, keepdims=True)
        return np.where((hyp2 - adj**2 <= rad2)*(adj < 0))[0]

    def sphere_transform(self):
        return self

    @staticmethod
    def _orhogonal_orientation(orientation):
        x = orientation[0]
        if np.any(x):
            x /= np.sum(x**2)**0.5
        else:
            x = np.array([1, 0, 0], dtype=float)
        if np.size(orientation, axis=0) > 1:
            y = orientation[1]
        else:
            y = np.zeros(3)
        y -= np.sum(x*y)*x
        if np.any(y):
            y /= np.sum(y**2)**0.5
        elif x[0] or x[1]:
            y = np.array([
                -x[1], x[0], 0,
            ])/(x[0]**2 + x[1]**2)**0.5
        else:
            y = np.array([1, 0, 0], dtype=float)
        z = np.cross(x, y)
        return np.stack([x, y, z], axis=0)

    @staticmethod
    def _norm_orientation(orientation):
        if orientation is None:
            return np.eye(3)
        if isinstance(orientation, list):
            orientation = np.concatenate([Volume.to3d(vect) for vect in orientation])
        elif isinstance(orientation, np.ndarray):
            if len(orientation.shape) < 2:
                orientation = Volume.to3d(orientation)
        else:
            orientation = Volume.to3d(orientation)
        return Volume._orhogonal_orientation(orientation)

    @classmethod
    def Brick(cls, width, height, depth, orientation, *args, **kwargs):
        V = cls('brick', *args, **kwargs)
        V.dists = np.array([[width, depth, height]])
        V.orientation = V._norm_orientation(orientation)
        return V

    def brick_apply(self, width=None, height=None, depth=None, orientation=None, *args, **kwargs):
        if width is not None:
            self.dists[0] = width
        if height is not None:
            self.dists[2] = height
        if depth is not None:
            self.dists[1] = depth
        if orientation is not None:
            self.orientation = self._norm_orientation(orientation)
        return self._apply_shape(*args, **kwargs)

    def brick_project(self, view):
        self.projected = True
        self.orientation = self.orientation @ np.diag(
            2*(np.sum(self.orientation*view.z, axis=-1) >= 0) - 1
        )
        rad = self.scale/2
        rad2 = rad**2
        self.loc = self.pos.copy()
        if self.overground:
            self.loc[:,-1] = max(self.loc[:,-1], rad*np.sum(np.abs(self.orientation[:,-1]*self.dists[0])))
        self.depth = np.sum((self.loc - view.pos)*view.z)

        pos = np.concatenate([
            np.sum((view.pos - self.pos)*self.orientation[0:1], axis=-1, keepdims=True),
            np.sum((view.pos - self.pos)*self.orientation[1:2], axis=-1, keepdims=True),
            np.sum((view.pos - self.pos)*self.orientation[2:3], axis=-1, keepdims=True),
        ], axis=-1)
        rays = np.concatenate([
            np.sum(view.rays*self.orientation[0:1], axis=-1, keepdims=True),
            np.sum(view.rays*self.orientation[1:2], axis=-1, keepdims=True),
            np.sum(view.rays*self.orientation[2:3], axis=-1, keepdims=True),
        ], axis=-1)
        dist = (pos - self.dists*rays)/(rays + (rays == 0))
        surface = np.argmin(dist, axis=-1)
        dist = np.min(dist, axis=-1, keepdims=True)
        print(surface)
        print(dist)





        hyp2 = np.sum((self.loc - view.pos)**2, axis=-1, keepdims=True)
        adj = np.sum((self.loc - view.pos)*view.rays, axis=-1, keepdims=True)
        self.indices = hyp2 - adj**2 <= rad2
        self.indices *= np.all(adj >= view.screen)
        self.indices = np.where(self.indices)[0]
        adj = adj[self.indices]
        rays = view.rays[self.indices]
        self.surface = view.pos + (adj - (rad2 - hyp2 + adj**2)**0.5)*rays
        self.sun_ratio = (1 + np.sum((self.surface - self.loc)*view.direction, axis=-1)/rad)/2
        return self

    def brick_intersect(self, pos, rays):
        rad2 = (self.scale/2)**2
        hyp2 = np.sum((self.loc - pos)**2, axis=-1, keepdims=True)
        adj = np.sum((self.loc - pos)*rays, axis=-1, keepdims=True)
        return np.where((hyp2 - adj**2 <= rad2)*(adj < 0))[0]

    def brick_transform(self):
        self.orientation @ self.get_transform()
        return self

    @classmethod
    def Cube(cls, *args, **kwargs):
        V = cls.Brick(1, 1, 1, *args, **kwargs)
        V.name = 'cube'
        return V

    def cube_apply(self, orientation=None, *args, **kwargs):
        if orientation is not None:
            self.orientation = V._norm_orientation(orientation)
        return self._apply_shape(*args, **kwargs)

    def cube_project(self, *args, **kwargs):
        return self.brick_project(*args, **kwargs)

    def cube_intersect(self, *args, **kwargs):
        return self.brick_intersect(*args, **kwargs)

    def cube_transform(self, *args, **kwargs):
        return self.brick_transform(*args, **kwargs)

