#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import threading
import time

from orbit.gravity_engine import GravityEngine
from orbit.simulation_window import SimulationWindow
from orbit.control_window import ControlWindow

def main():
    threading.Event
    shutdown_event = threading.Event()
    marked_event = threading.Event()
    preset_event = threading.Event()
    init_draw_event = threading.Event()

    #create simulation framework
    alghorithm = 3
    gravity_engine = GravityEngine(alghorithm, shutdown_event, preset_event, init_draw_event)
    simulation_window = SimulationWindow(gravity_engine, True, shutdown_event, marked_event, init_draw_event)
    control_window = ControlWindow(simulation_window, gravity_engine, shutdown_event, marked_event, preset_event)

    #start all threads
    gravity_engine.start()
    simulation_window.start()
    time.sleep(0.3) #wait some time to avoid obscure tkinter bug
    control_window.start()


if __name__ == "__main__":
    main()