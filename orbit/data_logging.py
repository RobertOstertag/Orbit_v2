import sys
import os
import psutil
import time

import orbit.gravity_engine

#update logging information every 60ms
REFRESH_TIME = 200.0/1000.0

class DataLogger:
    def __init__(self):
        self.accumalator = 0
        self.now = time.perf_counter()
        self.last = time.perf_counter()

        self.memory          = str("Memory Usage    : ") + str(0)[:5] + str(" MByte")
        self.engine_duration = str("Simulation Time : ") + str(0)[:4] + str(" ms (") + str(0)[:4] + str(" %)")
        self.draw_duration   = str("Drawing Time    : ") + str(0)[:4] + str(" ms (") + str(0)[:4] + str(" %)")
        self.engine_timestep = str("Simulation Speed: ") + str(0)[:3]

    def get_string(self, engine_duration, draw_duration, engine_timestep):
        self.now = time.perf_counter()

        self.accumalator += self.now - self.last
        self.last = self.now
        #only update log sometimes so that the values can be read easily
        if self.accumalator >= REFRESH_TIME:
            self.accumalator = 0

            engine_capacity   = (engine_duration / orbit.gravity_engine.UPDATE_RATE) * 100
            draw_capacity  = (draw_duration / orbit.gravity_engine.UPDATE_RATE) * 100

            self.memory          = str("Memory Usage    : ") + str(psutil.Process().memory_info().rss / (1000 ** 2))[:5] + str(" MByte")
            self.engine_duration = str("Simulation Time : ") + str(engine_duration*1000)[:4] + str(" ms (") + str(engine_capacity)[:4] + str(" %)")
            self.draw_duration   = str("Drawing Time    : ") + str(draw_duration*1000)[:4] + str(" ms (") + str(draw_capacity)[:4] + str(" %)")
            self.engine_timestep = str("Simulation Speed: ") + str("{:.2f}".format(engine_timestep))

        return self.memory + str("\n") + self.engine_duration + str("\n") + self.draw_duration + str("\n") + self.engine_timestep

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