#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from orbit.utils import Vector2D
from orbit.gravity_engine import GravityEngine, CelestialBody

import math

def test_GravityEngine_energy_euler_1_body():
    print("Energy test for 1 body with Euler Method")
    body_list = [
        CelestialBody(pos=Vector2D(+0,  +0), vel=Vector2D(+1, +3), mass=1000)
    ]
    gravity_engine = GravityEngine(body_list, alghorithm=0)
    gravity_engine.change_dt(0.5)
    check_energy(body_list, 10000, gravity_engine, 2/100)

def test_GravityEngine_energy_euler_2_body():
    print("Energy test for 2 bodies with Euler Method")
    body_list = [
        CelestialBody(pos=Vector2D(+0,  +0), vel=Vector2D(+0, +0), mass=1000),
        CelestialBody(pos=Vector2D(+85, +0), vel=Vector2D(+0, +4), mass=1),
    ]
    gravity_engine = GravityEngine(body_list, alghorithm=0)
    gravity_engine.change_dt(0.5)
    check_energy(body_list, 10000, gravity_engine, 2/100)

def test_GravityEngine_energy_euler_3_body():
    print("Energy test for 6 bodies with Euler Method")
    body_list = [
        CelestialBody(Vector2D(+0,  +0),  Vector2D(+0, +0),   1000),
        CelestialBody(Vector2D(+50, +0),  Vector2D(+0, +5),   1),
        CelestialBody(Vector2D(-50, +0),  Vector2D(+0, -5),   1)
    ]
    gravity_engine = GravityEngine(body_list, alghorithm=0)
    gravity_engine.change_dt(0.1)
    check_energy(body_list, 10000, gravity_engine, 2/100)



def test_GravityEngine_energy_verlet_1_body():
    print("Energy test for 1 body with Verlet Method")
    body_list = [
        CelestialBody(pos=Vector2D(+0,  +0), vel=Vector2D(+1, +3), mass=1000)
    ]
    gravity_engine = GravityEngine(body_list, alghorithm=1)
    gravity_engine.change_dt(0.5)
    check_energy(body_list, 10000, gravity_engine, 2/100)

def test_GravityEngine_energy_verlet_2_body():
    print("Energy test for 2 bodies with Verlet Method")
    body_list = [
        CelestialBody(pos=Vector2D(+0,  +0), vel=Vector2D(+0, +0), mass=1000),
        CelestialBody(pos=Vector2D(+85, +0), vel=Vector2D(+0, +4), mass=1),
    ]
    gravity_engine = GravityEngine(body_list, alghorithm=1)
    gravity_engine.change_dt(0.5)
    check_energy(body_list, 10000, gravity_engine, 2/100)

def test_GravityEngine_energy_verlet_3_body():
    print("Energy test for 6 bodies with Verlet Method")
    body_list = [
        CelestialBody(Vector2D(+0,  +0),  Vector2D(+0, +0),   1000),
        CelestialBody(Vector2D(+50, +0),  Vector2D(+0, +5),   1),
        CelestialBody(Vector2D(-50, +0),  Vector2D(+0, -5),   1)
    ]
    gravity_engine = GravityEngine(body_list, alghorithm=1)
    gravity_engine.change_dt(0.1)
    check_energy(body_list, 10000, gravity_engine, 2/100)



def test_GravityEngine_energy_velocity_verlet_1_body():
    print("Energy test for 1 body with Velocity Verlet Method")
    body_list = [
        CelestialBody(pos=Vector2D(+0,  +0), vel=Vector2D(+1, +3), mass=1000)
    ]
    gravity_engine = GravityEngine(body_list, alghorithm=2)
    gravity_engine.change_dt(0.5)
    check_energy(body_list, 10000, gravity_engine, 2/100)

def test_GravityEngine_energy_velocity_verlet_2_body():
    print("Energy test for 2 bodies with Velocity Verlet Method")
    body_list = [
        CelestialBody(pos=Vector2D(+0,  +0), vel=Vector2D(+0, +0), mass=1000),
        CelestialBody(pos=Vector2D(+85, +0), vel=Vector2D(+0, +4), mass=1),
    ]
    gravity_engine = GravityEngine(body_list, alghorithm=2)
    gravity_engine.change_dt(0.5)
    check_energy(body_list, 10000, gravity_engine, 2/100)

def test_GravityEngine_energy_velocity_verlet_3_body():
    print("Energy test for 6 bodies with Velocity Verlet Method")
    body_list = [
        CelestialBody(Vector2D(+0,  +0),  Vector2D(+0, +0),   1000),
        CelestialBody(Vector2D(+50, +0),  Vector2D(+0, +5),   1),
        CelestialBody(Vector2D(-50, +0),  Vector2D(+0, -5),   1)
    ]
    gravity_engine = GravityEngine(body_list, alghorithm=2)
    gravity_engine.change_dt(0.1)
    check_energy(body_list, 10000, gravity_engine, 2/100)


def check_energy(body_list, iterations, engine, error_value):
    #initial energy of system
    initial_energy = calculate_system_energy(body_list)
    print("Initial Energy of System ", initial_energy)

    #do many iterations of simulation steps
    for iter in range(iterations):
        engine.update()

    final_energy = calculate_system_energy(body_list)
    print("Energy of System after", iterations, "Iterations:", final_energy)
    print("Difference:", abs(initial_energy - final_energy))
    print()
    assert math.isclose(initial_energy - final_energy, 0.0, abs_tol=error_value)

def calculate_system_energy(body_list):
    kinetic_energy = 0
    gravity_energy = 0
    for body in body_list:
        kinetic_energy += 0.5 * body.mass * body.vel.magnitude() * body.vel.magnitude()

    i = 0
    for body in body_list:
        j = 0
        for other_body in body_list:
            #only calculate half of every combination because it is redundant
            if i < j:
                gravity_energy += -(body_list[i].mass * body_list[j].mass) / (body_list[i].pos - body_list[j].pos).magnitude()
            j += 1
        i += 1
    return kinetic_energy + gravity_energy


if __name__ == "__main__":
    test_GravityEngine_energy_euler_1_body()
    test_GravityEngine_energy_euler_2_body()
    test_GravityEngine_energy_euler_3_body()

    test_GravityEngine_energy_verlet_1_body()
    test_GravityEngine_energy_verlet_2_body()
    test_GravityEngine_energy_verlet_3_body()

    test_GravityEngine_energy_velocity_verlet_1_body()
    test_GravityEngine_energy_velocity_verlet_2_body()
    test_GravityEngine_energy_velocity_verlet_3_body()

    print("All tests completed")
    print()