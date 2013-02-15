# -*- coding: utf-8 -*-

import math

class Vector(object):
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, v):
        return Vector(self.x + v.x, self.y + v.y)

    def __sub__(self, v):
        return Vector(self.x - v.x, self.y - v.y)

    def __mul__(self, coef):
        return Vector(self.x*coef, self.y*coef)

    def __eq__(self, v):
        return self.x, self.y == v.x, v.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __len__(self):
        return math.sqrt(self.x**2, self.y**2)

    def __iter__(self):
        return iter((self.x, self.y))

class AABB(object):
    def __init__(self, x, y, size):
        self.position = Vector(x, y)
        self.size = Vector(*size)
