from bean import Volume

# initiates the class and adapt the view point to the figure size
VL = Volume(figsize=(10, 10), view_pos=(0.5, -0.7, 2), view_angle=-60)
VL.add_arg('--precision', type=int, default=0)
VL.set_args(True)
VL.scale = 0.5

# creates a triangle of spheres and connecting tubes
positions = [(0, 0), (2, 2), (0, 2)]
for pos in positions:
    VL.new_sphere(str(pos), pos=pos)
for key1, key2 in zip(positions, positions[1:] + [positions[0]]):
    VL.new_tube(key1=str(key1), key2=str(key2))

# adds several polyhedrons
triangle_face = [(0.0, 0.0), (1, 0.0), (1, 1)]
VL.new_pylon('tri', pos=(0.6, 1.4), basic_face=triangle_face, pylon_height=2)
VL.new_cube(pos=(2, 1), colour='forestgreen')
VL.new_pyramid(pos=(1, 0), pyramid_height=2, colour='royalblue')
VL.new_polysphere(pos=(1.5, 0, 1), precision=VL.precision, colour='gold')

# updates the colour of the triangle pylon.
VL.update('tri', colour='crimson')
# updates each radius to be 0.2
VL.update(radius=0.2)
# changes the colour of all volumes except polyhedrons 
VL.update(avoid='polyhedron', colour='saddlebrown')
# specifies the design of tubes
VL.update(only='tube', radius=0.1, space=0.5, colour='peachpuff')

# saves the image and outputs the time it took to create the image
file_name = 'volume'
if VL.precision:
    file_name = 'polysphere'
if VL.draft:
    file_name += ' draft'
VL.save(
    name=file_name,
    image_dir='examples',
)
print(f'Time to create \'{file_name}.png\': {VL.time()}')