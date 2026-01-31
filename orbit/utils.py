import math
import threading
import queue

class Vector2D:
    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x + other.x, self.y + other.y)
        raise TypeError("Second addition operand is not of type Vector2D")
    
    def __sub__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x - other.x, self.y - other.y)
        raise TypeError("Second subtraction operand is not of type Vector2D")

    def __mul__(self, scalar):
        if (isinstance(scalar, float) or isinstance(scalar, int)):
            return Vector2D(self.x * scalar, self.y * scalar)
        raise TypeError("Second multiplication operand is not of type int or float")
    
    def __rmul__(self, scalar):
        if (isinstance(scalar, float) or isinstance(scalar, int)):
            return Vector2D(scalar * self.x, scalar * self.y)
        raise TypeError("First multiplication operand is not of type int or float")

    def __truediv__(self, scalar):
        if (isinstance(scalar, float) or isinstance(scalar, int)):
            return Vector2D(self.x / scalar, self.y / scalar)
        raise TypeError("Second division operand is not of type int or float")
    
    def __rtruediv__(self, scalar):
        if (isinstance(scalar, float) or isinstance(scalar, int)):
            return Vector2D(scalar / self.x, scalar / self.y)
        raise TypeError("First division operand is not of type int or float")
    
    def dot(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x * other.x, self.y * other.y)
        raise TypeError("Second dot product operand is not of type Vector2D")
    
    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normalize(self):
        magn = self.magnitude()
        if (magn != 0):
            return Vector2D(self.x / magn, self.y / magn)
        else:
            raise ValueError("Vector2D is of length 0")

class Color:
    def __init__(self, h:float, s:float, v:float):
        if (h < 0) or (s < 0) or (v < 0):
            raise ValueError("All arguments have to be above 0")

        self.h = (h % 360) / 360

        if s <= 1:
            self.s = s
        else:
            self.s = s % 1

        if v <= 1:
            self.v = v
        else:
            self.v = v % 1

        self.r, self.g, self.b = self.hsv_to_rgb(self.h, self.s, self.v)

    def get_rgb_8bit(self):
        return int(self.r * 255), int(self.g * 255), int(self.b * 255)

    scalar = float
    def hsv_to_rgb(self, h:scalar, s:scalar, v:scalar) -> tuple:
        if s:
            if h == 1.0: h = 0.0
            i = int(h*6.0); f = h*6.0 - i

            w = v * (1.0 -s)
            q = v * (1.0 -s * f)
            t = v * (1.0 - s * (1.0 - f))

            if i == 0: return [v, t, w]
            if i == 1: return [q, v, w]
            if i == 2: return [w, v, t]
            if i == 3: return [w, q, v]
            if i == 4: return [t, w, v]
            if i == 5: return [v, w, q]
            if i >= 6: return [0, 0, 0]
        else: return [v, v, v]

class CelestialBody:
    def __init__(self, pos:Vector2D, vel:Vector2D, mass, radius, color_h = 360, color_s = 1.0, color_v = 1.0):
        self.pos = pos
        self.vel = vel
        self.acc = Vector2D(0.0, 0.0)
        self.prev_pos = self.pos - vel #only used for verlet integration
        self.prev_acc = Vector2D(0.0, 0.0) #used for velocity verlet integration
        self.mass = mass
        self.radius = radius
        self.color = Color(color_h, color_s, color_v)
    
    def __eq__(self, other):
        if self.mass == other.mass \
        and self.pos.x == other.pos.x \
        and self.pos.y == other.pos.y \
        and self.vel.x == other.vel.x \
        and self.vel.y == other.vel.y:
            return True
        else:
            return False

class UserInputData:
    def __init__(self):
        self.index = 0
        self.mass = 0
        self.pos = Vector2D(0, 0)
        self.vel = Vector2D(0, 0)

class InterfaceItem:
    def __init__(self, initial=None, trigger=False):
        self._value = initial
        self._lock = threading.Lock()
        self._trigger = trigger
    
    def send(self, value):
        with self._lock:
            self._value = value

    def receive(self):
        with self._lock:
            return self._value
    
    def trigger(self):
        with self._lock:
            self._trigger = True

    def is_triggered(self):
        with self._lock:
            return_val = self._trigger
            self._trigger = False
            return return_val

class Interface:
    def __init__(self):
        self.bodies = InterfaceItem()
        self.engine_timestep = InterfaceItem(0)
        self.engine_duration = InterfaceItem(0)
        self.marked_body_index = InterfaceItem(0)
        self.selected_preset = InterfaceItem("Figure Eight", True)
        self.user_input = InterfaceItem()

        self.events = EventContainer()

class EventContainer:
    def __init__(self):
        self.stop = threading.Event()
        self.initialize_window = threading.Event()
        self.running = threading.Event()
        self.load_preset = threading.Event()
        self.dt_increment = threading.Event()
        self.dt_decrement = threading.Event()
        #user input
        self.add_body = threading.Event()
        self.delete_body = threading.Event()
        self.update_body = threading.Event()
        self.add_shape = threading.Event()
        self.delete_shape = threading.Event()
        self.update_shape = threading.Event()