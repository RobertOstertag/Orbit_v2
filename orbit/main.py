#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import time
import random

from orbit.gravity_engine import GravityEngine
from orbit.simulation_window import SimulationWindow
from orbit.window_handler import WindowHandler

def main():
    #initialize random seed for color
    random.seed(3)

    #create simulation framework
    gravity_engine = GravityEngine(alghorithm=3)

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
    # gravity_engine.add_body(+0,             +0,             -0.93240737,    -0.8643146,     1)
    # gravity_engine.add_body(+0.97000436,    -0.24308753,    +0.93240737/2,  +0.8643146/2,   1)
    # gravity_engine.add_body(-0.97000436,    +0.24308753,    +0.93240737/2,  +0.8643146/2,   1)

    #Broucke 1
    # gravity_engine.add_body(-0.9892620043,0,   0,1.9169244185,   1)
    # gravity_engine.add_body(2.2096177241,0,    0,0.1910268738,   1)
    # gravity_engine.add_body(-1.2203557197,0,    0,-2.1079512924, 1)

    # #Broucke 2
    gravity_engine.add_body(0.336130095,0,   0,1.532431537,   1)
    gravity_engine.add_body(0.7699893804,0,  0,-0.6287350978,   1)
    gravity_engine.add_body(-1.1061194753,0, 0,-0.9036964391, 1)

    #Broucke 3
    # gravity_engine.add_body(0.0132604844,0,   0,1.05415192,   1)
    # gravity_engine.add_body(1.4157286016,0,   0,-0.2101466639,   1)
    # gravity_engine.add_body(-1.4289890859,0,  0,-0.8440052572, 1)

    #Broucke 4
    # gravity_engine.add_body(-0.5426216182,0,   0,0.8750200467,   1)
    # gravity_engine.add_body(2.5274928067,0,   0,-0.0526955841,   1)
    # gravity_engine.add_body(-1.9848711885,0,  0,-0.8223244626, 1)

    #Sheen 1
    # gravity_engine.add_body(0.486657678894505,0.75504188858351,   -0.182709864466916,0.363013287999004,   1)
    # gravity_engine.add_body(-0.681737994414464,0.29366023319721,   -0.579074922540872,-0.748157481446087,   1)
    # gravity_engine.add_body(-0.02259632746864,-0.612645601255358,  0.761784787007641,0.385144193447218, 1)

    #not working, need adaptive step size for integration
    # gravity_engine.add_body(0.335476420318203,-0.243208301824394,   1.047838171160758,0.817404215288346,   1)
    # gravity_engine.add_body(0.010021708193205,0.363104062311693,   -0.84720090780794,-0.235749148338353,   1)
    # gravity_engine.add_body(0.030978712523174,0.423035485079015,  -0.200636552532016,-0.581655492859626, 1)


    #creat simulation window for drawing, scaling, button presses, etc.
    # simulation_window = SimulationWindow(gravity_engine)

    #start simulation
    #simulation_window.simulation_start(updateLoop, gravity_engine, simulation_window)

    window_handler = WindowHandler(gravity_engine)
    window_handler.run()



# def updateLoop(dt, gravity_engine:GravityEngine, simulation_window:SimulationWindow):
#     start_time = time.time_ns()

#     #stop engine when paused
#     if (simulation_window.running == True):
#         #update forces, positions, etc or every object.
#         gravity_engine.update()

#     #update window
#     simulation_window.update(dt, start_time)
    
if __name__ == "__main__":
    main()