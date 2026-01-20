import sys
import os
import psutil
import time

import orbit.gravity_engine

#update logging information every 60ms
REFRESH_TIME = 60.0/1000.0

class DataLogger:
    def __init__(self):
        self.timeSum = 0.0
        self.memory    = str("Memory Usage    : ") + str(0)[:5] + str(" MByte")
        self.sim_time  = str("Simulation Time : ") + str(0)[:5] + str(" ms")
        self.sim_cap   = str("Simulation Cap. : ") + str(0)[:5] + str(" %")
        self.draw_time = str("Drawing Time    : ") + str(0)[:5] + str(" ms")
        self.draw_cap  = str("Drawing Capacity: ") + str(0)[:5] + str(" %")
        self.speed     = str("Simulation Speed: ") + str(0)[:3]

    def log(self, time_since_last_call, sim_time, draw_time, speed):
        self.timeSum += time_since_last_call
        #only update log sometimes so that the values can be read easily
        if self.timeSum >= REFRESH_TIME:
            self.memory    = str("Memory Usage    : ") + str(psutil.Process().memory_info().rss / (1000 ** 2))[:5] + str(" MByte")

            self.sim_time  = str("Simulation Time : ") + str(sim_time*1000)[:5] + str(" ms")
            sim_capacity   = (sim_time / orbit.gravity_engine.UPDATE_RATE) * 100
            self.sim_cap   = str("Simulation Cap. : ") + str(sim_capacity)[:5] + str(" %")

            self.draw_time = str("Drawing Time    : ") + str(draw_time*1000)[:5] + str(" ms")
            draw_capacity  = (draw_time / orbit.gravity_engine.UPDATE_RATE) * 100
            self.draw_cap  = str("Drawing Capacity: ") + str(draw_capacity)[:5] + str(" %")

            self.speed     = str("Simulation Speed: ") + str("{:.2f}".format(speed))
            self.timeSum   = 0.0
        return self.memory + str("\n") + self.sim_time + str("\n") + self.sim_cap + str("\n") + self.draw_time + str("\n") + self.draw_cap + str("\n") + self.speed

def hide_terminal_cursor():
    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = False
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

def show_terminal_cursor():
    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = True
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

if os.name == 'nt':
    import msvcrt
    import ctypes

    class _CursorInfo(ctypes.Structure):
        _fields_ = [("size", ctypes.c_int),
                    ("visible", ctypes.c_byte)]
        


#move curser x lines up to overwrite last lines
#ansi_escape_sequence = str("\033[") + str(self.numberOfLines) + str("A")