#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import time
import random
from orbit.gravity_engine import GravityEngine, CelestialBody
from orbit.utils import Vector2D
from orbit.simulation_window import SimulationWindow

def main():
    #initialize random seed for color
    random.seed(3)

    #create list of bodies to show in the simulation
    body_list = [
        CelestialBody(  Vector2D(+0,  +0),  Vector2D(+0,  +0),  1000,   color_h = 0, color_s = 0), #white
        CelestialBody(  Vector2D(+85, +0),  Vector2D(+0,  +4),  1,      color_h = 0, color_s = 1), #red

        #nice visuals
        # CelestialBody(  Vector2D(+0,  +0),  Vector2D(+0,  +0),  1000,   color_h = 1, color_s = 0),
        # CelestialBody(  Vector2D(+50, +0),  Vector2D(+0,  +5),  1,      color_h = 0),
        # CelestialBody(  Vector2D(-50, +0),  Vector2D(+0,  -5),  1,      color_h = 55),
        # CelestialBody(  Vector2D(-70, +0),    Vector2D(+0,  -4),    1,      color_h = 105),
        # CelestialBody(  Vector2D(-40, +0),    Vector2D(+0,  -6.5),  1,      color_h = 180),
        # CelestialBody(  Vector2D(+60, +60),   Vector2D(-2,  +2),    1,      color_h = 265),
        # CelestialBody(  Vector2D(-80, -80),   Vector2D(+5,  -4),    1,      color_h = 285),
        # CelestialBody(  Vector2D(-30, +0),    Vector2D(+0,  +7.0),  1,      color_h = 325),
    ]

    #create celestial bodies and the simulation framework
    gravity_engine = GravityEngine(body_list, alghorithm = 2)

    #creat simulation handler for window drawing, scaling, button presses, etc.
    simulation_window = SimulationWindow(gravity_engine)

    #start simulation
    simulation_window.simulation_start(updateLoop, gravity_engine)

def updateLoop(dt, gravity_engine:GravityEngine, simulation_window:SimulationWindow):
    start_time = time.time_ns()

    #stop engine when paused
    if (simulation_window.running == True):
        #update forces, positions, etc or every object.
        gravity_engine.update()

    #update window
    simulation_window.update(gravity_engine.body_list, dt, start_time)
    
if __name__ == "__main__":
    main()