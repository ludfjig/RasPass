import tkinter as tk
from tkinter import ttk

from PasswordView import PasswordView
from StartScreen import StartScreen

class RasPassApp(tk.Tk):

  def __init__(self, parent=None):
    #__init__ function for class Tk
    tk.Tk.__init__(self, parent)
    self.title("RasPass App")
    # create a container
    container = tk.Frame(self)
    container.pack(side = "top", fill = "both", expand = True)

    container.grid_rowconfigure(0, weight = 1)
    container.grid_columnconfigure(0, weight = 1)

    # initialize empty array of frames
    self.frames = {}

    for page in (StartScreen, PasswordView) :
      frame = page(container, self)

      # initialize frame of each page object
      self.frames[page] = frame
      frame.grid(row = 0, column = 0, sticky="nsew")

    self.show_frame(StartScreen)

  def show_frame(self, page):
    """Changes the view to the frame of the page passed in to parameter"""
    frame = self.frames[page]
    frame.tkraise()

def main():
  # create app instance
  rasPassApp = RasPassApp()
  # run event loop
  rasPassApp.mainloop()

if __name__ == "__main__":
    main()