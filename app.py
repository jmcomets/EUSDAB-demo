from functools import wraps
import sfml as _sf

# Mapping to readable key
_key_mapping = {
        _sf.Keyboard.A        : 'a',
        _sf.Keyboard.B        : 'b',
        _sf.Keyboard.C        : 'c',
        _sf.Keyboard.D        : 'd',
        _sf.Keyboard.E        : 'e',
        _sf.Keyboard.F        : 'f',
        _sf.Keyboard.G        : 'g',
        _sf.Keyboard.H        : 'h',
        _sf.Keyboard.I        : 'i',
        _sf.Keyboard.J        : 'j',
        _sf.Keyboard.K        : 'k',
        _sf.Keyboard.L        : 'l',
        _sf.Keyboard.M        : 'm',
        _sf.Keyboard.N        : 'n',
        _sf.Keyboard.O        : 'o',
        _sf.Keyboard.P        : 'p',
        _sf.Keyboard.Q        : 'q',
        _sf.Keyboard.R        : 'r',
        _sf.Keyboard.S        : 's',
        _sf.Keyboard.T        : 't',
        _sf.Keyboard.U        : 'u',
        _sf.Keyboard.V        : 'v',
        _sf.Keyboard.W        : 'w',
        _sf.Keyboard.X        : 'x',
        _sf.Keyboard.Y        : 'y',
        _sf.Keyboard.Z        : 'z',
        _sf.Keyboard.UP       : 'up',
        _sf.Keyboard.DOWN     : 'down',
        _sf.Keyboard.LEFT     : 'left',
        _sf.Keyboard.RIGHT    : 'right',
        _sf.Keyboard.SPACE    : 'space',
        _sf.Keyboard.RETURN   : 'enter',
        _sf.Keyboard.ESCAPE   : 'escape',
        _sf.Keyboard.L_ALT     : 'alt',
        _sf.Keyboard.R_ALT     : 'alt',
        _sf.Keyboard.L_CONTROL : 'ctrl',
        _sf.Keyboard.R_CONTROL : 'ctrl',
        _sf.Keyboard.L_SHIFT   : 'shift',
        _sf.Keyboard.R_SHIFT   : 'shift',
        }
# inverse mapping to a list of *real* keys
_inverse_key_mapping = {}
for key, value in _key_mapping.iteritems():
    _inverse_key_mapping.setdefault(value, []).append(key)

def _real_keys(key):
    assert key in _inverse_key_mapping
    return iter(_inverse_key_mapping[key])

_color_mapping = {
        'red'         :  _sf.Color.RED,
        'blue'        :  _sf.Color.BLUE,
        'cyan'        :  _sf.Color.CYAN,
        'black'       :  _sf.Color.BLACK,
        'white'       :  _sf.Color.WHITE,
        'green'       :  _sf.Color.GREEN,
        'yellow'      :  _sf.Color.YELLOW,
        'magenta'     :  _sf.Color.MAGENTA,
        'transparent' :  _sf.Color.TRANSPARENT,
        }

def _to_actual_color(color):
    if isinstance(color, str):
        if color not in _color_mapping:
            raise ValueError("Invalid color")
        return _color_mapping[color]
    elif isinstance(color, int):
        b = (color >> (8 * 0)) & 0xff
        g = (color >> (8 * 1)) & 0xff
        r = (color >> (8 * 2)) & 0xff
        color = r, g, b
    return _sf.Color(*color)

class Listener(object):
    def update(self):
        pass

    def key_pressed(self, key):
        pass

    def key_released(self, key):
        pass

class Window(object):
    def __init__(self, size=(800, 600), title=__name__, fps=40, icon=None,
            closable=True, resizable=False, mouse=True, vsync=True,
            fullscreen=False, enable_key_repeat=False):
        style = 0
        if closable: style |= _sf.Style.CLOSE
        if resizable: style |= _sf.Style.RESIZE
        if fullscreen: style |= _sf.Style.FULLSCREEN
        self._impl = _sf.RenderWindow(_sf.VideoMode(*size), title, style)
        self._impl.key_repeat_enabled = enable_key_repeat
        self._impl.framerate_limit = fps
        self._impl.vertical_synchronization = vsync
        self._impl.mouse_cursor_visible = mouse
        if icon is not None:
            icon_image = _sf.Image.from_file(icon)
            self._impl.icon = icon_image.pixels
        self.graphics = Graphics(self)

    def mouse_position(self):
        return _sf.Mouse.get_position(self._impl)

    def set_active(self, active):
        self._impl.active = active

    def display(self):
        self._impl.display()

    def clear(self):
        self._impl.clear()

    def close(self):
        self._impl.close()

    def is_opened(self):
        return self._impl.is_open

    def draw(self, drawable):
        drawable.render(self.graphics)

    @property
    def width(self):
        return self._impl.width

    @width.setter
    def set_width(self, w):
        self._impl.width = w

    @property
    def height(self):
        return self._impl.height

    @height.setter
    def set_height(self, h):
        self._impl.height = h

class App(Listener):
    def __init__(self):
        super(App, self).__init__()
        self.windows = []
        self.key_events = []

    def bind_key_event(self, f, bind_key=None, on_press=True):
        if not callable(f):
            raise TypeError("Bind object '%s' should be callable" % f)
        self.key_events.append((bool(on_press), bind_key, f))

    def key_event(self, bind_key=None, on_press=True):
        @wraps(f)
        def closure(f):
            self.bind_key_event(f, bind_key=bind_key, on_press=on_press)
            return f
        return closure

    def is_pressed(self, key):
        if key in _inverse_key_mapping:
            kb = _sf.Keyboard
            return any(kb.is_key_pressed(k) for k in _real_keys(key))
        return False

    def is_released(self, key):
        if key in _inverse_key_mapping:
            kb = _sf.Keyboard
            return any(not kb.is_key_pressed(k) for k in _real_keys(key))
        return False

    def _key_events_bound_to(self, key, on_press):
        def decide_if_callback(key, bind):
            if bind is None:
                return True
            elif isinstance(bind, (tuple, list)):
                return key in bind
            elif isinstance(bind, str):
                return key == bind
            else:
                raise TypeError("Invalid bind '%s'" % bind)
        for p, bind, callback in self.key_events:
            if p == on_press:
                if decide_if_callback(key, bind):
                    callback()

    def run(self):
        while self.windows:
            closed = []
            for window in self.windows:
                for event in window._impl.events:
                    if type(event) is _sf.CloseEvent:
                        window.close()
                    elif type(event) is _sf.KeyEvent:
                        if event.code not in _key_mapping:
                            continue
                        key = event.code
                        if event.pressed:
                            action = _key_mapping[key]
                            self._key_events_bound_to(action, True)
                            self.key_pressed(action)
                        else:
                            action = _key_mapping[key]
                            self._key_events_bound_to(action, False)
                            self.key_released(action)
                self.update()
                window.clear()
                self.render_to(window)
                window.display()
                if not window.is_opened():
                    closed.append(window)
            for window in closed:
                self.windows.remove(window)

    def create_window(self, dtype=Window, *args, **kwargs):
        win = dtype(*args, **kwargs)
        self.windows.append(win)
        return win

    def render_to(self, window):
        pass

class Graphics(object):
    def __init__(self, window):
        self.window = window
        self.graphic_states = []
        self.push_state()

    def _draw(self, drawable):
        assert isinstance(drawable, _sf.Drawable)
        self.window._impl.draw(drawable, self.graphic_states[-1])

    def translate(self, x, y):
        state = self.graphic_states[-1]
        state.transform.translate(_sf.Vector2(x, y))

    def push_state(self):
        state = _sf.RenderStates()
        if len(self.graphic_states) > 0:
            old_state = self.graphic_states[-1]
            state.transform.combine(old_state.transform)
        self.graphic_states.append(state)

    def pop_state(self):
        self.graphic_states.pop()
        if len(self.graphic_states) == 0:
            self.push_state()

    def draw(self, drawable):
        drawable.render(self)

class Drawable(object):
    def render(self, graphics):
        msg = "'render' method should be defined in custom Drawables"
        raise NotImplementedError(msg)

class Image(Drawable):
    def __init__(self, filename):
        super(Drawable, self).__init__()
        tx = _sf.Texture.from_file(filename)
        self._impl = _sf.Sprite(tx)

    def render(self, graphics):
        graphics._draw(self._impl)

    size = property(lambda x: x._impl.size)

class StatesApp(App):
    def __init__(self):
        super(StatesApp, self).__init__()
        self.states = {}
        self.current = None
        try:
            self.init_states()
        except NotImplementedError:
            msg = 'Current state should be set in init_states'
            raise NotImplementedError(msg)

    def init_states(self):
        raise NotImplementedError

    def add_state(self, state_id, state):
        if state_id in self.states:
            raise KeyError('State %s already defined' % state_id)
        self.states[state_id] = state

    def switch_state(self, state_id):
        if state_id not in self.states:
            raise KeyError('Undefined state %s' % state_id)
        s = self.states[state_id]
        if self.current is not None:
            self.current.leave()
        self.current = s
        self.current.enter()
        self.current.alive = True

    def set_state(self, state_id):
        if state_id not in self.states:
            raise KeyError('Undefined state %s' % state_id)
        self.current = self.states[state_id]
        self.current.enter()

    def update(self):
        self.current.update()
        if not self.current.alive:
            self.switch_state(self.current.next_state)

    def render_to(self, window):
        self.current.render_to(window)

class BaseState(Listener):
    def __init__(self):
        super(BaseState, self).__init__()
        self.alive = True
        self.next_state = None

    def switch_state(self, state_id):
        self.alive = False
        self.next_state = state_id

    def enter(self): pass
    def leave(self): pass
