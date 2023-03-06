import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import StartScreen
import pyperclip as pc
import hashlib
import crypto
import sv_ttk
from tkinter.messagebox import askyesno

LARGEFONT = ("Courier", 20)
MEDIUMFONT = ("Courier", 16)
SMALLFONT = ("Courier", 14)
BOLDFONT = ('Courier bold', 16)

STATUS_SUCCESS = 0
STATUS_MISSING_PARAM = 3        # Missing request parameter
STATUS_MALFORMED_REQ = 4        # Malformed request
STATUS_BAD_METHOD = 5           # Bad/nonexistent method
STATUS_FAILED_BIOMETRICS = 6    # Failed biometric, but not too many attempts
STATUS_NOT_VERIFIED = 7         # User must run verifyMasterHash
# Other (unhandled) exception thrown in code - traceback returned
STATUS_UNKNOWN_ERR = 10
STATUS_API_OTHER_ERROR = 11     # Other (handled) error in the API
STATUS_NOT_YET_IMPLEMENTED = 12  # API method exists, but not implemented


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
        #site_label = ttk.Label(column_names, width=20, font=MEDIUMFONT, text="Site", anchor=tk.CENTER)
       # username_label = ttk.Label(
           #column_names, width=20, font=MEDIUMFONT, text="Username")
        #password_label = ttk.Label(
            #column_names, width=20, font=MEDIUMFONT, text="Password")

        # banner
        header = self.open_img(banner, (550, 100), "./imgs/logo2.png")

        # ------------------ grid starts here -------------------------

        # frames
        content.grid(column=0, row=0)
        banner.grid(column=0, row=0, sticky="nsew")
        body.grid(column=0, row=3, sticky="nsew")
        column_names.grid(column=0, row=0, sticky="nsew")
        rows.grid(column=0, row=1, sticky="nsew")
        btnFrame.grid(column=0, row=6, pady=10)

        # column names
        #site_label.grid(column=0, row=0)
        #username_label.grid(column=1, row=0)
        #password_label.grid(column=2, row=0)

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

        style = ttk.Style()
        style.configure('Style.TButton', font=SMALLFONT)

        btn1 = ttk.Button(btnFrame, text="Lock Pico", style='Style.TButton',
                          command=lambda: self.switch_to_start(controller))

        btn1.grid(row=0, column=0, padx=10, ipady=5)

        btn2 = ttk.Button(btnFrame, text="Settings", style='Style.TButton',
                          command=lambda: self.settingsPopup())
        btn2.grid(row=0, column=1, padx=10, ipady=5)

        sv_ttk.set_theme("light")

    def returnEvent(self):
        pass

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

    def open_img(self, parent, dim, picture):
        img = Image.open(picture)
        img = img.resize((dim[0], dim[1]), Image.ANTIALIAS)
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

        s = tk.Entry(self.rows, width=20, font=("Courier bold", 14))
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
        self.site_entry = tk.Entry(self.rows, fg='grey', font=SMALLFONT)
        self.username_entry = tk.Entry(self.rows, fg='grey', font=SMALLFONT)
        self.password_entry = tk.Entry(self.rows, show="*", fg='grey', font=SMALLFONT)

        self.site_entry.insert(0, 'Sitename')
        self.username_entry.insert(0, 'Username')
        self.password_entry.insert(0, 'Password')

        self.site_entry.bind("<FocusIn>", lambda event: self.focus_entry(self.site_entry, 'Sitename'))
        self.username_entry.bind("<FocusIn>", lambda event: self.focus_entry(self.username_entry, 'Username'))
        self.password_entry.bind("<FocusIn>", lambda event: self.focus_entry(self.password_entry, 'Password'))

        self.site_entry.bind("<FocusOut>", lambda event: self.unfocus_entry(self.site_entry, 'Sitename'))
        self.username_entry.bind("<FocusOut>", lambda event: self.unfocus_entry(self.username_entry, 'Username'))
        self.password_entry.bind("<FocusOut>", lambda event: self.unfocus_entry(self.password_entry, 'Password'))

        self.add_new_pswd = ttk.Button(
            self.rows, text="Add", style="Style.TButton",
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

    def focus_entry(self, entry, msg):
        if entry.get() == msg:
            entry.delete(0, tk.END)
            entry.insert(0, '')
            entry.config(fg='black')

    def unfocus_entry(self, entry, msg):
        if entry.get() == '':
            entry.insert(0, msg)
            entry.config(fg='grey')

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

    def getUsername(self, sitename):
        # Open dialog/copy to clipboard
        resp = self.comm.getPassword(sitename)

        if resp is None:
            print("[ERR] Get username failed")
            return
        elif resp["status"] == self.comm.STATUS_NOT_VERIFIED:
            print("[ERR] Too many attempts for biometrics")
            self.controller.show_frame(StartScreen.StartScreen)
            return
        elif resp["status"] != self.comm.STATUS_SUCCESS:
            print("Unknown error while getting username. Status=", resp["status"])
            return

        cipher_uname = resp['username']
        plain_text_usr = crypto.decrypt(cipher_uname, self.get_master_pw_hash())
        pc.copy(plain_text_usr)
        print("[INFO] Got username")
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
            return
        elif resp["status"] != self.comm.STATUS_SUCCESS:
            print("Unknown error while getting password. Status=", resp["status"])
            return

        cipher_text = resp['password']
        plain_text_pw = crypto.decrypt(cipher_text, self.get_master_pw_hash())
        pc.copy(plain_text_pw)
        print("[INFO] Got password")
        return resp

    def settingsPopup(self):
        # Open dialog to change password or username
        res = self.comm.getSettings()
        if res['status'] != STATUS_SUCCESS:
            print("[ERR] Authentification failure")
            return

        top = tk.Toplevel(self)
        top.geometry("550x400")
        top.title("RasPass Settings")

        image = self.open_img(top, (400, 75), "./imgs/Settings.png")
        image.grid(column=0, row=0)

        settings = res['settings']
        fingerPrints = settings['fingerprints']
        passwordsAvail = settings['numPswdAvail']

        storageWrapper = tk.Frame(top, width=500, height=30)
        storageWrapper.grid(column=0, row=2, padx=25, pady=20, sticky='nw')
        storageWrapper.grid_propagate(False)
        storage = tk.Text(storageWrapper, font=LARGEFONT)
        storage.tag_configure("bold", font=BOLDFONT)
        storage.insert("end", "Storage Available: ", "bold")
        storage.insert("end", "%s password entries" % passwordsAvail)
        storage.config(state="disabled", borderwidth=0, highlightthickness=0)
        storage.grid(column=0, row=0, sticky='nw')

        style = ttk.Style()
        style.configure('Settings.TButton', font=MEDIUMFONT)
        enrollBtn = ttk.Button(top, text="Enroll New Fingerprint", style='Settings.TButton',
                              command=lambda: self.enrollFinger(top, enrollBtn))
        enrollBtn.grid(column=0, row=4, padx=25, pady=10, sticky='nw')

        regFingers = tk.Label(top, font=BOLDFONT, text="Fingerprints registered:")
        regFingers.grid(column=0, row=6, padx=25, pady=10, sticky='nw')

        rows = ttk.Frame(top)
        rows.grid(column=0, row=8, padx=25, pady=5, sticky='nw')

        if len(fingerPrints) == 0:
            tk.Label(rows, text='No fingerprints registered', fg='red', font=MEDIUMFONT).grid()
        for finger in fingerPrints:
            self.initFingerprintEntry(rows, fingerPrints[finger])

    def enrollFinger(self, parent, btn):
        btn.grid_forget()
        frame = tk.Frame(parent)
        frame.grid(column=0, row=4, padx=25, pady=10, sticky='nw')

        name = tk.Entry(frame, fg='grey', font=SMALLFONT)
        name.insert(0, "Fingerprint name")
        name.grid(column=0, row=0)

        name.bind("<FocusIn>", lambda event: self.focus_entry(name, 'Fingerprint name'))

        submit = ttk.Button(frame, width=8, text="submit", style='Style.TButton',
                            command=lambda: self.comm.enrollFingerprint(name.get()))
        submit.grid(column=1, row=0)

        #cancel = ttk.Button(frame, width=8, text="cancel", style='Style.TButton',
        #                    command=lambda: self.cancelEnroll(btn, submit, cancel, name))
        #cancel.grid(column=2, row=0)

    """
    def cancelEnroll(self, btn, submit, cancel, name):
        submit.grid_remove()
        cancel.grid_remove()
        name.grid_remove()
        btn.grid(column=0, row=4, padx=25, pady=10, sticky='nw')
    """

    def initFingerprintEntry(self, rows, name):
        _, rownum = rows.grid_size()
        items = []

        entry = tk.Entry(rows,  width=20, font=("Courier bold", 14))
        delete = ttk.Button(rows, width=20, text="Delete", style='Style.TButton',
                       command=lambda: self.deleteFingerprint)

        items.append(entry)
        items.append(delete)

        entry.insert(0, name)
        entry.config(state="readonly")

        entry.grid(row=rownum, column=0, sticky="nesw")
        delete.grid(row=rownum, column=1, sticky="nesw")

    def deleteFingerprint(self):
        pass

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
            return False
        elif resp["status"] != self.comm.STATUS_SUCCESS:
            print("Unknown error while removing password. Status=", resp["status"])
            return False

        for i in items:
            i.destroy()

        return True
