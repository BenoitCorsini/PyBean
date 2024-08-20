import matplotlib.patches as patches
from matplotlib.transforms import Affine2D
from matplotlib.textpath import TextPath

from .figure import Figure


class Image(Figure):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save_image(self, *args, **kwargs):
        self.save(*args, **kwargs)
        print('Time to plot image: ' + self.time())

    def plot_shape(self, shape_name, **kwargs):
        patch = getattr(patches, shape_name)(**kwargs)
        self.ax.add_patch(patch)
        return patch

    def grid(self, x_blocks=1, y_blocks=None, xmin=None, xmax=None, ymin=None, ymax=None, **kwargs):
        if y_blocks is None:
            y_blocks = x_blocks
        if xmin is None:
            xmin = self.xmin
        if xmax is None:
            xmax = self.xmax
        if ymin is None:
            ymin = self.ymin
        if ymax is None:
            ymax = self.ymax
        columns = []
        rows = []
        kwargs['capstyle'] = 'butt'
        delta_x = (xmax - xmin)/x_blocks
        for x in range(0, x_blocks + 1):
            pos = xmin + x*delta_x
            column_patch = self.plot_shape(
                shape_name='Polygon',
                xy=[[pos, ymin], [pos, ymax]],
                **kwargs
            )
            columns.append(column_patch)
        delta_y = (ymax - ymin)/y_blocks
        for y in range(0, y_blocks + 1):
            pos = ymin + y*delta_y
            row_patch = self.plot_shape(
                shape_name='Polygon',
                xy=[[xmin, pos], [xmax, pos]],
                **kwargs
            )
            rows.append(row_patch)
        return columns, rows