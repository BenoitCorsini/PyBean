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
            'zorder' : 1000,
            'alpha' : 0.05,
            'joinstyle' : 'round',
            'capstyle' : 'round',
        },
    },
    'axis_params' : {
        'color' : 'black',
        'lw' : 1,
        'alpha' : 0.07,
        'zorder' : 100,
        'joinstyle' : 'round',
        'capstyle' : 'round',
    },
    # volume
    'draft' : False,
    'fps' : 20,
    'frames_dir' : 'frames',
}