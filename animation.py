# -*- coding: utf-8 -*-

import os
from PySFML import sf
from config import Animations as config

class Animation(object):
    def __init__(self, frames, loop=True):
        self.frames = frames
        self.loop = loop
        self.index = 0

    def Advance(self):
        nbFrames = len(self.frames)
        if nbFrames > 0 and self.loop:
            self.index = (self.index + 1) % nbFrames
        elif self.index < nbFrames-1:
            self.index += 1

    def Current(self):
        return self.frames[self.index]

    def Reset(self):
        self.index = 0

    def IsFinished(self):
        return self.loop == False and self.index == len(self.frames) - 1

class AnimationFactory(object):
    instance = None
    animations = {}

    def __new__(cls, *args, **kwargs):
        """Singleton pattern boilerplate."""
        if cls.instance is None:
            cls.instance = super(AnimationFactory, cls).__new__(cls, *args, **kwargs)
        return cls.instance

    def All(self):
        for animKey in os.listdir(config['dir']):
            animDir = config['dir'] + '/' + animKey
            animFrames = []
            for animImage in os.listdir(animDir):
                image = sf.Image()
                image.LoadFromFile(animDir + '/' + animImage)
                animFrames.append(image)
            self.animations[animKey] = Animation(animFrames)

    def Get(self, key, loop=True):
        if key in self.animations:
            return self.animations[key]
        else:
            animDir = config['dir'] + '/' + key
            animFrames = []
            animImages = os.listdir(animDir)
            animImages.sort()
            for animImage in animImages:
                image = sf.Image()
                anim = None
                if image.LoadFromFile(animDir + '/' + animImage):
                    animFrames.append(image)
            anim = Animation(animFrames, loop)
            self.animations[key] = anim
            return anim
