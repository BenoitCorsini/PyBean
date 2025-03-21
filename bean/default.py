import inspect
import os.path as osp

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
        'xshift' : 0.02,
        'yshift' : 0.02,
        'anchor' : 'south west',
        'font_properties' : {
            'fname' : osp.join(
                osp.dirname(
                    osp.abspath(
                        inspect.getfile(
                            inspect.currentframe()
                        )
                    )
                ),
                'font.otf'
            ),
        },
        'params' : {
            'lw' : 1.2,
            'ec' : 'darkgrey',
            'fc' : 'lightgrey',
            'alpha' : 0.25,
            'zorder' : 100,
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
    'view_pos' : (0.5, -1.5, 2),
    'view_angle' : -45,
    'screen_dist' : 1.5,
    'sun_direction' : (0.5, 0.25, -1),
    'altitude_to_shade' : 0.2,
    'side_cmap_ratio' : 0.7,
    'shade_darkness_ratio' : 0.5,
    'shade_background_ratio' : 0.1,
    'round_sides' : {
        0.49 : 0.05,
        0.25 : 0.07,
        0.09 : 0.12,
        0.02 : 0.25,
    },
    'polyhedron_lw' : 1,
    # motion
    'fps' : 20,
    'frames_dir' : 'frames',
    'remove_frames' : True,
    'print_on' : False,
    'levitation_mode' : 'random',
    'levitation_height' : 7e-2,
    'levitation_freq' : 1,
    'rotation_mode' : 'normal',
    'rotation_freq' : 1e-1,
    'rotation_clockwise' : False,
    'movement_frequency' : 2,
    'movement_damping' : 0.4,
    'movement_response' : 12,
    'movement_batch_size' : 10,
    'movement_position_threshold' : 3e-3,
    'movement_speed_threshold' : 5e-3,
}