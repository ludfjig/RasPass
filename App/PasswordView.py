import tkinter as tk
from tkinter import ttk
import StartScreen
import serial
import pyperclip as pc
import json


LARGEFONT = ("Arial", 35)


class PasswordView(tk.Frame):
    def __init__(self, parent, controller, s, commLink):
        tk.Frame.__init__(self, parent)
        self.s = s
        self.comm = commLink
        self.ledState = 1
        content = ttk.Frame(self, padding=(3, 3, 12, 12))

        banner = ttk.Frame(content, borderwidth=5, relief="solid")
        body = ttk.Frame(content, borderwidth=5, relief="solid")

        column_names = ttk.Frame(body, borderwidth=5, relief="solid")
        rows = ttk.Frame(body, borderwidth=5, relief="solid")
        self.rows = rows
        # column names
        site_label = ttk.Label(column_names, text="Site")
        username_label = ttk.Label(
            column_names, text="Username")
        password_label = ttk.Label(
            column_names, text="Password")

        # banner
        header = ttk.Label(banner, text="RasPass", font=("Arial", 25))

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

        btn1 = ttk.Button(self, text="Start Screen",
                          command=lambda: controller.show_frame(StartScreen.StartScreen))

        btn1.grid(row=1, column=0, padx=10, pady=10)

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
        _ , rows = self.rows.grid_size()
        # rows += 1
        print(site, self.rows.grid_size())
        s = ttk.Entry(self.rows)
        u = ttk.Button(self.rows, text="Get Username",
                       command=lambda: self.getUsername(site))
        g = ttk.Button(self.rows, text="Get Password",
                       command=lambda: self.getPassword(site))
        c = ttk.Button(
            self.rows, text="Change", command=lambda: self.changePassword(site))
        d = ttk.Button(
            self.rows, text="Delete", command=lambda: self.deletePassword(site))

        s.grid(row=rows, column=0, sticky="new")
        s.insert(0, site)
        u.grid(row=rows, column=1, sticky="new")
        #p.grid(row=i, column=2, sticky="new")
        g.grid(row=rows, column=2, sticky="new")
        c.grid(row=rows, column=3, sticky="new")
        d.grid(row=rows, column=4, sticky="new")

    def init_input_row(self):
        self.site_entry = ttk.Entry(self.rows)
        self.username_entry = ttk.Entry(self.rows)
        self.password_entry = ttk.Entry(self.rows)
        self.add_new_pswd = ttk.Button(
            self.rows, text="Add", command=lambda: self.addPassword(
                self.site_entry.get(),
                self.username_entry.get(),
                self.password_entry.get()
            ))

        rows = 100  # any large number
        self.site_entry.grid(column=0, row=rows, sticky="new")
        self.username_entry.grid(column=1, row=rows, sticky="new")
        self.password_entry.grid(column=2, row=rows, sticky="new")
        self.add_new_pswd.grid(column=3, row=rows, sticky="new", columnspan=2)

    def init_password_rows(self):
        site_reply = self.comm.getAllSiteNames()
        print(site_reply)
        if site_reply["status"] == 0:
            sitenames = site_reply["sitenames"]
            for i in range(len(sitenames)):
                self.add_row(sitenames[i])

    def addPassword(self, sitename, username, password):
        # Add and refresh interface (e.g. show in list)
        print("Adding password")
        # TODO: encrypt username, password
        # TODO: check length of sitename, username, password!!
        addPass = self.comm.addPassword(sitename, username, password)
        print(addPass)
        if addPass["status"] == 0:
            print("Added password")
        elif addPass["status"] == 5:
            print("Password already exists in db")
        else:
            print("Unknown error")
            exit()
        pswd = self.comm.getPassword(sitename)
        self.forget_input_row()
        self.add_row(sitename)
        self.clear_input_row()
        self.remember_input_row()
        print(self.rows.grid_size())
        print("returned password: ", pswd)

    def getUsername(self, sitename):
        # Open dialog/copy to clipboard
        username = self.comm.getPassword(sitename)['username']
        pc.copy(username)
        print("returned username: ", username)

    def getPassword(self, sitename):
        # Open dialog/copy to clipboard
        pswd = self.comm.getPassword(sitename)['password']
        pc.copy(pswd)
        print("returned password: ", pswd)

    def changePassword(self, sitename):
        # Open dialog to change password
        pass

    def deletePassword(self, sitename):
        # Delete and refresh interface
        pass
