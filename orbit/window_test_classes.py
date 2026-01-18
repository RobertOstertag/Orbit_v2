import pyglet
import tkinter as tk
from threading import Thread


class ControlWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.counter = 0
    
    def start(self):
        self.tick()
        self.root.mainloop()

    def tick(self):
        print("tkinter running", self.counter)
        self.counter += 1
        self.root.after(1000, self.tick)


class SimulationWindow:
    def __init__(self):
        class Window(pyglet.window.Window):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
        self.window = Window()

        self.counter = 0
    
    def start(self):
        pyglet.clock.schedule_interval(self.tick, 1)
        pyglet.app.run()
    
    def tick(self):
        print("Pyglet running", self.counter)
        self.counter += 1



if __name__ == '__main__':
    control_window = ControlWindow()
    simulation_window = SimulationWindow()

    Thread(target=control_window.start).start()
    Thread(target=simulation_window.start).start()