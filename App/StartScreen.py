import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import PasswordView
import hashlib
import base64
import sv_ttk
import time


LARGEFONT = ("Courier", 20)
SMALLFONT = ("Courier", 14)

""" Creates and manages the Start Screen for the RasPassApp.
    Blocks user from accessing password view until a valid master password
    has been entered.
"""


class StartScreen(tk.Frame):
    def __init__(self, parent, controller, s, commLink):
        tk.Frame.__init__(self, parent)
        self.s = s
        self.window = controller
        self.comm = commLink
        self.grid(row=0, column=0, sticky="ne")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.open_img("./imgs/logo2.png")

        self.style = ttk.Style()
        self.style.configure('Style.TButton', font=SMALLFONT)

        # display whether or not the Pico has been successfully connected
        self.statusMsg = tk.Label(
            self, text="Status: Not connected", fg="red", font=SMALLFONT)
        self.statusMsg.grid(row=3, column=0, columnspan=2, pady=5)

        # button to initiate attempt to connect to pico
        self.connBtn = ttk.Button(self, text="Connect to Pico", width=20,
                                  style='Style.TButton',
                                  command=self.togglePicoConn)
        self.connBtn.grid(row=4, column=0, columnspan=2, pady=20)

        self.entryFrame = tk.Frame(self, width=50)
        self.entryFrame.grid(row=5, column=0)
        self.checkPwBtn = ttk.Button(self.entryFrame,
                                     text="Check Master Password",
                                     style='Style.TButton',
                                     command=lambda: self.checkMasterPass(controller, s))

        self.checkPwBtn.grid(row=0, column=1, padx=10)
        # check master password button disabled until pico connected
        self.checkPwBtn["state"] = "disabled"

        self.master = ttk.Entry(
            self.entryFrame, width=35, show="*", font=SMALLFONT)
        self.master.grid(row=0, column=0, padx=10)
        self.master.config(state="disabled")

        sv_ttk.set_theme("light")

    def returnEvent(self):
        """ On return key click, submits and checks the master password entry.
        """
        self.checkMasterPass(self.window, self.s)

    def checkMasterPass(self, controller, s):
        """ Checks that the hash of the last 4 bytes of entered master password
            matches the password hash stored in the secure storage of the
            fingerprint sensor.

            If password valid, switches to the PasswordView.
            If not, displays message informing user of an incorrect password
        """
        self.statusMsg.config(text="Status: Checking password...", fg="orange")
        pass_hash = self.get_master_pw_hash()

        pass_hash = base64.b64encode(pass_hash).decode('ascii')
        self.master.delete(0, tk.END)
        controller.update_idletasks()

        print("[INFO] Password: %s. Hash: %s" % (self.master.get(), pass_hash))

        # check hash of last four bytes of password against stored password
        pass_check = self.comm.verifyMasterHash(pass_hash[-4:])
        if not pass_check or "valid" not in pass_check or \
           not pass_check["valid"]:
            print("[WARN] Incorrect master password")
            self.statusMsg.config(text="Status: Incorrect password", fg="red")
            return
        # valid master password initiates change to password view
        controller.show_frame(PasswordView.PasswordView)

    def togglePicoConn(self):
        """ Connect to a Pico, if available """
        if self.comm.s is None:
            if not self.comm.initConn():
                self.statusMsg.config(
                    text="Status: Failed to connect", fg="red")
                self.statusMsg.update()
                time.sleep(1)
        else:
            self.comm.disconnect()
        self.checkPicoConn()

    def checkPicoConn(self):
        """ Check the connection to the Pico and update the UI """
        if self.comm.s is not None:
            self.statusMsg.config(text="Status: Connected", fg="green")
            self.connBtn.config(text="Disconnect from Pico")
            self.checkPwBtn["state"] = "normal"
            self.master.config(state="normal")
            return
        else:
            self.statusMsg.config(text="Status: Not connected", fg="red")
        self.connBtn.config(text="Connect to Pico")
        self.checkPwBtn["state"] = "disabled"
        self.master.config(state="disabled")

    def get_master_pw_hash(self):
        """ Returns the sha256 hash of the master password """
        m = hashlib.sha256()
        m.update(self.master.get().encode('utf-8'))
        return m.digest()

    def open_img(self, picture):
        """ Open and display the header image """
        img = Image.open(picture)
        img = img.resize((800, 150), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        panel = ttk.Label(self, image=img)
        panel.image = img
        panel.grid(column=0, row=0, padx=10, pady=5, columnspan=2, rowspan=1)
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(0, weight=1)

    def onShowFrame(self):
        """ Event handler for show frame """
        self.checkPicoConn()
