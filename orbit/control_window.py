#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from orbit.gravity_engine import GravityEngine
from orbit.simulation_window import SimulationWindow
import orbit.gravity_engine
import orbit.presets

import tkinter as tk
import threading

WINDOW_WIDTH = 350
WINDOW_HEIGHT = 400

class ControlWindow(threading.Thread):
    def __init__(self, sim_window:SimulationWindow, engine:GravityEngine, shutdown_event:threading.Event, marked_event:threading.Event, preset_event:threading.Event):
        super().__init__()
        self.sim_window = sim_window
        self.engine = engine
        self.shutdown_event = shutdown_event
        self.marked_event = marked_event
        self.preset_event = preset_event

    def run(self):
        #create window
        self.window = tk.Tk()
        self.window.title("Orbit Control")
        #self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.window.geometry(f"{WINDOW_WIDTH}x{self.sim_window.height}+{self.sim_window.pos_x-WINDOW_WIDTH-10}+{self.sim_window.pos_y - 30}")
        self.window.resizable(False, False)
        #define function to be called when window is closed
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.font = ("Arial", 15)

        #main frame container
        self.body_frame = tk.Frame(self.window)
        self.body_frame.grid(pady=20)

        # ======================
        # Header
        # ======================
        row = 0
        tk.Label(self.body_frame, text="Celestial Body Information", font=("Arial", 20)).grid(row=row, column=0, columnspan=3, padx=0, pady=(10, 0))

        # ======================
        # Index
        # ======================
        row += 1
        tk.Label(self.body_frame, text="Index", font=self.font, width=10).grid(row=row, column=0, padx=0, pady=(30, 0))
        self.entry_body_index = tk.Entry(self.body_frame, font=self.font, width=7, justify='center')
        self.entry_body_index.grid(row=row, column=1, padx=10, pady=(30, 0))

        # ======================
        # Mass
        # ======================
        row += 1
        tk.Label(self.body_frame, text="Mass", font=self.font, width=10).grid(row=row, column=0, padx=0, pady=(15, 0))
        self.entry_body_mass = tk.Entry(self.body_frame, font=self.font, width=7, justify='center')
        self.entry_body_mass.grid(row=row, column=1, padx=10, pady=(15, 0))

        # ======================
        # Coordinates header
        # ======================
        row += 1
        tk.Label(self.body_frame, text=" ", width=10, font=self.font).grid(row=row, column=0, padx=0, pady=(20, 0))
        tk.Label(self.body_frame, text="X", width=10, font=self.font).grid(row=row, column=1, padx=0, pady=(20, 0))
        tk.Label(self.body_frame, text="Y", width=10, font=self.font).grid(row=row, column=2, padx=0, pady=(20, 0))

        # ======================
        # Position
        # ======================
        row += 1
        entry_width = 9
        tk.Label(self.body_frame, text="Position", font=self.font, width=10).grid(row=row, column=0, padx=0, pady=(0, 0))
        self.entry_body_pos_x = tk.Entry(self.body_frame, font=self.font, width=entry_width, justify="center")
        self.entry_body_pos_x.grid(row=row, column=1, padx=0, pady=(0, 0))
        self.entry_body_pos_x.insert(0, "0")
        self.entry_body_pos_y = tk.Entry(self.body_frame, font=self.font, width=entry_width, justify="center")
        self.entry_body_pos_y.grid(row=row, column=2, padx=0, pady=(0, 0))
        self.entry_body_pos_y.insert(0, "0")

        # ======================
        # Velocity
        # ======================
        row += 1
        tk.Label(self.body_frame, text="Velocity", font=self.font, width=10).grid(row=row, column=0, padx=0, pady=(5, 0))
        self.entry_body_vel_x = tk.Entry(self.body_frame, font=self.font, width=entry_width, justify="center")
        self.entry_body_vel_x.grid(row=row, column=1, padx=0, pady=(5, 0))
        self.entry_body_vel_x.insert(0, "0")
        self.entry_body_vel_y = tk.Entry(self.body_frame, font=self.font, width=entry_width, justify="center")
        self.entry_body_vel_y.grid(row=row, column=2, padx=0, pady=(5, 0))
        self.entry_body_vel_y.insert(0, "0")

        #Buttons for updaing, adding and deleting
        row += 1
        self.button_update_body = tk.Button(self.body_frame, text="Update", command=self.button_upd_body_func, width=20, height=2, font=self.font)
        self.button_update_body.grid(row=row, column=0, columnspan=3, padx=0, pady=(10, 0))
        row += 1
        self.button_add_body = tk.Button(self.body_frame, text="Add", command=self.button_add_body_func, width=20, height=2, font=self.font)
        self.button_add_body.grid(row=row, column=0, columnspan=3, padx=0, pady=(10, 0))
        row += 1
        self.button_delete_body = tk.Button(self.body_frame, text="Delete", command=self.button_del_body_func, width=20, height=2, font=self.font)
        self.button_delete_body.grid(row=row, column=0, columnspan=3, padx=0, pady=(10, 0))

        #Dropdown menu
        row += 1
        tk.Label(self.body_frame, text="Presets", font=self.font, width=10).grid(row=row, column=0, padx=0, pady=(30, 0))
        self.presets = orbit.presets.PRESETS
        self.selected_preset = tk.StringVar(value=self.presets[0])
        self.menu_presets = tk.OptionMenu(self.body_frame, self.selected_preset, *self.presets)
        self.menu_presets.config(width=13, height=1, font=self.font)
        self.menu_presets.grid(row=row, column=1, columnspan=2, padx=0, pady=(30, 0))
        menu = self.window.nametowidget(self.menu_presets.menuname)
        menu.config(font=self.font)
        row += 1
        self.button_load_preset = tk.Button(self.body_frame, text="Load Preset", command=self.button_load_preset_func, width=20, height=2, font=self.font)
        self.button_load_preset.grid(row=row, column=0, columnspan=3, padx=0, pady=(5, 0))

        self.update()
        self.window.mainloop()

    def update(self):
        #set window left of simulation window location
        self.window.geometry(f"{WINDOW_WIDTH}x{self.sim_window.height}+{self.sim_window.pos_x-WINDOW_WIDTH-10}+{self.sim_window.pos_y - 30}")

        if self.marked_event.is_set():
            self.marked_event.clear()
            self.update_body_information()
        if self.engine.running == True:
            self.update_body_information()


        #check if other window was closed and if so, close myself
        if self.shutdown_event.is_set():
            self.stop()
            return
        #call function again after delay
        self.window.after(int(orbit.gravity_engine.UPDATE_RATE* 1000), self.update)

    def update_body_information(self):
        self.set_entry_text(self.entry_body_index, str(self.sim_window.marked_body))
        if self.sim_window.marked_body != None:
            mass, pos_x, pos_y, vel_x, vel_y = self.engine.get_body_information(self.sim_window.marked_body)
        else:
            mass, pos_x, pos_y, vel_x, vel_y = 0, 0, 0, 0, 0
        rounding = 6
        self.set_entry_text(self.entry_body_mass, str(round(mass, rounding)))
        self.set_entry_text(self.entry_body_pos_x, str(round(pos_x, rounding)))
        self.set_entry_text(self.entry_body_pos_y, str(round(pos_y, rounding)))
        self.set_entry_text(self.entry_body_vel_x, str(round(vel_x, rounding)))
        self.set_entry_text(self.entry_body_vel_y, str(round(vel_y, rounding)))

    def button_upd_body_func(self):
        print("Updating Body")

    def button_add_body_func(self):
        print("Adding Body")

    def button_del_body_func(self):
        print("Deleting Body")

    def button_load_preset_func(self):
        self.preset_event.set()
        self.engine.set_preset(self.selected_preset.get())

    def set_entry_text(self, entry:tk.Entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, text)

    def on_close(self):
        #notify other thread that this window is closed
        self.shutdown_event.set()
        self.stop()

    def stop(self):
        self.window.quit()