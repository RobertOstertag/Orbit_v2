#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from orbit.simulation_window import SimulationWindow
from orbit.control_window import ControlWindow
from orbit.gravity_engine import GravityEngine

import pyglet
from threading import Thread

class WindowHandler:
    def __init__(self, engine:GravityEngine):
        self.engine = engine
        self.simulation = SimulationWindow(engine)
        self.control = ControlWindow()

    def run(self):
        self.thread_engine = Thread(target=self.engine.update).start()
        self.thread_simulation = Thread(target=self.simulation.start).start()
        self.thread_control = Thread(target=self.control.start).start()
        