import os

_this_dir = os.path.dirname(__file__)

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
        'dir': os.path.join(_this_dir, 'images'),
        }

Animations = {
        'dir': os.path.join(Images['dir'], 'animations'),
        }

Joystick = {
        'id': 0,
        'vomit': 2,
        }

Keyboard = {
        'jump': 'up',
        'vomit': 'a',
        }
