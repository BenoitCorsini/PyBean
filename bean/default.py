DEFAULT = {
    # canvas
    'figsize' : (16, 9),
    'dpi' : 100,
    'xmin' : 0,
    'xmax' : 1,
    'ymin' : 0,
    'ymax' : 9/16,
    # shape
    'lines_per_axis' : 5,
    'axis_tick_ratio' : 0.6,
    'info_margin' : 1e-2,
    'info_height' : 2e-2,
    'copyright' : {
        'text' : '@B.Corsini',
        'height' : 0.05,
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
    'axis_params' : {
        'color' : 'black',
        'lw' : 1,
        'alpha' : 0.05,
        'zorder' : 98,
        'joinstyle' : 'round',
        'capstyle' : 'round',
    },
    'info_params' : {
        'fc' : [0.4]*3,
        'ec' : [0.3]*3,
        'lw' : 1,
        'zorder' : 99,
        'joinstyle' : 'round',
        'capstyle' : 'round',
    },
    # volume
    'draft' : False,
    'shade_angle' : -60,
    'shade_delta_height' : 0.1,
    'fps' : 20,
    'frames_dir' : 'frames',
}