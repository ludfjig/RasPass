import serial
from serial.tools import list_ports
import time
import re

import tkinter as tk
from tkinter import ttk
from PasswordView import PasswordView
from StartScreen import StartScreen



class RasPassApp(tk.Tk):
    def __init__(self, serial, parent=None):
        tk.Tk.__init__(self, parent)
        self.s = serial
        self.title("RasPass Password Manager")

        content = ttk.Frame(self, padding=(3, 3, 12, 12))
        content.grid(column=0, row=0, sticky="nsew")
        content.columnconfigure(0, weight=1)

        # connect pages
        self.frames = {}

        for page in (StartScreen, PasswordView) :
            frame = page(content, self, self.s)

        # initialize frame of each page object
            self.frames[page] = frame
            frame.grid(row = 0, column = 0, sticky="nsew")

        self.show_frame(StartScreen)

    def show_frame(self, page):
        """Changes the view to the frame of the page passed in to parameter"""
        frame = self.frames[page]
        frame.tkraise()



def main():
    #root = tk.Tk()
    #root.title("RasPass Password Manager")

    s = None
    port = list_ports.comports()
    for p in port:
        info = p.vid
        if (p.vid == 11914):
            print(p.vid)
            device = p.device
            try:
                s = serial.Serial(device)
            except serial.SerialException:
                # for some reason when I do list_ports.comports on my mac it always
                # gives me "/dev/cu.usbmodem101" instead of "/dev/tty.usbmodem101"
                # so this is just forcing it to use tty for my computer if connecting
                # over cu fails
                device = re.sub(r'/cu', r'/tty', device)
                s = serial.Serial(device)
            break

    rasPassApp = RasPassApp(s)

    rasPassApp.mainloop()


if __name__ == "__main__":
    main()
