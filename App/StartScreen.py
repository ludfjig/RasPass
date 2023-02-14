import tkinter as tk
from tkinter import ttk
import PasswordView
import serial
from serial.tools import list_ports


LARGEFONT = ("Arial", 12)

class StartScreen(tk.Frame):
  def __init__(self, parent, controller, s, commLink):
    tk.Frame.__init__(self, parent)
    self.s = s

    label = ttk.Label(self, text = "Enter master password", font = LARGEFONT)
    label.grid(row = 0, column = 1, padx = 10, pady = 10, columnspan=2)

    btn1 = ttk.Button(self, text = "Submit",
            command = lambda : controller.show_frame(PasswordView.PasswordView))

    btn1.grid(row = 1, column = 2, padx = 10, pady = 10)

    self.master = ttk.Entry(self, show="*")
    self.master.grid(row=1, column=1, padx=10, pady=10)

