# -*- coding: utf-8 -*-

from PySFML import sf

Window = {
        'size': (600, 480),
        'title': 'Demo Fil Rouge',
        'control': 'joystick'
        }

Player = {
        'speeds': {
            'walk': 4,
            },
        'accelerations': {
            'jump': 32
            },
        'size': (186, 148)
        }

Physics = {
        'offset': (0, Window['size'][1]),
        'gravity': (0, 2),
        'size': (Window['size'][0], -13)
        }

Images = {
        'dir': 'images'
        }

Animations = {
        'dir': Images['dir'] + '/animations'
        }

Joystick = {
        'id': 0,
        #'jump': 0,
        'vomit': 2
        }

Keyboard = {
        'jump': sf.Key.Up,
        'vomit': sf.Key.A
        }
