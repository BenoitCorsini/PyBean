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
            **kwargs,
        ) -> dict:
        # creates the volume dictionary of a sphere
        return self._round_volume(available_key=available_key)

    def _update_sphere(
            self: Self,
            _main: str,
            _side: list[str],
            _shade: str,
            _text: str,
            pos: tuple[float] = (0, 0),
            radius: float = 1,
            colour: Any = None,
            shade_colour: str = None,
            visible: bool = True,
            opacity: float = 1,
        ) -> None:
        # updates the sphere
        self.set_brush(key=_text, visible=False)
        if not visible:
            self.set_brush(key=_main, visible=False)
            for key in _side:
                self.set_brush(key=key, visible=False)
            self.set_brush(key=_shade, visible=False)
            return None
        xy = self._pos_to_xy(pos, height=radius)
        if not self.draft:
            shade_pos = self._pos_to_shade_pos(pos, height=radius)
            shade_xy = self._pos_to_xy(shade_pos)
            shade_radius = radius
        scale = self._pos_to_scale(pos, height=radius)
        radius *= self.screen_dist*self.scale*scale
        zorder = scale
        path = self._curve_path(xy=xy, a=radius)
        self.apply_to_brush('set_path', key=_main, path=path)
        clipper = self.set_brush(
            key=_main,
            color=colour,
            zorder=zorder,
            alpha=opacity,
        )
        if self.draft:
            self.set_brush(key=_text, zorder=zorder, **self._text_params)
            self.apply_to_brush(
                'set_path',
                key=_text,
                path=self.path_from_string(
                    s=_text[:-5],
                    xy=xy,
                    height=self._text_height_ratio*radius,
                )
            )
        else:
            side_angle = self.angle_from_xy(
                xy1=xy,
                xy2=shade_xy,
            )
            for key, ratio in zip(_side, self._round_sides):
                path = self._merge_curves(*self._crescent_paths(
                    xy=xy,
                    radius=radius,
                    ratio=ratio,
                    theta1=270,
                    theta2=90,
                    angle=side_angle,
                ))
                self.apply_to_brush('set_path', key=key, path=path)
                self.set_brush(
                    key=key,
                    clip_path=clipper,
                    zorder=zorder,
                    alpha=opacity*self._round_sides[ratio],
                )
            path = self._curve_path(
                xy=shade_pos,
                a=shade_radius,
            )
            path.vertices = np.array([
                self._pos_to_xy(pos) for pos in path.vertices
            ])
            self.apply_to_brush('set_path', key=_shade, path=path)
            if shade_colour is None:
                shade_colour = self._get_shade_colour(clipper.get_fc())
            self.set_brush(key=_shade, color=shade_colour, alpha=opacity*self._shade_opacity)