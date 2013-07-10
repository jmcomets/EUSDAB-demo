from functools import wraps
from PySFML import sf as _sf

# Mapping to readable key
_key_mapping = {
        _sf.Key.A        : 'a',
        _sf.Key.B        : 'b',
        _sf.Key.C        : 'c',
        _sf.Key.D        : 'd',
        _sf.Key.E        : 'e',
        _sf.Key.F        : 'f',
        _sf.Key.G        : 'g',
        _sf.Key.H        : 'h',
        _sf.Key.I        : 'i',
        _sf.Key.J        : 'j',
        _sf.Key.K        : 'k',
        _sf.Key.L        : 'l',
        _sf.Key.M        : 'm',
        _sf.Key.N        : 'n',
        _sf.Key.O        : 'o',
        _sf.Key.P        : 'p',
        _sf.Key.Q        : 'q',
        _sf.Key.R        : 'r',
        _sf.Key.S        : 's',
        _sf.Key.T        : 't',
        _sf.Key.U        : 'u',
        _sf.Key.V        : 'v',
        _sf.Key.W        : 'w',
        _sf.Key.X        : 'x',
        _sf.Key.Y        : 'y',
        _sf.Key.Z        : 'z',
        _sf.Key.Up       : 'up',
        _sf.Key.Down     : 'down',
        _sf.Key.Left     : 'left',
        _sf.Key.Right    : 'right',
        _sf.Key.Space    : 'space',
        _sf.Key.Return   : 'enter',
        _sf.Key.Escape   : 'escape',
        _sf.Key.LAlt     : 'alt',
        _sf.Key.RAlt     : 'alt',
        _sf.Key.LControl : 'ctrl',
        _sf.Key.RControl : 'ctrl',
        _sf.Key.LShift   : 'shift',
        _sf.Key.RShift   : 'shift',
        }
# inverse mapping to a list of *real* keys
_inverse_key_mapping = {}
for key, value in _key_mapping.iteritems():
    _inverse_key_mapping.setdefault(value, []).append(key)

def _real_keys(key):
    assert key in _inverse_key_mapping
    return iter(_inverse_key_mapping[key])

_color_mapping = {
        'red'     : _sf.Color.Red,
        'blue'    : _sf.Color.Blue,
        'cyan'    : _sf.Color.Cyan,
        'black'   : _sf.Color.Black,
        'white'   : _sf.Color.White,
        'green'   : _sf.Color.Green,
        'yellow'  : _sf.Color.Yellow,
        'magenta' : _sf.Color.Magenta,
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
        if closable: style |= _sf.Style.Close
        if resizable: style |= _sf.Style.Resize
        if fullscreen: style |= _sf.Style.Fullscreen
        self._impl = _sf.RenderWindow(_sf.VideoMode(*size), title, style)
        self._impl.EnableKeyRepeat(enable_key_repeat)
        self._impl.SetFramerateLimit(fps)
        self._impl.UseVerticalSync(vsync)
        self._impl.ShowMouseCursor(mouse)
        if icon is not None:
            icon_image = _sf.Image()
            if not icon_image.LoadFromFile(icon):
                raise IOError("Image '%s' couldn't be loaded" % icon)
            self._impl.SetIcon(icon_image.GetWidth(), icon_image.GetHeight(),
                    icon_image.GetPixels())
        self.graphics = Graphics(self)

    def mouse_position(self):
        input_ = self._impl.GetInput()
        x, y = input_.GetMouseX(), input_.GetMouseY()
        return self._impl.ConvertCoords(x, y)

    def set_active(self, active):
        self._impl.SetActive(active)

    def display(self):
        self._impl.Display()

    def clear(self):
        self._impl.Clear()

    def close(self):
        self._impl.Close()

    def is_opened(self):
        return self._impl.IsOpened()

    def draw(self, drawable):
        drawable.render(self.graphics)

    width = property(lambda x: x._impl.GetWidth, lambda x: x._impl.SetWidth)
    height = property(lambda x: x._impl.GetHeight, lambda x: x._impl.SetHeight)

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
            for real_key in _real_keys(key):
                for w in self.windows:
                    if w._impl.GetInput().IsKeyDown(real_key):
                        return True
        return False

    def is_released(self, key):
        if key in _inverse_key_mapping:
            for real_key in _real_keys(key):
                for w in self.windows:
                    if w._impl.GetInput().IsKeyUp(real_key):
                        return True
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
                event = _sf.Event()
                while window._impl.GetEvent(event):
                    if event.Type == _sf.Event.Closed:
                        window.close()
                    elif event.Type == _sf.Event.KeyPressed:
                        key = event.Key.Code
                        if key in _key_mapping:
                            action = _key_mapping[key]
                            self._key_events_bound_to(action, True)
                            self.key_pressed(action)
                    elif event.Type == _sf.Event.KeyReleased:
                        key = event.Key.Code
                        if key in _key_mapping:
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
        self.transform_stack = []
        self.push_transform()
        self.summed_transform = 0, 0

    def _draw(self, drawable):
        assert isinstance(drawable, _sf.Drawable)
        sx, sy = self.summed_transform
        drawable.Move(sx, sy)
        self.window._impl.Draw(drawable)
        drawable.Move(-sx, -sy)

    def translate(self, x, y):
        tx, ty = self.transform_stack[-1]
        sx, sy = self.summed_transform
        tx += x ; ty += y
        sx += x ; sy += y
        self.summed_transform = sx, sy
        self.transform_stack[-1] = tx, ty

    def push_transform(self):
        transform = 0, 0
        self.transform_stack.append(transform)

    def pop_transform(self):
        tx, ty = self.transform_stack.pop()
        sx, sy = self.summed_transform
        sx -= tx ; sy -= ty
        self.summed_transform = sx, sy
        if len(self.transform_stack) == 0:
            self.push_transform()

    def _set_shape_color(self, shape, color):
        if color == 'transparent':
            shape.EnableFill(False)
        else:
            actual_color = _to_actual_color(color)
            for i in xrange(shape.GetNbPoints()):
                shape.SetPointColor(i, actual_color)

    def _set_shape_outline_color(self, shape, color):
        if color == 'transparent':
            shape.EnableOutline(False)
        else:
            actual_color = _to_actual_color(color)
            for i in xrange(shape.GetNbPoints()):
                shape.SetPointOutlineColor(i, actual_color)

    def draw_line(self, start, end, color='white', width=1):
        x, y = start
        w, h = map(lambda x: x[1] - x[0], zip(start, end))
        line = _sf.Shape.Line(0, 0, w, h, width, _sf.Color.White)
        line.SetPosition(x, y)
        self._set_shape_color(line, color)
        self._draw(line)

    def draw_rect(self, start, end, fill_color='white',
            outline_color='transparent', outline_width=0):
        x, y = start
        w, h = map(lambda x: x[1] - x[0], zip(start, end))
        rect = _sf.Shape.Rectangle(0, 0, w, h, _sf.Color.White, outline_width)
        rect.SetPosition(x, y)
        self._set_shape_color(rect, fill_color)
        self._set_shape_outline_color(rect, outline_color)
        self._draw(rect)

    def draw_circle(self, center, radius, fill_color='white',
            outline_color='transparent', outline_width=1):
        circle = _sf.Shape.Circle(0, 0, radius, _sf.Color.White, outline_width)
        circle.SetPosition(*center)
        self._set_shape_color(circle, fill_color)
        self._set_shape_outline_color(circle, outline_color)
        self._draw(circle)

    def draw(self, drawable):
        drawable.render(self)

class Drawable(object):
    def render(self, graphics):
        msg = "'render' method should be defined in custom Drawables"
        raise NotImplementedError(msg)

class Image(Drawable):
    def __init__(self, filename):
        super(Drawable, self).__init__()
        image = _sf.Image()
        if not image.LoadFromFile(filename):
            raise IOError("Image '%s' couldn't be loaded" % filename)
        self._impl = _sf.Sprite(image)

    def render(self, graphics):
        graphics._draw(self._impl)

    @property
    def size(self):
        return self._impl.GetSize()

class Text(Drawable): # TODO add font support
    # style mapping
    _style_mapping = {
            'regular':    0,
            'bold':       1,
            'italic':     2,
            'underlined': 4,
            }

    def __init__(self, text=''):
        self._style = _to_style_strs(0)
        self._impl = _sf.String(str(text))

    def _to_style_strs(self, val):
        style_strs = []
        for key, value in _style_mapping.iteritems():
            if (val | value) == val:
                style_strs.append(key)
        assert_msg = 'Style mapping not bijective, encountered value %s' % val
        assert _to_impl_style(style_strs) == val, assert_msg
        return tuple(style_strs)

    def _to_impl_style(self, style_strs):
        val = 0
        for s in style_strs:
            if s in _style_mapping:
                val |= _style_mapping[s]
            else:
                raise ValueError('Invalid style %s' % s)
        return val

    @property
    def style(self):
        return self._to_style_strs(self._impl.GetStyle())

    @style.setter
    def set_style(self, style_strs):
        self._impl.SetStyle(self._to_impl_style(style_strs))

    @property
    def text(self):
        return self._impl.GetText()

    @text.setter
    def set_text(self, text):
        self._impl.SetText(str(text))

    def render(self, graphics):
        graphics._draw(self._impl)

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
