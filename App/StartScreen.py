import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import PasswordView


LARGEFONT = ("Arial", 12)


class StartScreen(tk.Frame):
    def __init__(self, parent, controller, s, commLink):
        tk.Frame.__init__(self, parent)
        self.s = s

        self.open_img()

        # check if master password has already been set up
        # if not, ask to set password instead of enter master password
        self.label = ttk.Label(
            self, text="Enter master password", font=LARGEFONT)
        self.label.grid(row=4, column=1, padx=10, pady=10, columnspan=2)

        btn1 = ttk.Button(self, text="Submit",
                          command=lambda: self.checkMasterPass(controller, s))

        btn1.grid(row=5, column=2, padx=10, pady=10)

        self.master = ttk.Entry(self, show="*")
        self.master.grid(row=5, column=1, padx=10, pady=10)

    def checkMasterPass(self, controller, s):
        # check that the entered password hash matches the password hash stored
        # in the raspass
        # if it does, switch to password view
        # if not, give 2 more attempts before 5min timeout (timing if pico disconnected?)
        self.master.delete(0, 'end')
        controller.show_frame(PasswordView.PasswordView)

    def open_img(self):
        img = Image.open("./imgs/logo.png")
        img = img.resize((250, 150), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        panel = ttk.Label(self, image=img)
        panel.image = img
        panel.grid(column=0, row=0, columnspan=7, rowspan=2)
