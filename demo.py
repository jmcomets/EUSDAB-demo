# -*- coding: utf-8 -*-

from PySFML import sf
import player
import config

class Game(object):
    def __init__(self):
        videoMode = sf.VideoMode(*config.Window['size'])
        self.window = sf.RenderWindow(videoMode, config.Window['title'])
        self.model = player.Model()
        self.alive = True
        self.active = True
        image = sf.Image()
        image.LoadFromFile(config.Images['dir'] + '/fond.png')
        self.back = sf.Sprite(image)

    def Update(self):
        self.input_()
        if self.active:
            self.logic()
        self.display()

    def input_(self):
        event = sf.Event()
        while self.window.GetEvent(event):
            if event.Type == sf.Event.Closed:
                self.alive = False
            elif event.Type == sf.Event.KeyPressed and event.Key.Code == sf.Key.Space:
                self.active = bool(1 - self.active)
            elif self.active:
                if config.Window['control'] == 'keyboard':
                    if event.Type == sf.Event.KeyPressed:
                        if event.Key.Code == config.Keyboard['jump']:
                            self.model.Control(player.Controls.Jump)
                        elif event.Key.Code == config.Keyboard['vomit']:
                            self.model.Control(player.Controls.Attack)
                elif config.Window['control'] == 'joystick':
                    if event.Type == sf.Event.JoyButtonPressed:
                        if event.JoyButton.Button == config.Joystick['vomit']:
                            self.model.Control(player.Controls.Attack)
                        #elif event.JoyButton.Button == config.Joystick['jump']:
                            #self.model.Control(player.Controls.Jump)
        if self.active:
            appInput = self.window.GetInput()
            if config.Window['control'] == 'keyboard':
                if appInput.IsKeyDown(sf.Key.Left):
                    self.model.Control(player.Controls.Left)
                elif appInput.IsKeyDown(sf.Key.Right):
                    self.model.Control(player.Controls.Right)
                else:
                    self.model.Control(player.Controls.Right, False)
                    self.model.Control(player.Controls.Left, False)
            elif config.Window['control'] == 'joystick':
                joyY = appInput.GetJoystickAxis(config.Joystick['id'], sf.Joy.AxisY)
                if joyY < 0:
                    self.model.Control(player.Controls.Jump)
                joyX = appInput.GetJoystickAxis(config.Joystick['id'], sf.Joy.AxisX)
                if joyX > 0:
                    self.model.Control(player.Controls.Right)
                elif joyX < 0:
                    self.model.Control(player.Controls.Left)
                else:
                    self.model.Control(player.Controls.Right, False)
                    self.model.Control(player.Controls.Left, False)

    def logic(self):
        self.model.Update()
        sf.Sleep(0.025)

    def display(self):
        self.window.Clear()
        self.window.Draw(self.back)
        self.window.Draw(self.model)
        self.window.Display()

if __name__ == '__main__':
    game = Game()
    while game.alive: game.Update()
