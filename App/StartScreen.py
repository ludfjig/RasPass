import tkinter as tk
from tkinter import ttk
import PasswordView
import serial
from serial.tools import list_ports


LARGEFONT = ("Arial", 35)

class StartScreen(tk.Frame):
  def __init__(self, parent, controller, s, commLink):
    tk.Frame.__init__(self, parent)
    self.s = s

    label = ttk.Label(self, text = "Start Screen", font = LARGEFONT)
    label.grid(row = 0, column = 4, padx = 10, pady = 10)

    btn1 = ttk.Button(self, text = "Password View",
            command = lambda : controller.show_frame(PasswordView.PasswordView))

    btn1.grid(row = 1, column = 1, padx = 10, pady = 10)
