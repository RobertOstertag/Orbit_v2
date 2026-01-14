from orbit.utils import Vector2D


def test_Vector2D_addition():
    vector_a = Vector2D(1, 2)
    vector_b = Vector2D(3, 4)
    vector_sum = vector_a + vector_b

    assert vector_sum.x == 4
    assert vector_sum.y == 6

def test_Vector2D_subtraction():
    vector_a = Vector2D(1, 2)
    vector_b = Vector2D(3, 4)
    vector_sum = vector_b - vector_a

    assert vector_sum.x == 2
    assert vector_sum.y == 2