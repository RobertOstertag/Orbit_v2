import sys
import os
import psutil
import time

#update logging information every 60ms
REFRESH_TIME = 60.0/1000.0

class DataLogger:
    def __init__(self):
        self.timeSum = 0.0
        self.numberOfLines = 3

        self.memory   = str("Memory Usage    : ") + str(0)[:5] + str(" MByte")
        self.time     = str("Simulation Time : ") + str(0)[:5] + str(" ms")
        self.capacity = str("Capacity        : ") + str(0)[:5] + str(" %")
        self.speed    = str("Simulation Speed: ") + str(0)[:3]

        #disable the terminal cursor for better visuals
        #hide_terminal_cursor()

        #write first lines which will be overwritten later
        # if self.active == True:
        #     for i in range(self.numberOfLines):
        #         print()


    def log(self, dt, start_time, target_time, speed):
        self.timeSum += dt
        if self.timeSum >= REFRESH_TIME:
            #move curser x lines up to overwrite last lines
            #ansi_escape_sequence = str("\033[") + str(self.numberOfLines) + str("A")

            self.memory   = str("Memory Usage    : ") + str(psutil.Process().memory_info().rss / (1000 ** 2))[:5] + str(" MByte")

            duration_ms   = (time.time_ns() - start_time) / 1000000
            self.time     = str("Simulation Time : ") + str(duration_ms)[:5] + str(" ms")

            cap           = ((duration_ms / 1000) / target_time) * 100
            self.capacity = str("Capacity        : ") + str(cap)[:5] + str(" %")

            self.speed    = str("Simulation Speed: ") + str("{:.2f}".format(speed))

            self.timeSum = 0.0
        
        return self.memory + str("\n") + self.time + str("\n") + self.capacity + str("\n") + self.speed

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