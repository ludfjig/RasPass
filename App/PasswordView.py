import tkinter as tk
from tkinter import ttk
import StartScreen
import serial

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

    # column names
    site_label = ttk.Label(column_names, text="Site")
    username_label = ttk.Label(
    column_names, text="Username")
    password_label = ttk.Label(
    column_names, text="Password")

    # actual entries / rows
    sitename = ttk.Entry(rows)
    username = ttk.Entry(rows)
    password = ttk.Entry(rows)
    add_new_pswd = ttk.Button(rows, text="Add", command=lambda : self.addPassword(sitename.get(), username.get(), password.get()))

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

    ss = self.comm.getAllSiteNames()
    n = 0
    if ss["status"] == 0:
      sitenames = ss["sitenames"]
      n = len(sitenames)
      for i in range(len(sitenames)):
        s = ttk.Entry(rows)
        u = ttk.Button(rows, text="Get Username", command=lambda sn = sitenames[i] : self.getUsername(sn))
        g = ttk.Button(rows, text="Get Password", command=lambda sn = sitenames[i] : self.getPassword(sn))
        c = ttk.Button(rows, text="Change", command=lambda sn = sitenames[i] : self.changePassword(sn))
        d = ttk.Button(rows, text="Delete", command=lambda sn = sitenames[i] : self.deletePassword(sn))
        s.grid(row=i, column=0, sticky="new")
        s.insert(0, sitenames[i])
        u.grid(row=i, column=1, sticky="new")
        #p.grid(row=i, column=2, sticky="new")
        g.grid(row=i, column=2, sticky="new")
        c.grid(row=i, column=3, sticky="new")
        d.grid(row=i, column=4, sticky="new")

    sitename.grid(column=0, row=n, sticky="new")
    username.grid(column=1, row=n, sticky="new")
    password.grid(column=2, row=n, sticky="new")
    add_new_pswd.grid(column=3, row=n, sticky="new", columnspan=2)
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


    btn1 = ttk.Button(self, text = "Start Screen",
            command = lambda : controller.show_frame(StartScreen.StartScreen))

    btn1.grid(row = 1, column = 0, padx = 10, pady = 10)


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
    print("returned password: ", pswd)

  def getUsername(self, sitename):
    # Open dialog/copy to clipboard
    pswd = self.comm.getPassword(sitename)
    print("returned password: ", pswd)

  def getPassword(self, sitename):
    # Open dialog/copy to clipboard
    pswd = self.comm.getPassword(sitename)
    print("returned password: ", pswd)

  def changePassword(self, sitename):
    # Open dialog to change password
    pass

  def deletePassword(self, sitename):
    # Delete and refresh interface
    pass
