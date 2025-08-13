import json
import os
import os.path as osp
import numpy as np
from typing_extensions import Any, Self

from .brush import Brush


class Polyhedron(object):

    def __init__(self, points, faces, pos=(0, 0), scale=1, axis=(0, 0, 1), angle=0):
        self.points = np.concatenate([self._normalize(point) for point in points])
        self.moved = self.points.copy()
        self.faces = faces
        self.middle = self._normalize(pos)
        self.mult = scale
        self.axis = self._unitary(axis)
        self.__clean__()
        self.__infos__()
        self.modify(angle=angle)

    def __len__(self):
        return len(self.faces)

    def __iter__(self):
        return iter(self.faces)

    def __shift__(self):
        self.shifted = self.middle + self.mult*(self.points @ self._matrix(self.axis, self.angle))

    def __clean__(self):
        used = np.zeros(len(self.points), dtype=bool)
        for face in self.faces:
            for node in face:
                used[node] = True
        self.points = self.points[used]

    @staticmethod
    def _unitary(vect):
        vect = np.array(vect)
        norm = np.sum(vect**2)**0.5
        if not norm:
            norm = 1.
        return vect/norm

    def __info__(self, face):
        centre = np.mean(self.points[face], axis=0)
        self.centres.append(centre)
        ortho = [
            np.cross(
                self.points[node1] - centre,
                self.points[node2] - centre,
            )
            for (node1, node2) in zip(face, face[1:] + [face[0]])
        ]
        ortho = np.sum(ortho, axis=0)
        self.orthos.append(self._unitary(ortho))

    def __infos__(self):
        self.centres = []
        self.orthos = []
        for face in self.faces:
            self.__info__(face)
        self.centres = np.stack(self.centres)
        self.orthos = np.stack(self.orthos)

    @staticmethod
    def _normalize(
            pos: Any,
        ) -> np.array:
        # normalize a position into a triplet
        pos = np.array(pos, dtype=float)
        normed = np.zeros((1, 3))
        normed[0,:min(3, np.size(pos))] = pos
        return normed

    @staticmethod
    def _transform(axis, angle):
        if angle is None:
            angle = 0
        angle *= np.pi/180
        transform = np.array([
            [1, axis[2], -axis[1]],
            [-axis[2], 1, axis[0]],
            [axis[1], -axis[0], 1],
        ], dtype=float)
        transform *= np.sin(angle)*(np.ones(1) - np.eye(3))
        transform += np.cos(angle)*np.eye(3)
        axis = np.array(axis).reshape((1, 3))
        transform += (1 - np.cos(angle))*(axis.T @ axis)
        return transform

    @classmethod
    def cube(cls):
        return cls(
            points=[
                (-0.5, -0.5, 0),
                (+0.5, -0.5, 0),
                (+0.5, +0.5, 0),
                (-0.5, +0.5, 0),
                (-0.5, -0.5, 1),
                (+0.5, -0.5, 1),
                (+0.5, +0.5, 1),
                (-0.5, +0.5, 1),
            ],
            faces=[
                [3, 2, 1, 0],
                [4, 5, 6, 7],
                [0, 1, 5, 4],
                [2, 3, 7, 6],
                [3, 0, 4, 7],
                [1, 2, 6, 5],
            ],
        )

    @classmethod
    def pyramid(cls, height=1, base=None):
        if base is None:
            base = [
                (-0.5, -0.5),
                (+0.5, -0.5),
                (+0.5, +0.5),
                (-0.5, +0.5),
            ]
        n_base = len(base)
        return cls(
            points = base + [
                (0, 0, height),
            ],
            faces = [
                list(range(n_base))[::-1],
            ] + [
                [i, (i + 1) % n_base, n_base]
                for i in range(n_base)
            ],
        )

    @staticmethod
    def _polyhedron_sphere(
            precision: int,
        ) -> (np.array, list[list[int]]):
        # returns a polyhedron approximation of a sphere
        if precision < 0:
            ps_list = os.listdir(Brush.path())
            ps_list = [file for file in ps_list if file.startswith('_ps')]
            file_name = Brush.path(sorted(ps_list)[precision])
        else:
            file_name = Brush.path(f'_ps{precision}.json')
        if osp.exists(file_name):
            with open(file_name) as ps:
                ps_dict = json.load(ps)
                points = ps_dict['points']
                faces = ps_dict['faces']
                ps.close()
        else:
            (
                previous_points,
                previous_faces
            ) = Polyhedron._polyhedron_sphere(precision - 1)
            points = list(previous_points)
            faces = []
            mids = {}
            new_index = len(points)
            for [a, b, c] in previous_faces:
                for (x, y) in [(a, b), (b, c), (c, a)]:
                    if (x, y) not in mids:
                        mid = np.mean(previous_points[[x, y]], axis=0)
                        mid /= np.sum(mid**2)**0.5
                        points.append(mid)
                        mids[x, y] = new_index
                        mids[y, x] = new_index
                        new_index += 1
                faces.append([a, mids[a, b], mids[a, c]])
                faces.append([b, mids[b, c], mids[b, a]])
                faces.append([c, mids[c, a], mids[c, b]])
                faces.append([mids[a, b], mids[b, c], mids[c, a]])
            points = [tuple(point) for point in points]
            with open(file_name, 'w') as ps:
                json.dump({'points' : points, 'faces' : faces}, ps)
                ps.close()
        return np.array(points), faces

    @classmethod
    def polysphere(cls, precision=-1):
        points, faces = cls._polyhedron_sphere(precision)
        points += np.array([[0, 0, np.min(points[:,2])]])
        return cls(points=points/2, faces=faces)

    def shift(self, shift=None):
        if shift is not None:
            shift = self._normalize(shift)
            self.middle += shift
        return self

    def pos(self, pos=None):
        if pos is None:
            pos = self.middle
        else:
            pos = self._normalize(pos)
        self.middle = pos
        return self

    def scale(self, scale=None):
        if scale is None:
            scale = 1
        elif scale < 0:
            scale = -scale/self.mult
        self.mult *= scale
        self.moved *= scale
        self.centres *= scale
        self.lowest *= scale
        return self

    def transform(self, axis=None, angle=None):
        if axis is None:
            axis = self.axis
        else:
            axis = self._unitary(axis)
        self.axis = axis
        transform = self._transform(axis, angle)
        self.moved = self.moved @ transform
        self.centres = self.centres @ transform
        self.orthos = self.orthos @ transform
        self.lowest = np.min(self.moved[:,-1])
        return self

    def modify(self, pos=None, shift=None, scale=None, axis=None, angle=None):
        return self.transform(axis, angle).scale(scale).shift(shift).pos(pos)

    def ground_floor(self):
        if self.lowest + self.middle[0,-1] >= 0:
            return np.zeros((1, 3))
        else:
            return np.array([[
                0, 0, -self.lowest - self.middle[0,-1]
            ]])

    def get_points(self):
        return self.middle + self.moved + self.ground_floor()

    def get_centres(self):
        return self.middle + self.centres + self.ground_floor()

    def get_orthos(self):
        return self.orthos

