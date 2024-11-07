DEFAULT = {
    # canvas
    'figsize' : (16, 9),
    'dpi' : 100,
    'xmin' : 0,
    'xmax' : 1,
    'ymin' : 0,
    'ymax' : 9/16,
    'seed' : None,
    # shape
    'copyright_on' : None,
    'copyright' : {
        'text' : 'MathemaSixte',
        'height' : 0.07,
        'margin' : 0.02,
        'lw' : 2,
        'ec' : 'grey',
        'fc' : 'black',
        'font_properties' : {
            'fname' : 'bean/font.otf',
        },
        'params' : {
            'zorder' : 100,
            'alpha' : 0.05,
            'joinstyle' : 'round',
            'capstyle' : 'round',
        },
    },
    'axis_on' : None,
    'lines_per_axis' : 5,
    'axis_tick_ratio' : 0.6,
    'axis_params' : {
        'color' : 'black',
        'lw' : 1,
        'alpha' : 0.05,
        'zorder' : 98,
        'joinstyle' : 'round',
        'capstyle' : 'round',
    },
    'info_on' : None,
    'info_margin' : 1e-2,
    'info_height' : 2e-2,
    'info_params' : {
        'color' : 'black',
        'lw' : 1,
        'alpha' : 0.5,
        'zorder' : 99,
        'joinstyle' : 'round',
        'capstyle' : 'round',
    },
    # volume
    'draft' : False,
    'scale' : 1,
    'horizon_angle' : 42,
    'depth_scale' : 1,
    'depth_shift' : 0,
    'side_scale' : 1,
    'shade_angle' : -60,
    'altitude_to_shade' : 0.2,
    'shade_cmap_ratio' : 0.05,
    'round_sides' : {
        0.49 : 0.05,
        0.25 : 0.07,
        0.09 : 0.12,
        0.02 : 0.25,
    },
    # motion
    'fps' : 20,
    'frames_dir' : 'frames',
    'print_on' : False,
    'levitation_mode' : 'random',
    'levitation_height' : 5e-2,
    'levitation_freq' : 1,
    'movement_frequency' : 2,
    'movement_damping' : 0.4, # < 1 fluctuates, > 1 converges
    'movement_response' : 12, # 0 slow response, > 0 direct reponse, > 1 overshoot, < 0 anticipated response
    'movement_batch_size' : 10,
    'movement_position_threshold' : 5e-3,
    'movement_speed_threshold' : 2e-3,
}