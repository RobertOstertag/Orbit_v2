#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import threading
import time
import queue

from orbit.gravity_engine import GravityEngine
from orbit.simulation_window import SimulationWindow
from orbit.control_window import ControlWindow
from orbit.utils import ControlEvents


def main():
    events = ControlEvents()
    body_pos_queue = queue.Queue(1)

    #create simulation framework
    alghorithm = 3
    gravity_engine = GravityEngine(alghorithm, body_pos_queue, events)
    simulation_window = SimulationWindow(gravity_engine, True, body_pos_queue, events)
    control_window = ControlWindow(simulation_window, gravity_engine, events)

    #start all threads
    gravity_engine.start()
    simulation_window.start()
    time.sleep(0.3) #wait some time to avoid obscure tkinter bug
    control_window.start()


if __name__ == "__main__":
    main()