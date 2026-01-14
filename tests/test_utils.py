import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from orbit.utils import Vector2D

import math

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

    assert math.isclose(vector_sum.x, vector_a.x + scalar, abs_tol=1e-09)
    assert math.isclose(vector_sum.y, vector_a.y + scalar, abs_tol=1e-09)

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

    assert math.isclose(vector_sum.x, vector_a.x - scalar, abs_tol=1e-09)
    assert math.isclose(vector_sum.y, vector_a.y - scalar, abs_tol=1e-09)

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

    assert math.isclose(vector_sum.x, vector_a.x*scalar, abs_tol=1e-09)
    assert math.isclose(vector_sum.y, vector_a.y*scalar, abs_tol=1e-09)

#--------------------Division--------------------
def test_Vector2D_division_vector():
    vector_a = Vector2D(5, 7)
    vector_b = Vector2D(4, 3)
    vector_sum = vector_a / vector_b

    assert math.isclose(vector_sum.x, vector_a.x/vector_b.x, abs_tol=1e-09)
    assert math.isclose(vector_sum.y, vector_a.y/vector_b.y, abs_tol=1e-09)

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

    assert math.isclose(vector_sum.x, vector_a.x / scalar, abs_tol=1e-09)
    assert math.isclose(vector_sum.y, vector_a.y / scalar, abs_tol=1e-09)

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


if __name__ == "__main__":
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

