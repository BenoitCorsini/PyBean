from bean import Brush


# initiates the class
BS = Brush(
    figsize=(10, 10),
    xmin=-2,
    xmax=+2,
    ymin=-2,
    ymax=+2,
    info_margin=0.1,
    info_height=0.1,
)
BS.set_args(True)

# creates a global grid splitting the image in 2x2 blocks
grid_params = {'capstyle' : 'round', 'alpha' : 0.2}
BS.grid(blocks=2, lw=30, **grid_params)

# in the top-left corner, plots a circle and a grid
BS.add_brush('Circle', xy=(-1, 1), radius=0.8)
BS.grid(right=0, bottom=0, blocks=(2, 5), lw=20, **grid_params)

# in the top-right corner, plots a rounded triangle and a grid
vertices = [(0.4, 0.4), (1.6, 0.4), (1.0, 1.6), (0.4, 0.4)]
BS.add_raw_path(vertices, key='tri')
BS.set_brush('tri', lw=50, joinstyle='round', capstyle='round', color='gold')
BS.grid(left=0, bottom=0, steps=(0.4, 0.5), lw=10, **grid_params)

# in the bottom-left corner, plots a square and a grid
side = 0.8*2**0.5
BS.add_brush('Rectangle', 'diam', xy=(0, 0), width=side, height=side)
BS.apply_to_brush('set_angle', 'diam', angle=45)
BS.apply_to_brush('set_xy', 'diam', xy=(-1, -1.8))
BS.grid(right=0, top=0, blocks=3, lw=30, **grid_params)

# in the bottom-right corner, plots some text and a grid
path = BS.path_from_string(s='B', xy=(1, -1), height=1.25)
BS.add_path(path)
BS.grid(left=0, top=0, blocks=3, steps=0.5, lw=10, **grid_params)

# adds the info of the different blocks
BS.show_info('square', 'triangle', 'diamond', '\'B\'')

# saves the image and outputs its name
file_name = f'brush'
if BS.cpr_on:
    file_name += '+copyright'
if BS.axis_on:
    file_name += '+axis'
if BS.info_on is not None and not BS.info_on:
    file_name += '-info'
BS.save(
    name=file_name,
    image_dir='examples',
)
print(f'Image created: {file_name}.png')
