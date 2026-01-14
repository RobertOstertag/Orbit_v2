import math

class Vector2D:
    def __init__(self, pos_x:float, pos_y:float):
        self.x = pos_x
        self.y = pos_y
    
    def __add__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x + other.x, self.y + other.y)
        elif (isinstance(other, float) or isinstance(other, int)):
            return Vector2D(self.x + other, self.y + other)
        return NotImplemented
    
    def __sub__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x - other.x, self.y - other.y)
        elif (isinstance(other, float) or isinstance(other, int)):
            return Vector2D(self.x - other, self.y - other)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x * other.x, self.y * other.y)
        elif (isinstance(other, float) or isinstance(other, int)):
            return Vector2D(self.x * other, self.y * other)
        return NotImplemented
    
    def __truediv__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x / other.x, self.y / other.y)
        elif (isinstance(other, float) or isinstance(other, int)):
            return Vector2D(self.x / other, self.y / other)
        return NotImplemented
    
    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normalize(self):
        magn = self.magnitude()
        if (magn != 0):
            return Vector2D(self.x / magn, self.y / magn)
        else:
            raise ValueError('Vector2D is of length 0')

class Color:
    def __init__(self, h, s, v):
        self.h = h/360
        self.s = s
        self.v = v
        rgb = self.hsv_to_rgb(self.h, self.s, self.v)
        self.r = rgb[0] * 255
        self.g = rgb[1] * 255
        self.b = rgb[2] * 255

    scalar = float
    def hsv_to_rgb(self, h:scalar, s:scalar, v:scalar) -> tuple:
        if s:
            if h == 1.0: h = 0.0
            i = int(h*6.0); f = h*6.0 - i

            w = v * (1.0 -s)
            q = v * (1.0 -s * f)
            t = v * (1.0 - s * (1.0 - f))

            if i == 0: return (v, t, w)
            if i == 1: return (q, v, w)
            if i == 2: return (w, v, t)
            if i == 3: return (w, q, v)
            if i == 4: return (t, w, v)
            if i == 5: return (v, w, q)
            if i >= 6: return (0, 0, 0)
        else: return (v, v, v)