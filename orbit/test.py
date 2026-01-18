import pyglet
import tkinter as tk
from threading import Thread, Barrier

global tk_counter
tk_counter = 0
global pyglet_counter
pyglet_counter = 0

global barrier
barrier = Barrier(2)

def run1():
    root = tk.Tk()

    tkinter_tick(root)
    root.mainloop()

def tkinter_tick(root):
    global tk_counter
    print("tkinter running", tk_counter)
    tk_counter += 1

    global barrier
    barrier.wait()
    root.after(500, tkinter_tick, root)


def run2():
    window = pyglet.window.Window(width = 400, height = 400, caption = "test")

    pyglet.clock.schedule_interval(pyglet_tick, 1)
    pyglet.app.run()

def pyglet_tick(dt):
    global pyglet_counter
    print("Pyglet running", pyglet_counter)
    pyglet_counter += 1

    global barrier
    barrier.wait()


if __name__ == '__main__':
    Thread(target=run1).start()
    Thread(target=run2).start()