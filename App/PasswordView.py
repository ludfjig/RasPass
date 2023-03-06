import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import StartScreen
import pyperclip as pc
import hashlib
import crypto
import sv_ttk


LARGEFONT = ("Courier", 20)
MEDIUMFONT = ("Courier", 16)
SMALLFONT = ("Courier", 14)


class PasswordView(tk.Frame):
    def __init__(self, parent, controller, s, commLink, master_pw):
        tk.Frame.__init__(self, parent)
        self.master_pw = master_pw
        self.s = s
        self.controller = controller
        self.comm = commLink
        self.ledState = 1
        self.addedRows = False

        self.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        content = ttk.Frame(self, padding=(3, 3, 12, 12))

        banner = ttk.Frame(content)
        body = ttk.Frame(content, borderwidth=5)
        btnFrame = tk.Frame(content, width=40)

        column_names = ttk.Frame(body)
        rows = ttk.Frame(body)
        self.rows = rows

        # column names
        #site_label = ttk.Label(column_names, width=20, font=MEDIUMFONT, text="Site")
        #username_label = ttk.Label(
        #    column_names, width=20, font=MEDIUMFONT, text="Username")
        #password_label = ttk.Label(
        #    column_names, width=20, font=MEDIUMFONT, text="Password")
        #main_label = ttk.Label(
        #    column_names, width=20, font=MEDIUMFONT, text="Passwords")

        # banner
        header = self.open_img(banner, "./imgs/logo2.png")

        # ------------------ grid starts here -------------------------

        # frames
        content.grid(column=0, row=0)
        banner.grid(column=0, row=0, sticky="nsew")
        body.grid(column=0, row=3, sticky="nsew")
        column_names.grid(column=0, row=0, sticky="nsew")
        rows.grid(column=0, row=1, sticky="nsew")
        btnFrame.grid(column=0, row=6, pady=10)

        # column names
        #main_label.grid(column=0, columnspan=5)
        #site_label.grid(column=0, row=0, sticky="nsew")
        #username_label.grid(column=1, row=0, sticky="nsew")
        #password_label.grid(column=2, row=0, sticky="nsew")

        # new password button

        # ----------  fill   starts here ---------------------------
        parent.columnconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)
        banner.columnconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)
        column_names.columnconfigure(0, weight=1)
        rows.columnconfigure(0, weight=1)
        btnFrame.columnconfigure(0, weight=1)

        column_names.columnconfigure(0, weight=1)
        column_names.columnconfigure(1, weight=1)
        column_names.columnconfigure(2, weight=1)
        column_names.columnconfigure(3, weight=1)
        column_names.columnconfigure(4, weight=1)

        rows.columnconfigure(0, weight=1)
        rows.columnconfigure(1, weight=1)
        rows.columnconfigure(2, weight=1)
        rows.columnconfigure(3, weight=1)
        rows.columnconfigure(4, weight=1)

        header.grid(column=0, row=0, columnspan=5)

        self.style = ttk.Style()
        self.style.configure('Style.TButton', font=SMALLFONT)

        btn1 = ttk.Button(btnFrame, text="Lock Pico", style='Style.TButton',
                          command=lambda: self.switch_to_start(controller))

        btn1.grid(row=0, column=0, padx=10, ipady=5)

        btn2 = ttk.Button(btnFrame, text="Settings", style='Style.TButton',
                          command=lambda: self.settingsPopup())
        btn2.grid(row=0, column=1, padx=10, ipady=5)

        sv_ttk.set_theme("light")

    def onShowFrame(self):
        """ Event handler for show frame """
        # entires
        if not self.addedRows:
            self.init_password_rows()
            self.init_input_row()
            self.addedRows = True

    def switch_to_start(self, controller):
        self.clear_input_row()
        controller.show_frame(StartScreen.StartScreen)

    def open_img(self, parent, picture):
        img = Image.open(picture)
        img = img.resize((550, 100), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        panel = ttk.Label(parent, image=img)
        panel.image = img
        return panel

    def remember_input_row(self):
        rows = 100
        self.site_entry.grid(column=0, row=rows, sticky="new")
        self.username_entry.grid(column=1, row=rows, sticky="new")
        self.password_entry.grid(column=2, row=rows, sticky="new")
        self.add_new_pswd.grid(column=3, row=rows, sticky="new", columnspan=2)

    def forget_input_row(self):
        self.username_entry.grid_forget()
        self.site_entry.grid_forget()
        self.password_entry.grid_forget()
        self.add_new_pswd.grid_forget()

    def clear_input_row(self):
        self.username_entry.delete(0, 'end')
        self.site_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')

    def add_row(self, site):
        _, rows = self.rows.grid_size()

        items = []

        s = ttk.Entry(self.rows, width=20, font=("Courier bold", 14))
        u = ttk.Button(self.rows, width=20, text="Get Username", style='Style.TButton',
                       command=lambda: self.getUsername(site))
        g = ttk.Button(self.rows, width=20, text="Get Password", style='Style.TButton',
                       command=lambda: self.getPassword(site))
        c = ttk.Button(
            self.rows, text="Change", style='Style.TButton',
                        command=lambda: self.changePswdUsr(site))
        d = ttk.Button(
            self.rows, text="Delete",style='Style.TButton',
                        command=lambda: self.deletePassword(site, items))

        items.append(s)
        items.append(u)
        items.append(g)
        items.append(c)
        items.append(d)

        s.grid(row=rows, column=0, sticky="nesw")
        s.insert(0, site)
        s.config(state="readonly")
        u.grid(row=rows, column=1, sticky="nesw")
        g.grid(row=rows, column=2, sticky="nesw")
        c.grid(row=rows, column=3, sticky="nesw")
        d.grid(row=rows, column=4, sticky="nesw")

    def init_input_row(self):
        self.site_entry = ttk.Entry(self.rows)
        self.username_entry = ttk.Entry(self.rows)
        self.password_entry = ttk.Entry(self.rows, show="*")
        self.add_new_pswd = ttk.Button(
            self.rows, text="Add", style='Style.TButton',
            command=lambda: self.addPassword(
                self.site_entry.get(),
                self.username_entry.get(),
                self.password_entry.get()
            ))

        rows = 100  # any large number
        self.site_entry.grid(column=0, row=rows, sticky="nesw")
        self.username_entry.grid(column=1, row=rows, sticky="nesw")
        self.password_entry.grid(column=2, row=rows, sticky="nesw")
        self.add_new_pswd.grid(column=3, row=rows, sticky="nesw", columnspan=2)

    def get_master_pw_hash(self):
        m = hashlib.sha256()
        m.update(self.master_pw.get().encode('utf-8'))
        return m.digest()

    def init_password_rows(self):
        site_reply = self.comm.getAllSiteNames()
        if site_reply is not None and site_reply["status"] == self.comm.STATUS_SUCCESS:
            sitenames = site_reply["sitenames"]
            for i in range(len(sitenames)):
                self.add_row(sitenames[i])

    def addPassword(self, sitename, username, password):
        # Add and refresh interface (e.g. show in list)

        # encryption
        cipher_pass = crypto.encrypt(password, self.get_master_pw_hash())
        cipher_usr = crypto.encrypt(username, self.get_master_pw_hash())

        resp = self.comm.addPassword(sitename, cipher_usr, cipher_pass)
        if resp is None:
            print("[ERR] Add password failed")
            return
        elif resp["status"] == self.comm.STATUS_API_OTHER_ERROR:
            print("Password already exists in db")
            return
        elif resp["status"] != self.comm.STATUS_SUCCESS:
            print("Unknown error while adding password. Status=", resp["status"])
            return

        self.forget_input_row()
        self.add_row(sitename)
        self.clear_input_row()
        self.remember_input_row()
        #print(self.rows.grid_size())

    def getUsername(self, sitename):
        # Open dialog/copy to clipboard
        resp = self.comm.getPassword(sitename)

        if resp is None:
            print("[ERR] Get username failed")
            return
        elif resp["status"] == self.comm.STATUS_NOT_VERIFIED:
            print("[ERR] Too many attempts for biometrics")
            self.controller.show_frame(StartScreen.StartScreen)
        elif resp["status"] != self.comm.STATUS_SUCCESS:
            print("Unknown error while getting username. Status=", resp["status"])
            return

        cipher_uname = resp['username']
        plain_text_usr = crypto.decrypt(cipher_uname, self.get_master_pw_hash())
        pc.copy(plain_text_usr)
        print("[INFO] Got username: ", plain_text_usr)
        return resp

    def getPassword(self, sitename):
        # Open dialog/copy to clipboard
        resp = self.comm.getPassword(sitename)

        if resp is None:
            print("[ERR] Get password failed")
            return
        elif resp["status"] == self.comm.STATUS_NOT_VERIFIED:
            print("[ERR] Too many attempts for biometrics")
            self.controller.show_frame(StartScreen.StartScreen)
        elif resp["status"] != self.comm.STATUS_SUCCESS:
            print("Unknown error while getting password. Status=", resp["status"])
            return

        cipher_text = resp['password']
        plain_text_pw = crypto.decrypt(cipher_text, self.get_master_pw_hash())
        pc.copy(plain_text_pw)
        print("[INFO] Got password: ", plain_text_pw)
        return resp

    def settingsPopup(self):
        # Open dialog to change password or username
        top = tk.Toplevel(self)
        top.geometry("350x150")
        top.title("RasPass Settings")

        storage = ttk.Label(top, text="Storage available: ")
        storage.grid(column=0, row=0, padx=25, pady=25)

    def changePswdUsr(self, sitename):
        # Open dialog to change password or username
        top = tk.Toplevel(self)
        top.geometry("350x150")
        top.title("Update %s info" % sitename)
        site = ttk.Label(top, text="Update info for %s" % sitename, font=LARGEFONT)
        site.grid(column=0, row=0, padx=25, pady=15)

        usrbtn = ttk.Button(top, width=15, text="Change Username", style='Style.TButton',)
        usrbtn.grid(column=0, row=2, padx=25)
        usrbtn['command'] = lambda: self.changeField(top, usrbtn, 2, sitename)

        pswdbtn = ttk.Button(top, width=15, text="Change Password", style='Style.TButton',)
        pswdbtn.grid(column=0, row=4, padx=25)
        pswdbtn['command'] = lambda: self.changeField(top, pswdbtn, 4, sitename)
        ttk.Button(top, width=10, text="Cancel", style='Style.TButton',
                   command=lambda: top.destroy()).grid(column=0, row=6, padx=25, pady=15)

    def changeField(self, popup, btn, rw, site):
        if btn['text'] == "Change Username":
            field = "usr"
        else:
            field = "pass"

        btn.grid_forget()
        frame = tk.Frame(popup, width=25)
        frame.grid(column=0, row=rw, padx=25)

        change = tk.Entry(frame, width=15, font=SMALLFONT, show="*")
        change.grid(column=0, row=0)

        submit = ttk.Button(frame, width=8, text="submit", style='Style.TButton',
                            command=lambda: self.initiateChange(popup, field, change, site))
        submit.grid(column=1, row=0)

    def initiateChange(self, popup, field, change, site):
        new = change.get().strip()
        if field == "usr":
            cipher_usr = crypto.encrypt(new, self.get_master_pw_hash())
            self.comm.changeUsername(site, cipher_usr)
        else:
            cipher_pass = crypto.encrypt(new, self.get_master_pw_hash())
            self.comm.changePassword(site, cipher_pass)
        popup.destroy()

    def deletePassword(self, sitename, items):
        # Delete and refresh interface

        # should probably prompt the user again to make sure they really meant
        # to delete the password
        resp = self.comm.removePassword(sitename)

        if resp is None:
            print("[ERR] Remove password failed")
            return False
        elif resp["status"] == self.comm.STATUS_NOT_VERIFIED:
            print("[ERR] Too many attempts for biometrics")
            self.controller.show_frame(StartScreen.StartScreen)
        elif resp["status"] != self.comm.STATUS_SUCCESS:
            print("Unknown error while removing password. Status=", resp["status"])
            return False

        for i in items:
            i.destroy()

        return True
