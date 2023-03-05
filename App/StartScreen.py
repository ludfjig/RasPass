import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import PasswordView
import hashlib
import base64
import sv_ttk


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
        self.statusMsg = tk.Label(
            self, text="Status: Not connected", fg="red", font=SMALLFONT)
        self.statusMsg.grid(row=3, column=0, columnspan=2, pady=10)

        self.connBtn = ttk.Button(self, text="Connect to Pico", #font=SMALLFONT,
                         command=self.togglePicoConn)
        self.connBtn.grid(row=4, column=0, columnspan=2, sticky="nesw")
        self.checkPwBtn = ttk.Button(self, text="Check Master Password", #font=SMALLFONT,
                         command=lambda: self.checkMasterPass(controller, s))
        self.checkPwBtn.grid(row=5, column=1, sticky="nesw")
        self.checkPwBtn["state"] = "disabled"

        self.master = ttk.Entry(self, width=30, show="*", font=SMALLFONT)
        self.master.grid(row=5, column=0, columnspan=1, sticky="nesw")

        sv_ttk.set_theme("light")
        controller.bind('<Return>', lambda event: self.checkMasterPass(controller, s))

    def checkMasterPass(self, controller, s):
        # check that the entered password hash matches the password hash stored
        # in the raspass
        # if it does, switch to password view
        # if not, give 2 more attempts before 5min timeout (timing if pico disconnected?)
        self.statusMsg.config(text="Status: Checking password...", fg="orange")
        pass_hash = self.get_master_pw_hash()

        pass_hash = base64.b64encode(pass_hash).decode('ascii')
        self.master.delete(0, tk.END)
        controller.update_idletasks()

        print("[INFO] Password: %s. Hash: %s" %(self.master.get(), pass_hash))
        pass_check = self.comm.verifyMasterHash(pass_hash[-4:])
        if not pass_check or "valid" not in pass_check or not pass_check["valid"]:
            print("[WARN] Incorrect master password")
            self.statusMsg.config(text="Status: Incorrect password", fg="red")
            return
        controller.show_frame(PasswordView.PasswordView)

    def togglePicoConn(self):
        """ Connect to a Pico, if available """
        if self.comm.s is None:
            if self.comm.initConn():
                self.statusMsg.config(text="Status: Connected", fg="green")
                self.connBtn.config(text="Disconnect from Pico")
                self.checkPwBtn["state"] = "normal"
                return
            self.statusMsg.config(text="Status: Failed to connect", fg="red")
        else:
            self.comm.disconnect()
            self.statusMsg.config(text="Status: Not connected", fg="red")
        self.connBtn.config(text="Connect to Pico")
        self.checkPwBtn["state"] = "disabled"

    def get_master_pw_hash(self):
        m = hashlib.sha256()
        m.update(self.master.get().encode('utf-8'))
        return m.digest()

    def open_img(self, picture):
        img = Image.open(picture)
        img = img.resize((800, 150), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        panel = ttk.Label(self, image=img)
        panel.image = img
        panel.grid(column=0, row=0, padx=10, pady=5, columnspan=2, rowspan=1)

    def onShowFrame(self):
        """ Event handler for show frame """
        if self.comm.s is not None:
            self.statusMsg.config(text="Status: Connected", fg="green")
        else:
            self.statusMsg.config(text="Status: Not connected", fg="red")
