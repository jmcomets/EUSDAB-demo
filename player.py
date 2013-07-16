import random
import app
from physics import Component as PhysicsComponent
from animation import Animation, AnimationFactory
from config import Player as config

# Player controls
class Controls:
    END = 0
    JUMP = 1
    LEFT = 2
    RIGHT = 3
    GROUND = 4
    ATTACK = 5

class State(object):
    def __init__(self, model):
        self.model = model

    def update(self): pass
    def on_start(self): pass
    def on_end(self): pass

class AnimatedState(State):
    def __init__(self, model, animation):
        super(AnimatedState, self).__init__(model)
        self.animation = animation

    def on_start(self):
        self.model.animation = self.animation
        self.animation.reset()

    def on_finished(self):
        self.model.control(Controls.END)

    def update(self):
        super(AnimatedState, self).update()
        if self.animation.finished:
            self.on_finished()

class MoveState(AnimatedState):
    def __init__(self, model, animation, speed):
        super(MoveState, self).__init__(model, animation)
        self.speed = speed

    def update(self):
        super(MoveState, self).update()
        self.model.physics.position.x += self.speed

class JumpState(AnimatedState):
    def __init__(self, model, animation, force):
        super(JumpState, self).__init__(model, animation)
        self.force = force

    def update(self):
        super(JumpState, self).update()
        if self.model.physics.ground:
            self.on_ground()

    def on_start(self):
        super(JumpState, self).on_start()
        if self.model.physics.ground:
            self.model.physics.velocity.y -= self.force

    def on_ground(self):
        self.model.control(Controls.GROUND)

class JumpMoveState(JumpState):
    def __init__(self, model, animation, speed, force):
        super(JumpMoveState, self).__init__(model, animation, force)
        self.speed = speed

    def update(self):
        super(JumpMoveState, self).update()
        self.model.physics.position.x += self.speed

class Model(app.Drawable):
    def __init__(self):
        self.physics = PhysicsComponent(config['size'])
        fact = AnimationFactory()
        self.states = {
                'idle_left': AnimatedState(self, fact.get('idle_left')),
                'idle_right': AnimatedState(self, fact.get('idle_right')),
                'walk_left': MoveState(self, fact.get('walk_left'), -config['speeds']['walk']),
                'walk_right': MoveState(self, fact.get('walk_right'), config['speeds']['walk']),
                'idle_jump_left': JumpState(self, fact.get('jump_left', loop=False), config['accelerations']['jump']),
                'idle_jump_right': JumpState(self, fact.get('jump_right', loop=False), config['accelerations']['jump']),
                'jump_left': JumpMoveState(self, fact.get('jump_left', loop=False), -config['speeds']['walk'], config['accelerations']['jump']),
                'jump_right': JumpMoveState(self, fact.get('jump_right', loop=False), config['speeds']['walk'], config['accelerations']['jump']),
                'attack_left': AnimatedState(self, fact.get('vomit_left', loop=False)),
                'attack_right': AnimatedState(self, fact.get('vomit_right', loop=False)),
                }
        self.transitions = {
                'idle_left': {
                    (Controls.LEFT, True): 'walk_left',
                    (Controls.RIGHT, True): 'walk_right',
                    (Controls.JUMP, True): 'idle_jump_left',
                    (Controls.ATTACK, True): 'attack_left'
                    },
                'idle_right': {
                    (Controls.LEFT, True): 'walk_left',
                    (Controls.RIGHT, True): 'walk_right',
                    (Controls.JUMP, True): 'idle_jump_right',
                    (Controls.ATTACK, True): 'attack_right'
                    },
                'walk_left': {
                    (Controls.LEFT, False): 'idle_left',
                    (Controls.RIGHT, True): 'walk_right',
                    (Controls.JUMP, True): 'jump_left',
                    (Controls.ATTACK, True): 'attack_left'
                    },
                'walk_right': {
                    (Controls.LEFT, True): 'walk_left',
                    (Controls.RIGHT, False): 'idle_right',
                    (Controls.JUMP, True): 'jump_right',
                    (Controls.ATTACK, True): 'attack_right'
                    },
                'idle_jump_left': {
                    (Controls.GROUND, True): 'idle_left',
                    (Controls.LEFT, True): 'jump_left',
                    (Controls.RIGHT, True): 'jump_right'
                    },
                'idle_jump_right': {
                    (Controls.GROUND, True): 'idle_right',
                    (Controls.RIGHT, True): 'jump_right',
                    (Controls.LEFT, True): 'jump_left'
                    },
                'jump_left': {
                    (Controls.GROUND, True): 'walk_left',
                    (Controls.LEFT, False): 'idle_jump_left'
                    },
                'jump_right': {
                    (Controls.GROUND, True): 'walk_right',
                    (Controls.RIGHT, False): 'idle_jump_right'
                    },
                'attack_left': {
                    (Controls.END, True): 'idle_left'
                    },
                'attack_right': {
                    (Controls.END, True): 'idle_right'
                    }
                }
        self.animation = None
        self.saved_state_key = self.state_key = 'idle_' \
                + random.choice(['left', 'right'])
        self.state = self.states[self.state_key]
        self.state.on_start()

    def update(self):
        self.physics.update()
        if self.state:
            self.state.update()
        if self.state_key != self.saved_state_key:
            self.saved_state_key = self.state_key
            self.state.on_end()
            self.state = self.states[self.state_key]
            self.state.on_start()
        self.animation.advance()

    def control(self, control, pred=True):
        try:
            self.state_key = self.transitions[self.state_key][(control, pred)]
        except KeyError:
            pass

    def render(self, graphics):
        graphics.push_state()
        x, y = self.physics.position
        graphics.translate(x, y)
        graphics.draw(self.animation)
        graphics.pop_state()
