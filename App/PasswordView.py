import tkinter as tk
from tkinter import ttk
import StartScreen

LARGEFONT = ("Verdana", 35)

class PasswordView(tk.Frame):
  def __init__(self, parent, controller):
    tk.Frame.__init__(self, parent)

    label = ttk.Label(self, text = "Password View", font = LARGEFONT)

    label.grid(row = 0, column = 4, padx = 10, pady = 10)

    btn1 = ttk.Button(self, text = "Start Screen",
            command = lambda : controller.show_frame(StartScreen.StartScreen))

    btn1.grid(row = 1, column = 1, padx = 10, pady = 10)
