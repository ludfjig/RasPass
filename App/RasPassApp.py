import serial
from serial.tools import list_ports
import time
import re

import tkinter as tk
from tkinter import ttk


class RasPassApp():
    def __init__(self, root, serial):
        self.s = serial
        content = ttk.Frame(root, padding=(3, 3, 12, 12))

        banner = ttk.Frame(content, borderwidth=5, relief="solid")
        body = ttk.Frame(content, borderwidth=5, relief="solid")

        column_names = ttk.Frame(body, borderwidth=5, relief="solid")
        rows = ttk.Frame(body, borderwidth=5, relief="solid")
        new_button = ttk.Button(body, text="Add new password (Toggle LED for now)", command=self.toggle_led)

        # column names
        site_label = ttk.Label(column_names, text="Site")
        username_label = ttk.Label(
            column_names, text="Username")
        password_label = ttk.Label(
            column_names, text="Password")

        # actual entries / rows
        s1 = ttk.Entry(rows)
        u1 = ttk.Entry(rows)
        p1 = ttk.Entry(rows)

        # add sanitation of user input

        g1 = ttk.Button(rows, text="Copy PW", command=None)
        c1 = ttk.Button(rows, text="Change", command=None)

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
        s1.grid(column=0, row=0, sticky="new")
        u1.grid(column=1, row=0, sticky="new")
        p1.grid(column=2, row=0, sticky="new")
        g1.grid(column=3, row=0, sticky="new")
        c1.grid(column=4, row=0, sticky="new")

        # new password button
        new_button.grid(column=0, row=2, sticky="new")

        # ----------  fill   starts here ---------------------------
        root.columnconfigure(0, weight=1)
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

    def toggle_led(self):
        self.s.write(b"toggle\n")


def main():
    root = tk.Tk()
    root.title("RasPass Password Manager")

    s = None
    port = list_ports.comports()
    for p in port:
        info = p.vid
        if (p.vid == 11914):
            print(p.vid)
            device = p.device
            try:
                s = serial.Serial(device)
            except serial.SerialException:
                # for some reason when I do list_ports.comports on my mac it always
                # gives me "/dev/cu.usbmodem101" instead of "/dev/tty.usbmodem101"
                # so this is just forcing it to use tty for my computer if connecting
                # over cu fails
                device = re.sub(r'/cu', r'/tty', device)
                s = serial.Serial(device)
            break

    rasPassApp = RasPassApp(root, s)

    root.mainloop()


if __name__ == "__main__":
    main()
