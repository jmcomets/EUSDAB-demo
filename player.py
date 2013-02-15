# -*- coding: utf-8 -*-

from random import choice as randomChoice
from PySFML import sf
from physics import Component as PhysicsComponent
from animation import Animation, AnimationFactory
from config import Player as config
import utils

# Player controls
Controls = utils.enum('Left', 'Right', 'Jump', 'Ground', 'Attack', 'End')

# Player state handling
class State(object):
    def __init__(self, model):
        self.model = model

    def OnStart(self):
        pass

    def OnStop(self):
        pass

    def Update(self):
        pass

class AnimatedState(State):
    def __init__(self, model, animation):
        State.__init__(self, model)
        self.animation = animation

    def OnStart(self):
        self.model.animation = self.animation
        self.animation.Reset()

    def OnFinished(self):
        self.model.Control(Controls.End)

    def Update(self):
        State.Update(self)
        if self.animation.IsFinished():
            self.OnFinished()

class MoveState(AnimatedState):
    def __init__(self, model, animation, speed):
        AnimatedState.__init__(self, model, animation)
        self.speed = speed

    def Update(self):
        AnimatedState.Update(self)
        self.model.physics.position.x += self.speed

class JumpState(AnimatedState):
    def __init__(self, model, animation, force):
        AnimatedState.__init__(self, model, animation)
        self.force = force

    def OnStart(self):
        AnimatedState.OnStart(self)
        if self.model.physics.IsOnGround():
            self.model.physics.velocity.y -= self.force

    def Update(self):
        AnimatedState.Update(self)
        if self.model.physics.IsOnGround():
            self.model.Control(Controls.Ground)

class JumpMoveState(AnimatedState):
    def __init__(self, model, animation, speed, force):
        AnimatedState.__init__(self, model, animation)
        self.speed = speed
        self.force = force

    def OnStart(self):
        AnimatedState.OnStart(self)
        if self.model.physics.IsOnGround():
            self.model.physics.velocity.y -= self.force

    def Update(self):
        AnimatedState.Update(self)
        self.model.physics.position.x += self.speed
        if self.model.physics.IsOnGround():
            self.model.Control(Controls.Ground)

class Model(sf.Drawable):
    def __init__(self):
        self.physics = PhysicsComponent(config['size'])
        fact = AnimationFactory()
        self.states = {
                'idle_left': AnimatedState(self, fact.Get('idle_left')),
                'idle_right': AnimatedState(self, fact.Get('idle_right')),
                'walk_left': MoveState(self, fact.Get('walk_left'),
                    -config['speeds']['walk']),
                'walk_right': MoveState(self, fact.Get('walk_right'),
                    config['speeds']['walk']),
                'idle_jump_left': JumpState(self, fact.Get('jump_left', False),
                    config['accelerations']['jump']),
                'idle_jump_right': JumpState(self, fact.Get('jump_right', False),
                    config['accelerations']['jump']),
                'jump_left': JumpMoveState(self, fact.Get('jump_left', False),
                    -config['speeds']['walk'], config['accelerations']['jump']),
                'jump_right': JumpMoveState(self, fact.Get('jump_right', False),
                    config['speeds']['walk'], config['accelerations']['jump']),
                'attack_left': AnimatedState(self, fact.Get('vomit_left', False)),
                'attack_right': AnimatedState(self, fact.Get('vomit_right', False)),
                }
        self.transitions = {
                'idle_left': {
                    (Controls.Left, True): 'walk_left',
                    (Controls.Right, True): 'walk_right',
                    (Controls.Jump, True): 'idle_jump_left',
                    (Controls.Attack, True): 'attack_left'
                    },
                'idle_right': {
                    (Controls.Left, True): 'walk_left',
                    (Controls.Right, True): 'walk_right',
                    (Controls.Jump, True): 'idle_jump_right',
                    (Controls.Attack, True): 'attack_right'
                    },
                'walk_left': {
                    (Controls.Left, False): 'idle_left',
                    (Controls.Right, True): 'walk_right',
                    (Controls.Jump, True): 'jump_left',
                    (Controls.Attack, True): 'attack_left'
                    },
                'walk_right': {
                    (Controls.Left, True): 'walk_left',
                    (Controls.Right, False): 'idle_right',
                    (Controls.Jump, True): 'jump_right',
                    (Controls.Attack, True): 'attack_right'
                    },
                'idle_jump_left': {
                    (Controls.Ground, True): 'idle_left',
                    (Controls.Left, True): 'jump_left',
                    (Controls.Right, True): 'jump_right'
                    },
                'idle_jump_right': {
                    (Controls.Ground, True): 'idle_right',
                    (Controls.Right, True): 'jump_right',
                    (Controls.Left, True): 'jump_left'
                    },
                'jump_left': {
                    (Controls.Ground, True): 'walk_left',
                    (Controls.Left, False): 'idle_jump_left'
                    },
                'jump_right': {
                    (Controls.Ground, True): 'walk_right',
                    (Controls.Right, False): 'idle_jump_right'
                    },
                'attack_left': {
                    (Controls.End, True): 'idle_left'
                    },
                'attack_right': {
                    (Controls.End, True): 'idle_right'
                    }
                }
        self.animation = None
        self.stateKeySave = self.stateKey = 'idle_' + \
                randomChoice(['left', 'right'])
        self.state = self.states[self.stateKey]
        self.state.OnStart()

    def Update(self):
        if self.stateKey != self.stateKeySave:
            self.stateKeySave = self.stateKey
            self.state.OnStop()
            self.state = self.states[self.stateKey]
            self.state.OnStart()
        self.physics.Update()
        self.state.Update()
        self.animation.Advance()

    def Control(self, control, pred=True):
        try:
            self.stateKey = self.transitions[self.stateKey][(control, pred)]
        except KeyError: pass

    def Render(self, target):
        image = self.animation.Current()
        sprite = sf.Sprite(image)
        x, y = self.physics.position
        sprite.SetPosition(x, y)
        target.Draw(sprite)
