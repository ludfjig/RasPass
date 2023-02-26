import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import StartScreen
import pyperclip as pc
import hashlib
import crypto


LARGEFONT = ("Courier", 20)
MEDIUMFONT = ("Courier", 16)
SMALLFONT = ("Courier", 14)


class PasswordView(tk.Frame):
    def __init__(self, parent, controller, s, commLink, master_pw):
        tk.Frame.__init__(self, parent)
        # access master password through self.master_pw.get()
        self.master_pw = master_pw
        self.s = s
        self.controller = controller
        self.comm = commLink
        self.ledState = 1
        content = ttk.Frame(self, padding=(3, 3, 12, 12))

        banner = ttk.Frame(content, borderwidth=4, relief="solid")
        body = ttk.Frame(content, borderwidth=5, relief="ridge")

        column_names = ttk.Frame(body, borderwidth=2, relief="solid")
        rows = ttk.Frame(body, borderwidth=2, relief="solid")
        self.rows = rows
        # column names
        site_label = ttk.Label(column_names, width=20, font=MEDIUMFONT, text="Site")
        username_label = ttk.Label(
            column_names, width=20, font=MEDIUMFONT, text="Username")
        password_label = ttk.Label(
            column_names, width=20, font=MEDIUMFONT, text="Password")

        # banner
        #header = ttk.Label(banner, text="RasPass", font=("Arial", 25))
        header = self.open_img(banner, "./imgs/logo2.png")

        # ------------------ grid starts here -------------------------

        # frames
        content.grid(column=0, row=0, sticky="nsew")
        banner.grid(column=0, row=0, sticky="nsew")
        body.grid(column=0, row=3, sticky="nsew")
        column_names.grid(column=0, row=0, sticky="nsew")
        rows.grid(column=0, row=1, sticky="nsew")

        # column names
        site_label.grid(column=0, row=0)
        username_label.grid(column=1, row=0)
        password_label.grid(column=2, row=0)

        # entires
        self.init_password_rows()
        self.init_input_row()

        # new password button

        # ----------  fill   starts here ---------------------------
        parent.columnconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)
        banner.columnconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)
        column_names.columnconfigure(0, weight=1)
        rows.columnconfigure(0, weight=1)

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

        btn1 = tk.Button(self, text="Start Screen", font=MEDIUMFONT,
                          command=lambda: controller.show_frame(StartScreen.StartScreen))

        btn1.grid(row=1, column=0, padx=10, pady=10)

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
        # rows += 1
        print(site, self.rows.grid_size())

        items = []

        s = ttk.Entry(self.rows, width=20, font=("Courier bold", 14))
        u = tk.Button(self.rows, width=20, font=SMALLFONT, text="Get Username",
                       command=lambda: self.getUsername(site))
        g = tk.Button(self.rows, width=20, font=SMALLFONT, text="Get Password",
                       command=lambda: self.getPassword(site))
        c = tk.Button(
            self.rows, text="Change", font=SMALLFONT, command=lambda: self.changePassword(site, items))
        d = tk.Button(
            self.rows, text="Delete", font=SMALLFONT, command=lambda: self.deletePassword(site, items))

        items.append(s)
        items.append(u)
        items.append(g)
        items.append(c)
        items.append(d)

        s.grid(row=rows, column=0, sticky="new")
        s.insert(0, site)
        s.config(state="readonly")
        u.grid(row=rows, column=1, sticky="new")
        # p.grid(row=i, column=2, sticky="new")
        g.grid(row=rows, column=2, sticky="new")
        c.grid(row=rows, column=3, sticky="new")
        d.grid(row=rows, column=4, sticky="new")

    def init_input_row(self):
        self.site_entry = ttk.Entry(self.rows)
        self.username_entry = ttk.Entry(self.rows)
        self.password_entry = ttk.Entry(self.rows, show="*")
        self.add_new_pswd = tk.Button(
            self.rows, text="Add", font=SMALLFONT, command=lambda: self.addPassword(
                self.site_entry.get(),
                self.username_entry.get(),
                self.password_entry.get()
            ))

        rows = 100  # any large number
        self.site_entry.grid(column=0, row=rows, sticky="new")
        self.username_entry.grid(column=1, row=rows, sticky="new")
        self.password_entry.grid(column=2, row=rows, sticky="new")
        self.add_new_pswd.grid(column=3, row=rows, sticky="new", columnspan=2)

    def get_master_pw_hash(self):
        m = hashlib.sha256()
        m.update(self.master_pw.get().encode('utf-8'))
        return m.digest()

    def init_password_rows(self):
        site_reply = self.comm.getAllSiteNames()
        print(site_reply)
        if site_reply["status"] == 0:
            sitenames = site_reply["sitenames"]
            for i in range(len(sitenames)):
                self.add_row(sitenames[i])

    def addPassword(self, sitename, username, password):
        # Add and refresh interface (e.g. show in list)
        print("Adding password", password)
        # TODO: encrypt username, password
        # TODO: check length of sitename, username, password!!

        # encryption
        cipher_text = crypto.encrypt(password, self.get_master_pw_hash())

        addPass = self.comm.addPassword(sitename, username, cipher_text)
        while addPass['status'] != 0:
            if addPass["status"] == 1:
                print("Authentification failure")
            elif addPass["status"] == 5:
                print("Password already exists in db")
            else:
                print("Unknown error")
            addPass = self.comm.addPassword(sitename, username, cipher_text)

        print(addPass)

        # pswd = self.comm.getPassword(sitename)
        self.forget_input_row()
        self.add_row(sitename)
        self.clear_input_row()
        self.remember_input_row()
        print(self.rows.grid_size())
        # print("returned password: ", pswd)

    def getUsername(self, sitename):
        # Open dialog/copy to clipboard
        ret = self.comm.getPassword(sitename)
        while ret['status'] != 0:
            print("Authentification failure")
            ret = self.comm.getPassword(sitename)
        print(ret)
        uname = ret['username']
        pc.copy(uname)
        print("returned username: ", uname)
        return ret

    def getPassword(self, sitename):
        # Open dialog/copy to clipboard
        ret = self.comm.getPassword(sitename)
        while ret['status'] != 0:
            print("Authentification failure")
            ret = self.comm.getPassword(sitename)
        print(ret)
        cipher_text = ret['password']
        plain_text_pw = crypto.decrypt(cipher_text, self.get_master_pw_hash())
        pc.copy(plain_text_pw)
        print("returned password: ", plain_text_pw)
        return ret

    def changePassword(self, sitename):
        # Open dialog to change password

        pass

    def deletePassword(self, sitename, items):
        # Delete and refresh interface

        # should probably prompt the user again to make sure they really meant
        # to delete the password
        ret = self.comm.removePassword(sitename)

        if ret == 1:
            print("unable to remove password")
            return False
        elif ret == 3:
            print("error occurred while deleting")
            return False

        for i in items:
            i.destroy()

        return True
