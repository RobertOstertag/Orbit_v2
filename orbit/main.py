#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import time

from orbit.gravity_engine import GravityEngine
from orbit.simulation_window import SimulationWindow
from orbit.control_window import ControlWindow
from orbit.utils import EventContainer, QueueContainer


def main():
    events = EventContainer()
    queues = QueueContainer()

    #create simulation framework
    alghorithm = 3
    gravity_engine = GravityEngine(alghorithm, queues, events)
    simulation_window = SimulationWindow(True, queues, events)
    control_window = ControlWindow(queues, events)

    #start all threads
    gravity_engine.start()
    simulation_window.start()
    time.sleep(0.3) #wait some time to avoid obscure tkinter bug
    control_window.start()


if __name__ == "__main__":
    main()