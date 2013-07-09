from geometry import Vector, AABB
from config import Physics as config

class _World(AABB):
    """_world object."""
    def __init__(self):
        """Set config values for world AABB."""
        AABB.__init__(self, config['offset'][0],
                config['offset'][1], config['size'])
        self.gravity = Vector(*config['gravity'])

    def resolve(self, c):
        if c.position.x < self.position.x:
            c.position.x = self.position.x
            c.velocity.x = 0
        elif c.position.x + c.size.x > self.position.x + self.size.x:
            c.position.x = self.position.x + self.size.x - c.size.x
            c.velocity.x = 0
        if c.position.y + c.size.y > self.position.y + self.size.y:
            c.position.y = self.position.y + self.size.y - c.size.y
            c.velocity.y = 0
            c.acceleration.x, c.acceleration.y = self.gravity
            c.contact = True
_world = _World()

class Component(AABB):
    def __init__(self, size, x=0, y=0, vx=0, vy=0, ax=0, ay=0):
        """Build the component."""
        AABB.__init__(self, x, y, size)
        self.velocity = Vector(vx, vy)
        self.acceleration = Vector(ax, ay)
        self.acceleration += _world.gravity
        self.contact = False

    def update(self):
        """update the component (motion)."""
        self.contact = False
        self.velocity += self.acceleration
        self.position += self.velocity
        _world.resolve(self)

    @property
    def ground(self):
        return self.contact
