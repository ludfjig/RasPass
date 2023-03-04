import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import PasswordView
import hashlib
import base64


LARGEFONT = ("Courier", 20)
SMALLFONT = ("Courier", 14)


class StartScreen(tk.Frame):
    def __init__(self, parent, controller, s, commLink):
        tk.Frame.__init__(self, parent)
        self.s = s
        self.comm = commLink

        self.open_img("./imgs/logo2.png")

        # check if master password has already been set up
        # if not, ask to set password instead of enter master password
        self.label = ttk.Label(
            self, text="Enter master password:", font=LARGEFONT)
        self.label.grid(row=3, column=0, columnspan=1)

        btn1 = tk.Button(self, text="Submit", font=SMALLFONT,
                         command=lambda: self.checkMasterPass(controller, s))

        btn1.grid(row=4, column=1)

        self.master = ttk.Entry(self, width=30, show="*", font=SMALLFONT)
        self.master.grid(row=4, column=0, pady=10, columnspan=1)

    def checkMasterPass(self, controller, s):
        # check that the entered password hash matches the password hash stored
        # in the raspass
        # if it does, switch to password view
        # if not, give 2 more attempts before 5min timeout (timing if pico disconnected?)
        pass_hash = self.get_master_pw_hash()

        pass_hash = base64.b64encode(pass_hash).decode('ascii')
        self.master.delete(0, tk.END)

        print("[INFO] Password: %s. Hash: %s" %(self.master.get(), pass_hash))
        pass_check = self.comm.verifyMasterHash(pass_hash[-4:])
        if not pass_check or not pass_check["valid"]:
            print("[WARN] Incorrect master password")
            return
        controller.show_frame(PasswordView.PasswordView)

    def get_master_pw_hash(self):
        m = hashlib.sha256()
        m.update(self.master.get().encode('utf-8'))
        return m.digest()

    def open_img(self, picture):
        img = Image.open(picture)
        img = img.resize((792, 149), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        panel = ttk.Label(self, image=img)
        panel.image = img
        panel.grid(column=0, row=0, padx=10, pady=10, columnspan=7, rowspan=2)
