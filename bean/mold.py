import itertools
import numpy as np
from matplotlib.path import Path
from typing_extensions import Any, Self
from matplotlib import colormaps

from .brush import Brush
from .view import View
from .volume import Volume


class Mold(Brush):

    '''
    fundamental variables and function
    '''

    draft = 0
    view_dist = 4
    view_height = 5
    view_angle = None
    view_shift = 0
    view_rotation = 0
    view_screen = 2
    view_scale = 1
    sun_direction = (0.5, 0.25, -1)
    _sun_colour = Brush.hsl(hue=0.15, saturation=1, lightness=0.8)
    _sun_lightness = 0.3
    _sun_darkness = 0.8
    _overshade_shift = 0.1
    _shade_colour = np.array(Brush.hsl(lightness=0)).reshape((1, 3))
    _shade_opacity = 0.1

    _mold_params = {
        'draft' : int,
    }

    def _init_mold(
            self: Self,
        ) -> Self:
        # new mold instance
        self._molds = {}
        self._mold_index = 0
        self.new_image_from_matrix(
            key='_mold_matrix',
            matrix=np.zeros((1, 1, 4)),
            extent=self.extent(),
            zorder=0,
        )
        mold_dpi = int(np.ceil(self.dpi/10**self.draft))
        self._matrix_shape = (
            1 + mold_dpi*self.figsize[1],
            1 + mold_dpi*self.figsize[0],
            4,
        )
        self._matrix = np.zeros(self._matrix_shape).reshape((-1, 4))
        self._set_view()
        return self

    '''
    hidden methods
    '''

    def _set_view(self):
        view_kwargs = {
            'shape' : self._matrix_shape,
            'direction' : self.unitary(self.sun_direction)
        }
        for param in View.params():
            view_kwargs[param] = getattr(self, 'view_' + param)
        self._view = View(**view_kwargs)

    def _new_mold(
            self: Self,
            volume: Volume,
            key: Any = None,
            colour: Any = Brush.hsl(),
            opacity: float = 1,
            visible: bool = True,
        ) -> Self:
        # creates a new mold
        key, available = self.check_key(key)
        if available:
            mold = {
                'key' : key,
                'volume' : volume,
                'cmap' : self.cmap([self._sun_colour, colour, 'black']),
                'opacity' : opacity,
                'visible' : visible,
            }
            self._molds[key] = mold

    @staticmethod
    def _conv2(M):
        return M[1:,1:,:] + M[1:,:-1,:] + M[:-1,1:,:] + M[:-1,:-1,:]

    @staticmethod
    def _avg_mat(matrix):
        matopa = matrix[:,:,-1:]
        avgopa = Mold._conv2(matopa)
        avgopa += avgopa == 0
        matrix = Mold._conv2(matrix*matopa)/avgopa
        matrix[:,:,-1:] = Mold._conv2(matopa)/4
        return matrix

    @staticmethod
    def _depth(mold):
        return mold['volume'].depth

    def _project_molds(self):
        for mold in self._molds.values():
            volume = mold['volume']
            if not volume.projected:
                volume.project(self._view)

    def _plot_molds(self):
        self._matrix = np.zeros_like(self._matrix)
        if self._view.pos[0,-1] < 0:
            self._plot_shades()
        for mold in sorted(self._molds.values(), key=self._depth):
            self._plot_mold(**mold)
        if self._view.pos[0,-1] >= 0:
            self._plot_shades()

    def _overshade(self, key):
        volume = self._molds[key]['volume']
        overshade = np.zeros(len(volume.indices))
        for mold in self._molds.values():
            if mold['key'] == key or not mold['visible'] or not mold['opacity']:
                continue
            shaded = mold['volume'].intersect(
                volume.surface,
                self._view.direction,
            )
            overshade[shaded] = 1 - (1 - overshade[shaded])*(1 - mold['opacity'])
        return self._overshade_shift*overshade

    def _add_to_matrix(self, indices, to_add):
            matrix = self._matrix[indices].copy()
            matopa = matrix[:,-1:]
            to_add, add_opa = to_add[:,:-1], to_add[:,-1:]
            matrix[:,:-1] = matrix[:,:-1]*matopa + to_add*add_opa*(1 - matopa)
            divider = matopa + add_opa*(1 - matopa)
            divider += divider == 0
            matrix /= divider
            matrix[:,-1:] = 1 - (1 - matopa)*(1 - add_opa)
            self._matrix[indices] = matrix

    def _plot_mold(
            self: Self,
            volume: Volume,
            key: Any,
            cmap: colormaps,
            opacity: float,
            visible: bool,
        ) -> Self:
        # updates a given mold
        if visible and opacity:
            volcol = volume.sun_ratio + self._overshade(key)
            volcol *= (self._sun_darkness - self._sun_lightness)
            volcol = cmap(self._sun_lightness + volcol)
            volcol[:,-1] *= opacity
            self._add_to_matrix(volume.indices, volcol)

    def _plot_shades(self):
        maybe_shade = (self._view.rays[:,-1]*self._view.pos[:,-1] < 0)*(self._matrix[:,-1] < 1)
        shades = np.zeros(np.sum(maybe_shade))
        shades_pos = self._view.rays[maybe_shade]
        shades_pos = self._view.pos - shades_pos*self._view.pos[:,-1:]/shades_pos[:,-1:]
        for mold in self._molds.values():
            shaded = mold['volume'].intersect(
                shades_pos,
                self._view.direction,
            )
            shades[shaded] = 1 - (1 - shades[shaded])*(1 - mold['opacity'])
        shades = np.stack([np.zeros_like(shades)]*3 + [shades], axis=-1)
        shades[:,:-1] = self._shade_colour
        shades[:,-1] *= self._shade_opacity
        self._add_to_matrix(maybe_shade, shades)

    def show(self):
        self._project_molds()
        self._plot_molds()
        self.apply(
            method='set_data',
            key='_mold_matrix',
            A=self._avg_mat(self._matrix.reshape(self._matrix_shape)),
        )

    def new_sphere(self, pos=0, scale=1, axis=0, rotation=0, overground=True, *args, **kwargs):
        volume = Volume.Sphere(pos, scale, axis, rotation, overground)
        self._new_mold(volume, *args, **kwargs)

    def set_view(self, *args, **kwargs):
        self._view.set_view(*args, **kwargs)
        for param in self._view.params():
            setattr(self, 'view_' + param, getattr(self._view, param))
        for mold in self._molds.values():
            mold['volume'].projected = False

    def set_sun(self, *args, **kwargs):
        self._view.set_sun(*args, **kwargs)

