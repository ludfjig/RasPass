import tkinter as tk
from tkinter import ttk
import time

SMALLFONT = ("Courier", 14)

class Popup:
    def __init__(self, window, title, startMsg, color="green"):
        """ Create the popup """
        self.window = window
        self.top = tk.Toplevel(self.window)
        self.top.title(title)
        self.mainLabel = tk.Label(self.top, text=startMsg, font=SMALLFONT, fg=color)
        self.mainLabel.pack(fill='x', padx=50, pady=5)
        self.window.update()

    def destroy(self, timeout : int):
        """ Destroy window after timeout seconds """
        time.sleep(timeout)
        self.top.destroy()

    def changeMsg(self, msg, color):
        """ Update the popup message """
        self.mainLabel.config(text=msg, fg=color)
        self.window.update()
