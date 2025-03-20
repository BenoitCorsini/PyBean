import numpy as np

from bean import Canvas

CV = Canvas(seed=0)
CV.add_arg('--cscale_colour')
CV.set_args(True)

cmap = Canvas.get_cscale(colour=CV.cscale_colour)
step = 0.02
linewidth = 10
for pos in np.arange(start=step, stop=0.5, step=step):
	random_colour = cmap(np.random.rand())
	CV.ax.plot(
		[pos, 1 - pos, 1 - pos, pos, pos],
		[pos, pos, 1 - pos, 1 - pos, pos],
		color=random_colour,
		lw=linewidth,
	)
file_name = f'canvas {CV.cscale_colour}'
CV.save(
	name=file_name,
	image_dir='examples',
)
print(f'Image created: {file_name}.png')