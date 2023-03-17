import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import StartScreen
import pyperclip as pc
import hashlib
import crypto
import sv_ttk
from Popup import Popup

LARGEFONT = ("Courier", 20)
LARGEBOLDFONT = ('Courier bold', 20)
MEDIUMFONT = ("Courier", 16)
MEDIUMBOLDFONT = ('Courier bold', 16)
SMALLFONT = ("Courier", 14)


""" Creates and manages the Password View screen for the RasPassApp.
    Displays the stored password entries. Allows the user to access
    username and password with fingerprint authentification.

    Allows user to add/delete/change password entries with fingerprint
    authentification

    Option to view setting that displays how many more password entries can
    be stored and allows user to enroll/delete fingerprints.
"""


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

        # frame that acts as a root parent to all widgets on window
        content = ttk.Frame(self, padding=(3, 3, 12, 12))

        banner = ttk.Frame(content)
        body = ttk.Frame(content, borderwidth=5)
        btnFrame = tk.Frame(content, width=40)

        column_names = ttk.Frame(body)
        rows = ttk.Frame(body)
        self.rows = rows

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

    def onShowFrame(self):
        """ Event handler for show frame. Initializes the password entry rows
            along with the input row to add a new entry
        """
        if not self.addedRows:
            self.init_password_rows()
            self.init_input_row()
            self.addedRows = True
        else:
            # unfocus input row so input prompts appear again
            self.remember_input_row()

    def switch_to_start(self, controller):
        """ Switches back to the start screen, clearing any text that may
            still be in the input row
        """
        self.clear_input_row()
        controller.show_frame(StartScreen.StartScreen)

    def open_img(self, parent, dim, picture):
        """ Opens and displays header image for password view """
        img = Image.open(picture)
        img = img.resize((dim[0], dim[1]), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        panel = ttk.Label(parent, image=img)
        panel.image = img
        return panel

    def remember_input_row(self):
        """ Adds the site, username, password, and add entries for the input
            row back to the grid. Unfocuses them so prompts appear in entries.
        """
        rows = 100
        self.site_entry.grid(column=0, row=rows, sticky="new")
        self.username_entry.grid(column=1, row=rows, sticky="new")
        self.password_entry.grid(column=2, row=rows, sticky="new")
        self.add_new_pswd.grid(column=3, row=rows, sticky="new", columnspan=2)

        self.unfocus_entry(self.site_entry, 'Sitename')
        self.unfocus_entry(self.username_entry, 'Username')
        self.unfocus_entry(self.password_entry, 'Password')

    def forget_input_row(self):
        """ Forces the grid to forget/remove the input row """
        self.username_entry.grid_forget()
        self.site_entry.grid_forget()
        self.password_entry.grid_forget()
        self.add_new_pswd.grid_forget()

    def clear_input_row(self):
        """ Clears the text from the input row """
        self.username_entry.delete(0, 'end')
        self.site_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')

    def add_row(self, site):
        """ Adds a new password entry row to the grid """
        _, rows = self.rows.grid_size()

        # container for the elements in the password row so they can
        # easily be deleted later
        items = []

        s = tk.Entry(self.rows, width=20, font=("Courier bold", 14))
        u = ttk.Button(self.rows, width=20, text="Get Info", style='Style.TButton',
                       command=lambda: self.getInfo(site))
        c = ttk.Button(self.rows, width=20, text="Change", style='Style.TButton',
                       command=lambda: self.changePswdUsr(site))
        d = ttk.Button(self.rows, text="Delete", width=16, style='Style.TButton',
                       command=lambda: self.confirmDel(items, self.rows, rows, site, None))

        items.append(s)
        items.append(u)
        items.append(c)
        items.append(d)

        s.grid(row=rows, column=0, sticky="nesw")
        s.insert(0, site)
        s.config(state="readonly")
        u.grid(row=rows, column=1, sticky="nesw")
        c.grid(row=rows, column=2, sticky="nesw")
        d.grid(row=rows, column=3, sticky="nesw")

    def init_input_row(self):
        """ Initialize the input row. Once user adds a new entry, input
            row is cleared so more entries may be added.
        """
        self.site_entry = tk.Entry(self.rows, fg='grey', font=SMALLFONT)
        self.username_entry = tk.Entry(self.rows, fg='grey', font=SMALLFONT)
        self.password_entry = tk.Entry(
            self.rows, show="*", fg='grey', font=SMALLFONT)

        # prompts for the user to know what each entry box is for
        self.site_entry.insert(0, 'Sitename')
        self.username_entry.insert(0, 'Username')
        self.password_entry.insert(0, 'Password')

        # when user is focused on a specific entry box, the prompt goes away
        # so they can fill in their own text
        self.site_entry.bind("<FocusIn>", lambda event: self.focus_entry(
            self.site_entry, 'Sitename'))
        self.username_entry.bind("<FocusIn>", lambda event: self.focus_entry(
            self.username_entry, 'Username'))
        self.password_entry.bind("<FocusIn>", lambda event: self.focus_entry(
            self.password_entry, 'Password'))

        # when unfocused, if entry still blank, re-adds prompt
        self.site_entry.bind("<FocusOut>", lambda event: self.unfocus_entry(
            self.site_entry, 'Sitename'))
        self.username_entry.bind("<FocusOut>", lambda event: self.unfocus_entry(
            self.username_entry, 'Username'))
        self.password_entry.bind("<FocusOut>", lambda event: self.unfocus_entry(
            self.password_entry, 'Password'))

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
        self.add_new_pswd.grid(column=3, row=rows, sticky="nesw")

    def focus_entry(self, entry, msg):
        """ Removes prompt from entry box """
        if entry.get() == msg:
            entry.delete(0, tk.END)
            entry.insert(0, '')
            entry.config(fg='black')

    def unfocus_entry(self, entry, msg):
        """ Adds prompt back to entry box """
        if entry.get() == '':
            entry.insert(0, msg)
            entry.config(fg='grey')

    def get_master_pw_hash(self):
        """ Returns the sha256 hash of the master password """
        m = hashlib.sha256()
        m.update(self.master_pw.get().encode('utf-8'))
        return m.digest()

    def init_password_rows(self):
        """ Initializes all the password rows from the data stored in the Pico
        """
        site_reply = self.comm.getAllSiteNames()
        if site_reply is not None and site_reply["status"] == self.comm.STATUS_SUCCESS:
            sitenames = site_reply["sitenames"]
            for i in range(len(sitenames)):
                self.add_row(sitenames[i])

    def addPassword(self, sitename, username, password):
        """ Adds a new password row to the grid once user has clicked the
            add button on the input row
        """

        # AES CBC encrypt both the username and password before sending to
        # be stored in pico
        cipher_pass = crypto.encrypt(password, self.get_master_pw_hash())
        cipher_usr = crypto.encrypt(username, self.get_master_pw_hash())

        resp = self.comm.addPassword(sitename, cipher_usr, cipher_pass)
        if resp is None:
            print("[ERR] Add password failed")
            return
        elif resp["status"] == self.comm.STATUS_API_OTHER_ERROR:
            print("[ERR] Password already exists in db")
            return
        elif resp["status"] != self.comm.STATUS_SUCCESS:
            print("[ERR] Unknown error while adding password. Status=",
                  resp["status"])
            return

        self.forget_input_row()
        self.add_row(sitename)
        self.clear_input_row()
        self.remember_input_row()

    def revealHideUsrPw(self, cipher_text, label, btn):
        """ Toggles the view of username or password in GetInfo popup """
        current_text = label.cget('text')
        if current_text == '*****':
            plain_text = crypto.decrypt(cipher_text, self.get_master_pw_hash())
            label.config(text=plain_text)
            btn.configure(text='Hide')
            print("[INFO] Revealed")
        else:
            label.config(text='*****')
            btn.configure(text='Reveal')
            print("[INFO] Hidden")
        return

    def copyField(self, window, pswd):
        """ Copies username or password to computer's clipboard """
        popup = Popup(window, "", "Copied!", color="green")
        pc.copy(pswd)
        popup.destroy(1)

    def getInfo(self, sitename):
        """ Creates popup where user can view and copy the username and
            password for a specific entry. Requires fingerprint
            authentification.
        """
        resp = self.comm.getPassword(sitename)

        if resp is None:
            print("[ERR] Get password failed")
            return
        elif resp["status"] == self.comm.STATUS_NOT_VERIFIED:
            print("[ERR] Too many attempts for biometrics")
            self.controller.show_frame(StartScreen.StartScreen)
            return
        elif resp["status"] != self.comm.STATUS_SUCCESS:
            print(
                "[ERR] Unknown error while getting username and password. Status=", resp["status"])
            return

        # decrypt password retrieved from Pico to display on App
        cipher_text = resp['password']
        plain_text_pw = crypto.decrypt(cipher_text, self.get_master_pw_hash())

        # decrpyt username retrieved from Pico to display on App
        cipher_uname = resp['username']
        plain_text_usr = crypto.decrypt(
            cipher_uname, self.get_master_pw_hash())

        # create popup
        top = tk.Toplevel(self)
        top.geometry("550x400")
        top.title("RasPass Site Entry Info")

        style = ttk.Style()
        style.configure('GetInfo.TButton', font=MEDIUMFONT)

        username = tk.Label(top, font=LARGEBOLDFONT, text="Username:")
        username.grid(column=0, row=0, padx=15, pady=10, sticky='nw')

        usernameWrapper = ttk.Frame(top)
        usernameWrapper.grid(column=0, row=3, padx=25, pady=25, sticky='nw')

        usernameLabel = ttk.Label(
            usernameWrapper, text='*****', font=MEDIUMFONT)
        usernameLabel.grid(column=0, row=0, padx=5, sticky='nw')
        usernameRevealBtn = ttk.Button(usernameWrapper, text="Reveal", style='GetInfo.TButton',
                                       command=lambda: self.revealHideUsrPw(cipher_uname, usernameLabel, usernameRevealBtn))
        usernameRevealBtn.grid(column=3, row=0, padx=5, sticky='nw')

        usernameGetBtn = ttk.Button(usernameWrapper, text="Copy", style='GetInfo.TButton',
                                    command=lambda: self.copyField(top, plain_text_usr))
        usernameGetBtn.grid(column=6, row=0, padx=5, sticky='nw')

        password = tk.Label(top, font=LARGEBOLDFONT, text="Password:")
        password.grid(column=0, row=6, padx=15, pady=10, sticky='nw')

        passwordWrapper = ttk.Frame(top)
        passwordWrapper.grid(column=0, row=9, padx=25, pady=25, sticky='nw')

        passwordLabel = ttk.Label(
            passwordWrapper, text='*****', font=MEDIUMFONT)
        passwordLabel.grid(column=0, row=0, padx=5, sticky='nw')
        passwordRevealBtn = ttk.Button(passwordWrapper, text="Reveal", style='GetInfo.TButton',
                                       command=lambda: self.revealHideUsrPw(cipher_text, passwordLabel, passwordRevealBtn))
        passwordRevealBtn.grid(column=3, row=0, padx=5, sticky='nw')

        passwordGetBtn = ttk.Button(passwordWrapper, text="Copy", style='GetInfo.TButton',
                                    command=lambda: self.copyField(top, plain_text_pw))
        passwordGetBtn.grid(column=6, row=0, padx=5, sticky='nw')

        rows = ttk.Frame(top)
        rows.grid(column=0, row=8, padx=25, pady=5, sticky='nw')

    def settingsPopup(self):
        """ Opens a popup to view how much storage is left and enroll/delete
            fingerprints
        """
        res = self.comm.getSettings()
        if res['status'] != self.comm.STATUS_SUCCESS:
            print("[ERR] Authentification failure")
            return

        # creates popup
        top = tk.Toplevel(self)
        top.title("RasPass Settings")

        # open image for settings header
        image = self.open_img(top, (400, 75), "./imgs/Settings.png")
        image.grid(column=0, row=0)

        settings = res['settings']
        fingerPrints = settings['fingerprints']
        passwordsAvail = settings['numPswdAvail']

        storageWrapper = tk.Frame(top, width=500, height=30)
        storageWrapper.grid(column=0, row=2, padx=25, pady=20, sticky='nw')
        storageWrapper.grid_propagate(False)

        storage = tk.Text(storageWrapper, font=LARGEFONT)
        storage.tag_configure("bold", font=MEDIUMBOLDFONT)
        storage.insert("end", "Storage Available: ", "bold")
        storage.insert("end", "%s password entries" % passwordsAvail)
        storage.config(state="disabled", borderwidth=0, highlightthickness=0)
        storage.grid(column=0, row=0, sticky='nw')

        style = ttk.Style()
        style.configure('Settings.TButton', font=MEDIUMFONT)

        # button to enroll new finger prints that can be used for
        # authentification
        enrollBtn = ttk.Button(top, text="Enroll New Fingerprint", style='Settings.TButton',
                               command=lambda: self.enrollFinger(top, enrollBtn))
        enrollBtn.grid(column=0, row=4, padx=25, pady=10, sticky='nw')

        # display all fingerprints currently registered
        regFingers = tk.Label(top, font=MEDIUMBOLDFONT,
                              text="Fingerprints registered:")
        regFingers.grid(column=0, row=6, padx=25, pady=10, sticky='nw')

        rows = ttk.Frame(top)
        rows.grid(column=0, row=8, padx=25, pady=5, sticky='nw')

        if len(fingerPrints) == 0:
            tk.Label(rows, text='No fingerprints registered',
                     fg='red', font=MEDIUMFONT).grid()
        for finger in fingerPrints:
            self.initFingerprintEntry(rows, fingerPrints[finger])

    def enrollFinger(self, parent, btn):
        """ Enroll a new fingerprint for authentification """
        btn.grid_forget()
        frame = tk.Frame(parent)
        frame.grid(column=0, row=4, padx=25, pady=10, sticky='nw')

        # prompt for fingerprint entry
        name = tk.Entry(frame, fg='grey', font=SMALLFONT)
        name.insert(0, "Fingerprint name")
        name.grid(column=0, row=0)

        name.bind("<FocusIn>", lambda event: self.focus_entry(
            name, 'Fingerprint name'))

        submit = ttk.Button(frame, width=8, text="submit", style='Style.TButton',
                            command=lambda: self.enrollEvent(name.get(), parent))
        submit.grid(column=1, row=0)

    def enrollEvent(self, name, parent):
        """ Enrolls new fingerprint. Opens popup that indicates if enrollment
            was a success or needs to be tried again
        """
        success = self.comm.enrollFingerprint(name)
        if not success:
            p = Popup(parent, "Error",
                      "Enrollment failed, please try again", "red")
            p.destroy(2)

    def initFingerprintEntry(self, rows, name):
        """ Initialize a row for a stored fingerprint """
        _, rownum = rows.grid_size()
        items = []

        entry = tk.Entry(rows,  width=20, font=("Courier bold", 14))
        delete = ttk.Button(rows, width=20, text="Delete", style='Style.TButton',
                            command=lambda: self.confirmDel(items, rows, rownum, None, entry.get()))

        items.append(entry)
        items.append(delete)

        entry.insert(0, name)
        # all fingerprint names are readonly
        entry.config(state="readonly")

        entry.grid(row=rownum, column=0, pady=3, sticky="nesw")
        delete.grid(row=rownum, column=1, pady=3, sticky="nesw")

    def deleteFingerprint(self, fpName, confirmFrame, items):
        """ Delete a previously enrolled fingerprint """
        self.comm.deleteFingerprint(fpName)

        confirmFrame.destroy()
        for i in items:
            i.destroy()

        return True

    def changePswdUsr(self, sitename):
        """ Open a dialog to be able to change the username or password for
            a specific site entry. Sitename cannot be changed.
        """
        # Open popup
        top = tk.Toplevel(self)
        top.title("Update %s info" % sitename)
        site = ttk.Label(top, text="Update info for %s" %
                         sitename, font=LARGEFONT)
        site.grid(column=0, row=0, padx=25, pady=15)

        usrbtn = ttk.Button(
            top, width=15, text="Change Username", style='Style.TButton',)
        usrbtn.grid(column=0, row=2, padx=25)
        usrbtn['command'] = lambda: self.changeField(top, usrbtn, 2, sitename)

        pswdbtn = ttk.Button(
            top, width=15, text="Change Password", style='Style.TButton',)
        pswdbtn.grid(column=0, row=4, padx=25)
        pswdbtn['command'] = lambda: self.changeField(
            top, pswdbtn, 4, sitename)
        ttk.Button(top, width=10, text="Cancel", style='Style.TButton',
                   command=lambda: top.destroy()).grid(column=0, row=6, padx=25, pady=15)

    def changeField(self, popup, btn, rw, site):
        """ Reveals entry box to change either username or password """
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
        """ Responsible for actually updating the changed username or password
            in the Pico database
        """
        new = change.get().strip()
        resp = None
        if field == "usr":
            cipher_usr = crypto.encrypt(new, self.get_master_pw_hash())
            resp = self.comm.changeUsername(site, cipher_usr)
        else:
            cipher_pass = crypto.encrypt(new, self.get_master_pw_hash())
            resp = self.comm.changePassword(site, cipher_pass)

        if resp is None:
            print("[ERR] Change %s failed" % field)
            return False
        elif resp["status"] == self.comm.STATUS_FAILED_BIOMETRICS:
            print("[ERR] %s" % resp["error"])
            return False
        elif resp["status"] != self.comm.STATUS_SUCCESS:
            print("[ERR] Unknown error while removing password. Status=",
                  resp["status"])
            return False
        popup.destroy()

    def confirmDel(self, items, rows, row, sitename: None, fpName: None):
        """ Second confirmation when user clicks a delete button to prevent
            accidental deleting
        """
        items[-1].grid_forget()
        confirmFrame = tk.Frame(rows, width=16)
        confirmFrame.grid(row=row, column=3, sticky="nesw")
        if sitename is None:
            confirm = ttk.Button(confirmFrame, width=7, text="Confirm", style='Style.TButton',
                                 command=lambda: self.deleteFingerprint(fpName,  confirmFrame, items))
        else:
            confirm = ttk.Button(confirmFrame, width=7, text="Confirm", style='Style.TButton',
                                 command=lambda: self.deletePassword(sitename, confirmFrame, items))
        confirm.grid(row=0, column=0, sticky="nesw")
        cancel = ttk.Button(confirmFrame, width=7, text="Cancel", style='Style.TButton',
                            command=lambda: self.revertDel(items, confirmFrame, row))
        cancel.grid(row=0, column=1, sticky="nesw")

    def revertDel(self, items, confirm, row):
        """ Cancels the delete and returns back to normal row view """
        items[-1].grid(row=row, column=3, sticky="nesw")
        confirm.destroy()

    def deletePassword(self, sitename, confirmFrame, items):
        """ Delete a password row entry from the app and Pico database.
            Requires fingerprint authentification
        """

        resp = self.comm.removePassword(sitename)

        if resp is None:
            print("[ERR] Remove password failed")
            return False
        elif resp["status"] == self.comm.STATUS_NOT_VERIFIED:
            print("[ERR] Too many attempts for biometrics")
            self.controller.show_frame(StartScreen.StartScreen)
            return False
        elif resp["status"] != self.comm.STATUS_SUCCESS:
            print("[ERR] Unknown error while removing password. Status=",
                  resp["status"])
            return False

        confirmFrame.destroy()
        for i in items:
            i.destroy()

        return True
