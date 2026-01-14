import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
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
def test_Vector2D_addition_vector():
    vector_a = Vector2D(5, 7)
    vector_b = Vector2D(4, 3)
    vector_sum = vector_a + vector_b

    assert vector_sum.x == vector_a.x + vector_b.x
    assert vector_sum.y == vector_a.y + vector_b.y

def test_Vector2D_addition_scalar_int():
    vector_a = Vector2D(5, 7)
    scalar = 5
    vector_sum = vector_a + scalar

    assert vector_sum.x == vector_a.x + scalar
    assert vector_sum.y == vector_a.y + scalar

def test_Vector2D_addition_scalar_float():
    vector_a = Vector2D(5, 7)
    scalar = 5.3
    vector_sum = vector_a + scalar

    assert vector_sum.x == vector_a.x + scalar
    assert vector_sum.y == vector_a.y + scalar

#--------------------Subtraction--------------------
def test_Vector2D_subtraction_vector():
    vector_a = Vector2D(5, 7)
    vector_b = Vector2D(4, 3)
    vector_sum = vector_a - vector_b

    assert vector_sum.x == vector_a.x - vector_b.x
    assert vector_sum.y == vector_a.y - vector_b.y

def test_Vector2D_subtraction_scalar_int():
    vector_a = Vector2D(5, 7)
    scalar = 5
    vector_sum = vector_a - scalar

    assert vector_sum.x == vector_a.x - scalar
    assert vector_sum.y == vector_a.y - scalar

def test_Vector2D_subtraction_scalar_float():
    vector_a = Vector2D(5, 7)
    scalar = 5.3
    vector_sum = vector_a - scalar

    assert vector_sum.x == vector_a.x - scalar
    assert vector_sum.y == vector_a.y - scalar

#--------------------Multiplication--------------------
def test_Vector2D_multiplication_vector():
    vector_a = Vector2D(5, 7)
    vector_b = Vector2D(4, 3)
    vector_sum = vector_a * vector_b

    assert vector_sum.x == vector_a.x * vector_b.x
    assert vector_sum.y == vector_a.y * vector_b.y

def test_Vector2D_multiplication_scalar_int():
    vector_a = Vector2D(5, 7)
    scalar = 5
    vector_sum = vector_a * scalar

    assert vector_sum.x == vector_a.x * scalar
    assert vector_sum.y == vector_a.y * scalar

def test_Vector2D_multiplication_scalar_float():
    vector_a = Vector2D(5, 7)
    scalar = 5.3
    vector_sum = vector_a * scalar

    assert vector_sum.x == vector_a.x*scalar
    assert vector_sum.y == vector_a.y*scalar

#--------------------Division--------------------
def test_Vector2D_division_vector():
    vector_a = Vector2D(5, 7)
    vector_b = Vector2D(4, 3)
    vector_sum = vector_a / vector_b

    assert vector_sum.x == vector_a.x/vector_b.x
    assert vector_sum.y == vector_a.y/vector_b.y

def test_Vector2D_division_scalar_int():
    vector_a = Vector2D(5, 7)
    scalar = 5
    vector_sum = vector_a / scalar

    assert vector_sum.x == vector_a.x / scalar
    assert vector_sum.y == vector_a.y / scalar

def test_Vector2D_division_scalar_float():
    vector_a = Vector2D(5, 7)
    scalar = 5.3
    vector_sum = vector_a / scalar

    assert vector_sum.x == vector_a.x / scalar
    assert vector_sum.y == vector_a.y / scalar

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
    test_Vector2D_addition_vector()
    test_Vector2D_addition_scalar_int()
    test_Vector2D_addition_scalar_float()
    test_Vector2D_subtraction_vector()
    test_Vector2D_subtraction_scalar_int()
    test_Vector2D_subtraction_scalar_float()
    test_Vector2D_multiplication_vector()
    test_Vector2D_multiplication_scalar_int()
    test_Vector2D_multiplication_scalar_float()
    test_Vector2D_division_vector()
    test_Vector2D_division_scalar_int()
    test_Vector2D_division_scalar_float()
    test_Vector2D_magnitude()
    test_Vector2D_normalize()
    test_Vector2D_normalize_zero()

    #Color
    test_Color()

