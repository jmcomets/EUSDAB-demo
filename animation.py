import os
import app
from config import Animations as config

class Animation(app.Drawable):
    def __init__(self, frames, loop=True):
        assert len(frames) > 0
        self.frames = frames
        self.loop = loop
        self.index = 0

    def render(self, graphics):
        self.frames[current].render(graphics)

    def advance(self):
        nbFrames = len(self.frames)
        if nbFrames > 0 and self.loop:
            self.index = (self.index + 1) % nbFrames
        elif self.index < nbFrames - 1:
            self.index += 1

    def current_image(self):
        return self.frames[self.index]

    def reset(self):
        self.index = 0

    @property
    def finished(self):
        return self.loop == False and self.index == len(self.frames) - 1

class _AnimationFactory(object):
    animations = {}

    def all(self):
        for key in os.listdir(config['dir']):
            directory = os.path.join(config['dir'], key)
            self.animations[key] = self.raw_get(key)

    def get(self, key, *args, **kwargs):
        if key in self.animations:
            return self.animations[key]
        else:
            return self.raw_get(key)

    def raw_get(self, key, *args, **kwargs):
        directory = os.path.join(config['dir'], key)
        images = os.listdir(directory)
        images.sort()
        frames = []
        for image in images:
            try:
                image = app.Image(os.path.join(directory, image))
                frames.append(image)
            except IOError:
                pass
        anim = Animation(frames, *args, **kwargs)
        self.animations[key] = anim
        return anim

_global_animation_factory = None
def AnimationFactory():
    global _global_animation_factory
    if _global_animation_factory is None:
        _global_animation_factory = _AnimationFactory()
    return _global_animation_factory
