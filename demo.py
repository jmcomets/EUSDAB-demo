import os
import app
import player
import config

class Game(app.App):
    def __init__(self):
        super(Game, self).__init__()
        window = self.create_window(title=config.Window['title'],
                size=config.Window['size'])
        self.model = player.Model()
        self.back = app.Image(os.path.join(config.Images['dir'], 'fond.png'))
        self._paused = False

    def key_pressed(self, key):
        super(Game, self).key_pressed(key)
        if key == 'space':
            self._paused = bool(1 - self._paused)
        if key == config.Keyboard['jump']:
            self.model.control(player.Controls.JUMP)
        elif key == config.Keyboard['vomit']:
            self.model.control(player.Controls.ATTACK)

    def update(self):
        if not self._paused:
            if self.is_pressed('left'):
                self.model.control(player.Controls.LEFT)
            elif self.is_pressed('right'):
                self.model.control(player.Controls.RIGHT)
            else:
                self.model.control(player.Controls.RIGHT, False)
                self.model.control(player.Controls.LEFT, False)
            self.model.update()
            # TODO: sleep 25 ms ?

    def render_to(self, window):
        window.draw(self.back)
        window.draw(self.model)
