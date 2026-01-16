#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from orbit.utils import Vector2D
from orbit.utils import Color

import math
import pytest

#------------------------------------------------
#--------------------Vector2D--------------------
#------------------------------------------------

#--------------------Init--------------------
def test_Vector2D_init():
    vector_a = Vector2D(5, 7)
    assert vector_a.x == 5
    assert vector_a.y == 7


#--------------------Addition--------------------
def test_Vector2D_addition():
    vector_a = Vector2D(5, 7)
    vector_b = Vector2D(4, 3)
    result = vector_a + vector_b

    assert result.x == vector_a.x + vector_b.x
    assert result.y == vector_a.y + vector_b.y

def test_Vector2D_addition_error():
    vector_a = Vector2D(5, 7)

    with pytest.raises(TypeError, match="Second addition operand is not of type Vector2D"):
        result = vector_a + 5


#--------------------Subtraction--------------------
def test_Vector2D_subtraction():
    vector_a = Vector2D(5, 7)
    vector_b = Vector2D(4, 3)
    result = vector_a - vector_b

    assert result.x == vector_a.x - vector_b.x
    assert result.y == vector_a.y - vector_b.y

def test_Vector2D_subtraction_error():
    vector_a = Vector2D(5, 7)

    with pytest.raises(TypeError, match="Second subtraction operand is not of type Vector2D"):
        result = vector_a - 5



#--------------------Multiplication--------------------
def test_Vector2D_multiplication_int():
    vector_a = Vector2D(5, 7)
    scalar = 5
    result = vector_a * scalar

    assert result.x == vector_a.x * scalar
    assert result.y == vector_a.y * scalar

def test_Vector2D_multiplication_float():
    vector_a = Vector2D(5, 7)
    scalar = 5.3
    result = vector_a * scalar

    assert result.x == vector_a.x*scalar
    assert result.y == vector_a.y*scalar

def test_Vector2D_multiplication_int_reverse():
    vector_a = Vector2D(5, 7)
    scalar = 5
    result = scalar * vector_a

    assert result.x == scalar * vector_a.x
    assert result.y == scalar * vector_a.y

def test_Vector2D_multiplication_float_reverse():
    vector_a = Vector2D(5, 7)
    scalar = 5.3
    result = scalar * vector_a

    assert result.x == scalar * vector_a.x
    assert result.y == scalar * vector_a.y

def test_Vector2D_multiplication_error():
    vector_a = Vector2D(5, 7)
    vector_b = Vector2D(4, 3)

    with pytest.raises(TypeError, match="Second multiplication operand is not of type int or float"):
        result = vector_a * vector_b


#--------------------Division--------------------
def test_Vector2D_division_int():
    vector_a = Vector2D(5, 7)
    scalar = 5
    result = vector_a / scalar

    assert result.x == vector_a.x / scalar
    assert result.y == vector_a.y / scalar

def test_Vector2D_division_float():
    vector_a = Vector2D(5, 7)
    scalar = 5.3
    result = vector_a / scalar

    assert result.x == vector_a.x / scalar
    assert result.y == vector_a.y / scalar

def test_Vector2D_division_int_reverse():
    vector_a = Vector2D(5, 7)
    scalar = 5
    result = scalar / vector_a

    assert result.x == scalar / vector_a.x
    assert result.y == scalar / vector_a.y

def test_Vector2D_division_float_reverse():
    vector_a = Vector2D(5, 7)
    scalar = 5.3
    result = scalar / vector_a

    assert result.x == scalar / vector_a.x
    assert result.y == scalar / vector_a.y

def test_Vector2D_division_error():
    vector_a = Vector2D(5, 7)
    vector_b = Vector2D(4, 3)

    with pytest.raises(TypeError, match="Second division operand is not of type int or float"):
        result = vector_a / vector_b


#--------------------Dot Product--------------------
def test_Vector2D_dot_product():
    vector_a = Vector2D(5, 7)
    vector_b = Vector2D(4, 3)

    result = vector_a.dot(vector_b)

    assert result.x == vector_a.x * vector_b.x
    assert result.y == vector_a.y * vector_b.y

def test_Vector2D_dot_product_error():
    vector_a = Vector2D(5, 7)

    with pytest.raises(TypeError, match="Second dot product operand is not of type Vector2D"):
        result = vector_a.dot(9)


#--------------------Magnitude--------------------
def test_Vector2D_magnitude():
    vector_a = Vector2D(5, 7)
    magn = vector_a.magnitude()

    assert magn == math.sqrt(vector_a.x * vector_a.x + vector_a.y * vector_a.y)


#--------------------Normalize--------------------
def test_Vector2D_normalize():
    vector_a = Vector2D(5, 7)
    norm = vector_a.normalize()

    assert norm.x == vector_a.x / math.sqrt(vector_a.x * vector_a.x + vector_a.y * vector_a.y)
    assert norm.y == vector_a.y / math.sqrt(vector_a.x * vector_a.x + vector_a.y * vector_a.y)


#--------------------Normalize 0--------------------
def test_Vector2D_normalize_zero():
    vector_a = Vector2D(0, 0)

    with pytest.raises(ValueError, match="Vector2D is of length 0"):
        vector_a.normalize()



#---------------------------------------------
#--------------------Color--------------------
#---------------------------------------------
def test_Color():
    color_1 = Color(100, 0.5, 0.6)
    assert color_1.h * 360 == 100
    assert color_1.s == 0.5
    assert color_1.v == 0.6

    r, g, b = color_1.get_rgb_8bit()
    assert r == 101
    assert g == 153
    assert b == 76

    color_2 = Color(400, 0.0, 1.0)
    assert color_2.h * 360 == 400 % 360
    assert color_2.s == 0.0
    assert color_2.v == 1.0

    r, g, b = color_2.get_rgb_8bit()
    assert r == 255
    assert g == 255
    assert b == 255

if __name__ == "__main__":
    #Vector2D
    test_Vector2D_init()

    test_Vector2D_addition()
    test_Vector2D_addition_error()

    test_Vector2D_subtraction()
    test_Vector2D_subtraction_error()

    test_Vector2D_multiplication_int()
    test_Vector2D_multiplication_float()
    test_Vector2D_multiplication_int_reverse()
    test_Vector2D_multiplication_float_reverse()
    test_Vector2D_multiplication_error()

    test_Vector2D_division_int()
    test_Vector2D_division_float()
    test_Vector2D_division_int_reverse()
    test_Vector2D_division_float_reverse()
    test_Vector2D_division_error()

    test_Vector2D_dot_product()
    test_Vector2D_dot_product_error()

    test_Vector2D_magnitude()
    test_Vector2D_normalize()
    test_Vector2D_normalize_zero()

    #Color
    test_Color()

    print("All tests completed")

