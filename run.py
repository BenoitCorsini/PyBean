from bean import Motion


if __name__ == '__main__':
    bean = Motion()
    bean.levitation_mode = 'off'
    for horizon_angle in [0, 10, 20, 30, 40, 44]:
        for shade_angle in [0, 45, 90, 135, 180, 225, 270, 315]:
            for altitude_to_shade in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]:
                bean.horizon_angle = horizon_angle
                bean.shade_angle = shade_angle
                bean.altitude_to_shade = altitude_to_shade
                bean.reset()
                bean.new_sphere(radius=0.05, pos=(0, 0.5))
                bean.new_sphere(radius=0.05, pos=(1, 0.5))
                bean.new_sphere(radius=0.05, pos=(0.5, 0.2))
                bean.new_sphere(radius=0.05, pos=(0.5, 0.2, 0.5))
                bean.update()
                bean.save(f'{horizon_angle}_{shade_angle}_{altitude_to_shade}', image_dir='shade_test')