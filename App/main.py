import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

class RasPassApp:
  def __init__(self, tk):
    print("hi")

def main():
  # create Tk instance
  window = tk.Tk()
  # set program title
  window.title("RasPass Password Manager")
  # create app instance
  rasPassApp = RasPassApp(window)
  # run event loop
  window.mainloop()

if __name__ == "__main__":
    main()