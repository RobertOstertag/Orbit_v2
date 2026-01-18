# Source - https://stackoverflow.com/a
# Posted by JRiggles, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-18, License - CC BY-SA 4.0

import tkinter as tk

master = tk.Tk()


def update():
    # do things
    master.after(1000, update)  # call update again after 1 second
    print("gello")


update()  # begin updates
master.mainloop()
