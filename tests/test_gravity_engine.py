#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from orbit.gravity_engine import GravityEngine
from orbit.utils import QueueContainer, EventContainer

import time

NUMBER_OF_ITERATIONS = 10000
ACCEPTABLE_ERROR = 2/1000

def test_GravityEngine_energy_euler_1_body():
    print("Energy test for 1 body with Euler Method after", NUMBER_OF_ITERATIONS, "Iterations:")
    gravity_engine = GravityEngine(alghorithm=0, queues=QueueContainer(), events=EventContainer())
    gravity_engine.events.load_preset.clear() #dont load predefined preset
    gravity_engine.add_body(+0, +0, +1, +3, 1000)
    gravity_engine.change_dt(0.5)
    simulate_bodies(gravity_engine, ACCEPTABLE_ERROR)

def test_GravityEngine_energy_euler_2_body():
    print("Energy test for 2 bodies with Euler Method after", NUMBER_OF_ITERATIONS, "Iterations:")
    gravity_engine = GravityEngine(alghorithm=0, queues=QueueContainer(), events=EventContainer())
    gravity_engine.events.load_preset.clear() #dont load predefined preset
    gravity_engine.add_body(+0, +0, +0, +0, 1000)
    gravity_engine.add_body(+85, +0, +0, +4, 1)
    gravity_engine.change_dt(0.5)
    simulate_bodies(gravity_engine, ACCEPTABLE_ERROR)

def test_GravityEngine_energy_euler_3_body():
    print("Energy test for 3 bodies with Euler Method after", NUMBER_OF_ITERATIONS, "Iterations:")
    gravity_engine = GravityEngine(alghorithm=0, queues=QueueContainer(), events=EventContainer())
    gravity_engine.events.load_preset.clear() #dont load predefined preset
    gravity_engine.add_body(+0, +0, +0, +0, 1000)
    gravity_engine.add_body(+50, +0, +0, +5, 1)
    gravity_engine.add_body(-50, +0, +0, -5, 1)
    gravity_engine.change_dt(0.1)
    simulate_bodies(gravity_engine, ACCEPTABLE_ERROR)



def test_GravityEngine_energy_verlet_1_body():
    print("Energy test for 1 body with Verlet Method after", NUMBER_OF_ITERATIONS, "Iterations:")
    gravity_engine = GravityEngine(alghorithm=1, queues=QueueContainer(), events=EventContainer())
    gravity_engine.events.load_preset.clear() #dont load predefined preset
    gravity_engine.add_body(+0, +0, +1, +3, 1000)
    gravity_engine.change_dt(0.5)
    simulate_bodies(gravity_engine, ACCEPTABLE_ERROR)

def test_GravityEngine_energy_verlet_2_body():
    print("Energy test for 2 bodies with Verlet Method after", NUMBER_OF_ITERATIONS, "Iterations:")
    gravity_engine = GravityEngine(alghorithm=1, queues=QueueContainer(), events=EventContainer())
    gravity_engine.events.load_preset.clear() #dont load predefined preset
    gravity_engine.add_body(+0, +0, +0, +0, 1000)
    gravity_engine.add_body(+85, +0, +0, +4, 1)
    gravity_engine.change_dt(0.5)
    simulate_bodies(gravity_engine, ACCEPTABLE_ERROR)

def test_GravityEngine_energy_verlet_3_body():
    print("Energy test for 3 bodies with Verlet Method after", NUMBER_OF_ITERATIONS, "Iterations:")
    gravity_engine = GravityEngine(alghorithm=1, queues=QueueContainer(), events=EventContainer())
    gravity_engine.events.load_preset.clear() #dont load predefined preset
    gravity_engine.add_body(+0, +0, +0, +0, 1000)
    gravity_engine.add_body(+50, +0, +0, +5, 1)
    gravity_engine.add_body(-50, +0, +0, -5, 1)
    gravity_engine.change_dt(0.1)
    simulate_bodies(gravity_engine, ACCEPTABLE_ERROR)



def test_GravityEngine_energy_velocity_verlet_1_body():
    print("Energy test for 1 body with Velocity Verlet Method after", NUMBER_OF_ITERATIONS, "Iterations:")
    gravity_engine = GravityEngine(alghorithm=2, queues=QueueContainer(), events=EventContainer())
    gravity_engine.events.load_preset.clear() #dont load predefined preset
    gravity_engine.add_body(+0, +0, +1, +3, 1000)
    gravity_engine.change_dt(0.5)
    simulate_bodies(gravity_engine, ACCEPTABLE_ERROR)

def test_GravityEngine_energy_velocity_verlet_2_body():
    print("Energy test for 2 bodies with Velocity Verlet Method after", NUMBER_OF_ITERATIONS, "Iterations:")
    gravity_engine = GravityEngine(alghorithm=2, queues=QueueContainer(), events=EventContainer())
    gravity_engine.events.load_preset.clear() #dont load predefined preset
    gravity_engine.add_body(+0, +0, +0, +0, 1000)
    gravity_engine.add_body(+85, +0, +0, +4, 1)
    gravity_engine.change_dt(0.5)
    simulate_bodies(gravity_engine, ACCEPTABLE_ERROR)

def test_GravityEngine_energy_velocity_verlet_3_body():
    print("Energy test for 3 bodies with Velocity Verlet Method after", NUMBER_OF_ITERATIONS, "Iterations:")
    gravity_engine = GravityEngine(alghorithm=2, queues=QueueContainer(), events=EventContainer())
    gravity_engine.events.load_preset.clear() #dont load predefined preset
    gravity_engine.add_body(+0, +0, +0, +0, 1000)
    gravity_engine.add_body(+50, +0, +0, +5, 1)
    gravity_engine.add_body(-50, +0, +0, -5, 1)
    gravity_engine.change_dt(0.1)
    simulate_bodies(gravity_engine, ACCEPTABLE_ERROR)



def test_GravityEngine_energy_rk4_1_body():
    print("Energy test for 1 body with RK4 Method after", NUMBER_OF_ITERATIONS, "Iterations:")
    gravity_engine = GravityEngine(alghorithm=3, queues=QueueContainer(), events=EventContainer())
    gravity_engine.events.load_preset.clear() #dont load predefined preset
    gravity_engine.add_body(+0, +0, +1, +3, 1000)
    gravity_engine.change_dt(0.5)
    simulate_bodies(gravity_engine, ACCEPTABLE_ERROR)

def test_GravityEngine_energy_rk4_2_body():
    print("Energy test for 2 bodies with RK4 Method after", NUMBER_OF_ITERATIONS, "Iterations:")
    gravity_engine = GravityEngine(alghorithm=3, queues=QueueContainer(), events=EventContainer())
    gravity_engine.events.load_preset.clear() #dont load predefined preset
    gravity_engine.add_body(+0, +0, +0, +0, 1000)
    gravity_engine.add_body(+85, +0, +0, +4, 1)
    gravity_engine.change_dt(0.5)
    simulate_bodies(gravity_engine, ACCEPTABLE_ERROR)

def test_GravityEngine_energy_rk4_3_body():
    print("Energy test for 3 bodies with RK4 Method after", NUMBER_OF_ITERATIONS, "Iterations:")
    gravity_engine = GravityEngine(alghorithm=3, queues=QueueContainer(), events=EventContainer())
    gravity_engine.events.load_preset.clear() #dont load predefined preset
    gravity_engine.add_body(+0, +0, +0, +0, 1000)
    gravity_engine.add_body(+50, +0, +0, +5, 1)
    gravity_engine.add_body(-50, +0, +0, -5, 1)
    gravity_engine.change_dt(0.1)
    simulate_bodies(gravity_engine, ACCEPTABLE_ERROR)



def simulate_bodies(engine:GravityEngine, target_error):

    #initial energy of system
    initial_energy = engine.get_system_energy(engine.body_list)

    start_time = time.time_ns()
    #do many iterations of simulation steps
    for iter in range(NUMBER_OF_ITERATIONS):
        engine.update()
    duration = time.time_ns() - start_time

    final_energy = engine.get_system_energy(engine.body_list)
    energy_error = (initial_energy - final_energy) / initial_energy
    print("Energy Error:", round(energy_error * 100, 5), "%")
    print("Calculation Time:", duration/1000000, "ms")
    print()
    assert (energy_error < target_error)

if __name__ == "__main__":
    print()

    test_GravityEngine_energy_euler_1_body()
    test_GravityEngine_energy_euler_2_body()
    test_GravityEngine_energy_euler_3_body()

    test_GravityEngine_energy_verlet_1_body()
    test_GravityEngine_energy_verlet_2_body()
    test_GravityEngine_energy_verlet_3_body()

    test_GravityEngine_energy_velocity_verlet_1_body()
    test_GravityEngine_energy_velocity_verlet_2_body()
    test_GravityEngine_energy_velocity_verlet_3_body()

    test_GravityEngine_energy_rk4_1_body()
    test_GravityEngine_energy_rk4_2_body()
    test_GravityEngine_energy_rk4_3_body()

    print("All tests completed")
    print()