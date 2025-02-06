import numpy as np
from typing_extensions import Any, Self

from ._volume import _Volume


class _VolumeSphere(_Volume):

    '''
    hidden methods
    '''

    def _create_sphere(
            self: Self,
            available_key: Any,
        ) -> dict:
        # creates the volume dictionary of a sphere
        return self._round_volume(available_key=available_key)

    def _update_sphere(
            self: Self,
            main: str,
            side: list[str],
            shade: str,
            pos: tuple[float] = (0, 0),
            radius: float = 1,
            colour: str = None,
            shade_colour: str = None,
            visible: bool = True,
            alpha: float = 1,
        ) -> None:
        # updates the sphere
        if not visible:
            self.set_shape(key=main, visible=False)
            for key in side:
                self.set_shape(key=key, visible=False)
            self.set_shape(key=shade, visible=False)
            return None
        xy = self._pos_to_xy(pos, height=radius)
        if not self.draft:
            shade_pos = self._pos_to_shade_pos(pos, height=radius)
        radius *= self.scale*self.side_scale
        if not self.draft:
            shade_xy = self._pos_to_xy(shade_pos)
            shade_radius = radius*self._pos_to_scale(shade_pos)
        scale = self._pos_to_scale(pos)
        radius *= scale
        zorder = scale
        path = self.curve_path(xy=xy, a=radius)
        self.apply_to_shape('set_path', key=main, path=path)
        clipper = self.set_shape(
            key=main,
            color=colour,
            zorder=zorder,
            alpha=alpha,
        )
        if not self.draft:
            side_angle = self.angle_from_xy(
                xy1=xy,
                xy2=shade_xy,
                default_angle=self.shade_angle - 90,
            )
            for key, ratio in zip(side, self.round_sides):
                path = self.merge_curves(*self.crescent_paths(
                    xy=xy,
                    radius=radius,
                    ratio=ratio,
                    theta1=270,
                    theta2=90,
                    angle=side_angle,
                ))
                self.apply_to_shape('set_path', key=key, path=path)
                self.set_shape(
                    key=key,
                    clip_path=clipper,
                    zorder=zorder,
                    alpha=alpha*self.round_sides[ratio],
                )
            path = self.curve_path(
                xy=shade_xy,
                a=shade_radius,
                b=shade_radius*np.cos(self.horizon_angle*np.pi/180),
            )
            self.apply_to_shape('set_path', key=shade, path=path)
            if shade_colour is None:
                shade_colour = self.get_cmap(['white', clipper.get_fc()])(
                    self.shade_cmap_ratio
                )
            self.set_shape(key=shade, color=shade_colour, alpha=alpha)