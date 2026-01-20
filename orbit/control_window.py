#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from orbit.simulation_window import SimulationWindow
import orbit.gravity_engine

import tkinter as tk
import threading

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400

class ControlWindow(threading.Thread):
    def __init__(self, shutdown_event:threading.Event, sim_window:SimulationWindow):
        super().__init__()
        self.shutdown_event = shutdown_event
        self.sim_window = sim_window

    def run(self):
        #create window
        self.window = tk.Tk()
        self.window.title("Orbit Control")
        self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.window.resizable(False, False)
        #define function to be called when window is closed
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        #create button
        self.button = tk.Button(self.window, text="Button", command=self.button_pressed)
        self.button.pack()

        self.tick()
        self.window.mainloop()

    def tick(self):
        #set window left of simulation window location
        self.window.geometry(f"{WINDOW_WIDTH}x{self.sim_window.height}+{self.sim_window.pos_x-WINDOW_WIDTH-10}+{self.sim_window.pos_y - 30}")

        #check if other window was closed and if so, close myself
        if self.shutdown_event.is_set():
            self.stop()
            return

        #call function again after delay
        self.window.after(int(orbit.gravity_engine.UPDATE_RATE* 1000), self.tick)

    def button_pressed(self):
        print("Button is pressed")

    def on_close(self):
        #notify other thread that this window is closed
        self.shutdown_event.set()
        self.stop()

    def stop(self):
        self.window.quit()