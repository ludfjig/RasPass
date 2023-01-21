from tkinter import *
from tkinter import ttk

class RasPassApp:
  def __init__(self, root):
    # set program title
    root.title("RasPass Password Manager")
    content = ttk.Frame(root, padding=10)
    content.grid(column=0, row=0, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    btn = ttk.Button(content, text="Quit", command=root.destroy).grid(column=1, row=1)


def main():
  # create Tk instance
  root = Tk()
  # create app instance
  rasPassApp = RasPassApp(root)
  # run event loop
  root.mainloop()

if __name__ == "__main__":
    main()