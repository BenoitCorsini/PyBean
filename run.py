import pybean

if __name__ == '__main__':
	bean = pybean.Motion()
	bean.levitation_mode = 'random'
	bean.draft = False
	bean.scale = 0.5

	bean.new_sphere('blue', pos=(0.2, 0.1, 0), radius=0.2, colour='royalblue')
	bean.update()

	bean.new_sphere('sphere', pos=(0.6, 0.3, 0), radius=0.2, colour='gold')
	bean.update()

	bean.new_sphere('G', pos=(0.85, 0.15, 0), radius=0.2, colour='forestgreen')
	bean.appear('G', duration=1.)

	bean.new_sphere('tiny', pos=(0.3, 0.5, 0.1), radius=0.1, colour='crimson')
	bean.appear('tiny', duration=0.2)

	bean.disappear(avoid='blue', duration=1.)
	bean.disappear('blue', duration=0.2)