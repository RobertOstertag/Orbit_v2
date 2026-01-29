#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from orbit.simulation_window import SimulationWindow
from orbit.utils import EventContainer, QueueContainer
import orbit.gravity_engine
import orbit.presets

import tkinter as tk
import threading
import queue

WINDOW_WIDTH = 350
WINDOW_HEIGHT = 800
WINDOW_POS_X = 150
WINDOW_POS_Y = 200

class ControlWindow(threading.Thread):
    def __init__(self, queues:QueueContainer, events:EventContainer):
        super().__init__()
        self.queues = queues
        self.events = events

    def run(self):
        #create window
        self.window = tk.Tk()
        self.window.title("Orbit Control")
        self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{WINDOW_POS_X}+{WINDOW_POS_Y}")
        self.window.resizable(False, False)
        #define function to be called when window is closed
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.font = ("Arial", 15)

        self.create_labels()

        self.update()
        self.window.mainloop()

    def update(self):
        #timestep = self.queues.timestep.receive(timestep)

        self.update_body_information()

        #check if other window was closed and if so, close myself
        if self.events.stop.is_set():
            self.stop()
            return
        
        #call function again after delay
        self.window.after(int(orbit.gravity_engine.UPDATE_RATE * 1000), self.update)

    def create_labels(self):
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
        self.selected_preset = tk.StringVar(value=orbit.presets.PRESETS[2])
        self.menu_presets = tk.OptionMenu(self.body_frame, self.selected_preset, *orbit.presets.PRESETS)
        self.menu_presets.config(width=13, height=1, font=self.font)
        self.menu_presets.grid(row=row, column=1, columnspan=2, padx=0, pady=(30, 0))
        menu = self.window.nametowidget(self.menu_presets.menuname)
        menu.config(font=self.font)
        row += 1
        self.button_load_preset = tk.Button(self.body_frame, text="Load Preset", command=self.button_load_preset_func, width=20, height=2, font=self.font)
        self.button_load_preset.grid(row=row, column=0, columnspan=3, padx=0, pady=(5, 0))

    def update_body_information(self):
        marked_body_data = self.queues.marked_body.receive([0, 0, 0, 0, 0, 0])
        rounding = 4
        if self.entry_body_index.get() != str(marked_body_data[0]):
            self.set_entry_text(self.entry_body_index, str(marked_body_data[0]))
        if self.entry_body_mass.get() != str(round(marked_body_data[1], rounding)):
            self.set_entry_text(self.entry_body_mass, str(round(marked_body_data[1], rounding)))
        if self.entry_body_pos_x.get() != str(round(marked_body_data[2], rounding)):
            self.set_entry_text(self.entry_body_pos_x, str(round(marked_body_data[2], rounding)))
        if self.entry_body_pos_y.get() != str(round(marked_body_data[3], rounding)):
            self.set_entry_text(self.entry_body_pos_y, str(round(marked_body_data[3], rounding)))
        if self.entry_body_vel_x.get() != str(round(marked_body_data[4], rounding)):
            self.set_entry_text(self.entry_body_vel_x, str(round(marked_body_data[4], rounding)))
        if self.entry_body_vel_y.get() != str(round(marked_body_data[5], rounding)):
            self.set_entry_text(self.entry_body_vel_y, str(round(marked_body_data[5], rounding)))

    def button_upd_body_func(self):
        print("Updating Body")

    def button_add_body_func(self):
        print("Adding Body")

    def button_del_body_func(self):
        print("Deleting Body")

    def button_load_preset_func(self):
        self.queues.selected_preset.send(self.selected_preset.get())
        self.events.load_preset.set()

    def set_entry_text(self, entry:tk.Entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, text)

    def on_close(self):
        #notify other thread that this window is closed
        self.events.stop.set()
        self.stop()

    def stop(self):
        self.window.quit()