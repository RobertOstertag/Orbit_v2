from orbit.simulation_window import SimulationWindow

import tkinter as tk
from threading import Thread

class ControlWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.geometry("300x300")
        self.window.title("Control")

        label = tk.Label(self.window, text="Tkinter is running")
        label.pack(padx=20, pady=20)

    def start(self):
        self.window.after(16, self.tick)
        self.window.mainloop()
    
    def tick(self):
        print("Control")
