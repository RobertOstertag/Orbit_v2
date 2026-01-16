#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import time
import random
from orbit.gravity_engine import GravityEngine
from orbit.simulation_window import SimulationWindow

def main():
    #initialize random seed for color
    random.seed(3)

    #create simulation framework
    gravity_engine = GravityEngine(alghorithm = 3)

    #add bodies to simulation
    #                       pos_x           pos_y           vel_x           vel_y           mass

    # gravity_engine.add_body(+0,             +0,             +0,             +0,             1000)
    # gravity_engine.add_body(+85,            +0,             +0,             +4,             1)

    #nice visuals
    # gravity_engine.add_body(+0,             +0,             +0,             +0,             1000)
    # gravity_engine.add_body(+50,            +0,             +0,             +5,             1)
    # gravity_engine.add_body(-50,            +0,             +0,             -5,             1)
    # gravity_engine.add_body(-180,           +0,             +0,             -1.5,           1)
    # gravity_engine.add_body(-40,            +0,             +0,             -6.5,           1)
    # gravity_engine.add_body(+60,            +60,            -2,             +2,             1)
    # gravity_engine.add_body(-80,            -80,            +2.5,           -3,             1)

    #Figure 8
    gravity_engine.add_body(+0,             +0,             -0.93240737,    -0.8643146,     1)
    gravity_engine.add_body(+0.97000436,    -0.24308753,    +0.93240737/2,  +0.8643146/2,   1)
    gravity_engine.add_body(-0.97000436,    +0.24308753,    +0.93240737/2,  +0.8643146/2,   1)

    #creat simulation handler for window drawing, scaling, button presses, etc.
    simulation_window = SimulationWindow(gravity_engine)

    #start simulation
    simulation_window.simulation_start(updateLoop, gravity_engine, simulation_window)

def updateLoop(dt, gravity_engine:GravityEngine, simulation_window:SimulationWindow):
    start_time = time.time_ns()

    #stop engine when paused
    if (simulation_window.running == True):
        #update forces, positions, etc or every object.
        gravity_engine.update()

    #update window
    simulation_window.update(dt, start_time)
    
if __name__ == "__main__":
    main()