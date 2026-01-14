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