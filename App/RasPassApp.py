import tkinter as tk
from tkinter import ttk
import sv_ttk

from PasswordView import PasswordView
from StartScreen import StartScreen
from AppComm import AppComm


class RasPassApp(tk.Tk):
    def __init__(self, commLink, parent=None):
        tk.Tk.__init__(self, parent)
        self.serial = commLink.s
        commLink.setWindow(self)
        self.title("RasPass Password Manager")
        self.geometry("850x350")
        self.iconbitmap("imgs/logo.ico")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        content = ttk.Frame(self, padding=(3, 3, 12, 12))
        content.grid(column=0, row=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        # connect pages
        self.frames = {}

        start_screen = StartScreen(content, self, self.serial, commLink)
        password_view = PasswordView(
            content, self, self.serial, commLink, start_screen.master)
        start_screen.grid(row=0, column=0, sticky="nsew")
        password_view.grid(row=0, column=0, sticky="nsew")
        self.frames[StartScreen] = start_screen
        self.frames[PasswordView] = password_view

        self.show_frame(StartScreen)

    def show_frame(self, page):
        """Changes the view to the frame of the page passed in to parameter"""
        frame = self.frames[page]
        frame.onShowFrame()
        frame.tkraise()
        self.bind('<Return>', lambda event: frame.returnEvent())


def main():

    commLink = AppComm()

    rasPassApp = RasPassApp(commLink)

    sv_ttk.set_theme("light")

    rasPassApp.mainloop()


if __name__ == "__main__":
    main()
