import serial
from serial.tools import list_ports
import time

import tkinter as tk
from tkinter import ttk
from PasswordView import PasswordView
from StartScreen import StartScreen
from AppComm import AppComm



class RasPassApp(tk.Tk):
    def __init__(self, commLink, parent=None):
        tk.Tk.__init__(self, parent)
        self.serial = commLink.s
        self.title("RasPass Password Manager")

        content = ttk.Frame(self, padding=(3, 3, 12, 12))
        content.grid(column=0, row=0, sticky="nsew")
        content.columnconfigure(0, weight=1)

        # connect pages
        self.frames = {}

        for page in (StartScreen, PasswordView) :
            frame = page(content, self, self.serial, commLink)

        # initialize frame of each page object
            self.frames[page] = frame
            frame.grid(row = 0, column = 0, sticky="nsew")

        self.show_frame(StartScreen)

    def show_frame(self, page):
        """Changes the view to the frame of the page passed in to parameter"""
        frame = self.frames[page]
        frame.tkraise()



def main():
    commLink = AppComm()

    rasPassApp = RasPassApp(commLink)

    rasPassApp.mainloop()


if __name__ == "__main__":
    main()
