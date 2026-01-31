#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from orbit.utils import Interface, UserInputData, CelestialBody, Vector2D
import orbit.gravity_engine
import orbit.presets

import tkinter as tk
import threading
import copy
import math
import random

WINDOW_WIDTH = 350
WINDOW_HEIGHT = 800
WINDOW_POS_X = 150
WINDOW_POS_Y = 200

class ControlWindow(threading.Thread):
    def __init__(self, interface:Interface):
        super().__init__()
        self.interface = interface

    def run(self):
        #create window
        self.window = tk.Tk()
        self.window.title("Orbit Control")
        self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{WINDOW_POS_X}+{WINDOW_POS_Y}")
        self.window.resizable(False, False)
        #define function to be called when window is closed
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.font = ("Arial", 15)

        self.marked_body = CelestialBody(Vector2D(0, 0), Vector2D(0, 0), 0, 0, 0, 0, 0)
        self.user_input = UserInputData()

        self.create_labels()

        self.update()
        self.window.mainloop()

    def update(self):
        self.update_body_information()

        #check if other window was closed and if so, close myself
        if self.interface.events.stop.is_set():
            self.stop()
            return
        
        #call function again after delay
        self.window.after(int(orbit.gravity_engine.UPDATE_RATE * 1000), self.update)

    def create_labels(self):
        #main frame container
        self.body_frame = tk.Frame(self.window)
        self.body_frame.grid(pady=20)
        vcmd = (self.window.register(self.validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

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
        self.entry_body_index = tk.Entry(self.body_frame, validate ='key', validatecommand=vcmd, font=self.font, width=7, justify='center')
        self.entry_body_index.grid(row=row, column=1, padx=10, pady=(30, 0))

        # ======================
        # Mass
        # ======================
        row += 1
        tk.Label(self.body_frame, text="Mass", font=self.font, width=10).grid(row=row, column=0, padx=0, pady=(15, 0))
        self.entry_body_mass = tk.Entry(self.body_frame, validate ='key', validatecommand=vcmd, font=self.font, width=7, justify='center')
        self.entry_body_mass.grid(row=row, column=1, padx=10, pady=(15, 0))
        self.set_entry_text(self.entry_body_mass, 0)

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
        self.entry_body_pos_x = tk.Entry(self.body_frame, validate ='key', validatecommand=vcmd, font=self.font, width=entry_width, justify="center")
        self.entry_body_pos_x.grid(row=row, column=1, padx=0, pady=(0, 0))
        self.set_entry_text(self.entry_body_pos_x, 0)
        self.entry_body_pos_y = tk.Entry(self.body_frame, validate ='key', validatecommand=vcmd, font=self.font, width=entry_width, justify="center")
        self.entry_body_pos_y.grid(row=row, column=2, padx=0, pady=(0, 0))
        self.set_entry_text(self.entry_body_pos_y, 0)

        # ======================
        # Velocity
        # ======================
        row += 1
        tk.Label(self.body_frame, text="Velocity", font=self.font, width=10).grid(row=row, column=0, padx=0, pady=(5, 0))
        self.entry_body_vel_x = tk.Entry(self.body_frame, validate ='key', validatecommand=vcmd, font=self.font, width=entry_width, justify="center")
        self.entry_body_vel_x.grid(row=row, column=1, padx=0, pady=(5, 0))
        self.set_entry_text(self.entry_body_vel_x, 0)
        self.entry_body_vel_y = tk.Entry(self.body_frame, validate ='key', validatecommand=vcmd, font=self.font, width=entry_width, justify="center")
        self.entry_body_vel_y.grid(row=row, column=2, padx=0, pady=(5, 0))
        self.set_entry_text(self.entry_body_vel_y, 0)

        #Buttons for updaing, adding and deleting
        row += 1
        self.button_update_body = tk.Button(self.body_frame, text="Update", command=self.button_upd_body_func, width=20, height=2, font=self.font)
        self.button_update_body.grid(row=row, column=0, columnspan=3, padx=0, pady=(10, 0))
        row += 1
        self.button_add_body = tk.Button(self.body_frame, text="Add", command=self.button_add_body_func, width=20, height=2, font=self.font)
        self.button_add_body.grid(row=row, column=0, columnspan=3, padx=0, pady=(10, 0))
        self.cb_random_state = tk.IntVar(value=1)
        self.checkbox_random = tk.Checkbutton(self.body_frame, text="Rand", variable=self.cb_random_state)
        self.checkbox_random.grid(row=row, column=2, padx=(60, 0), pady=(10, 0))
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
        #get newest body information and which body is marked
        bodies = self.interface.bodies.receive()
        marked_body_index = self.interface.marked_body_index.receive()

        if ((bodies != None) and
            (marked_body_index < len(bodies))):
            new_marked_body = bodies[marked_body_index]
            #check if current marked body has differnet contents as last marked body
            if not (self.marked_body == new_marked_body):
                self.marked_body = copy.deepcopy(new_marked_body)
                rounding = 4
                #only update fields that changed
                if self.entry_body_index.get() != str(marked_body_index):
                    self.set_entry_text(self.entry_body_index, str(marked_body_index))
                if self.entry_body_mass.get() != str(round(self.marked_body.mass, rounding)):
                    self.set_entry_text(self.entry_body_mass, str(round(self.marked_body.mass, rounding)))
                if self.entry_body_pos_x.get() != str(round(self.marked_body.pos.x, rounding)):
                    self.set_entry_text(self.entry_body_pos_x, str(round(self.marked_body.pos.x, rounding)))
                if self.entry_body_pos_y.get() != str(round(self.marked_body.pos.y, rounding)):
                    self.set_entry_text(self.entry_body_pos_y, str(round(self.marked_body.pos.y, rounding)))
                if self.entry_body_vel_x.get() != str(round(self.marked_body.vel.x, rounding)):
                    self.set_entry_text(self.entry_body_vel_x, str(round(self.marked_body.vel.x, rounding)))
                if self.entry_body_vel_y.get() != str(round(self.marked_body.vel.y, rounding)):
                    self.set_entry_text(self.entry_body_vel_y, str(round(self.marked_body.vel.y, rounding)))

    def send_user_input(self):
        if self.entry_body_index.get() != "":
            self.user_input.index = self.get_int(self.entry_body_index.get(), self.user_input.index)

        if self.cb_random_state.get() == False:
            if self.entry_body_mass.get() != "":
                self.user_input.mass = self.get_float(self.entry_body_mass.get(), self.user_input.mass)
            if self.entry_body_pos_x.get() != "":
                self.user_input.pos.x = self.get_float(self.entry_body_pos_x.get(), self.user_input.pos.x)
            if self.entry_body_pos_y.get() != "":
                self.user_input.pos.y = self.get_float(self.entry_body_pos_y.get(), self.user_input.pos.y)
            if self.entry_body_vel_x.get() != "":
                self.user_input.vel.x = self.get_float(self.entry_body_vel_x.get(), self.user_input.vel.x)
            if self.entry_body_vel_y.get() != "":
                self.user_input.vel.y = self.get_float(self.entry_body_vel_y.get(), self.user_input.vel.y)
        else:
            self.user_input.mass = random.random() * 10
            self.user_input.pos.x = (random.random() * 20) - 10
            self.user_input.pos.y = (random.random() * 20) - 10
            self.user_input.vel.x = (random.random() * 20) - 10
            self.user_input.vel.y = (random.random() * 20) - 10

        self.interface.user_input.send(self.user_input)

    def button_upd_body_func(self):
        self.send_user_input()
        self.interface.events.update_body.set()

    def button_add_body_func(self):
        self.send_user_input()
        self.interface.events.add_body.set()

    def button_del_body_func(self):
        self.send_user_input()
        self.interface.events.delete_body.set()

    def button_load_preset_func(self):
        self.interface.selected_preset.send(self.selected_preset.get())
        self.interface.events.load_preset.set()

    def set_entry_text(self, entry:tk.Entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, text)

    def on_close(self):
        #notify other thread that this window is closed
        self.interface.events.stop.set()
        self.stop()

    def stop(self):
        self.window.quit()

    def validate(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
        if value_if_allowed:
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            #allow empty strings
            return True

    def get_float(self, string, fallback):
        if string != "":
            return float(string)
        else:
            return fallback
        
    def get_int(self, string, fallback):
        if string != "":
            return math.floor(float(string))
        else:
            return fallback
