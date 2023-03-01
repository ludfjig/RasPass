# Main program for RasPass on Pico
# Runs setup and handles requests
# Copyright (c), 2023  RasPass

import sys
from machine import Pin, UART
import time

sys.path.append("/libraries")

from libraries.communication import PicoComm  # noqa: E402
from libraries.auth import Auth  # noqa: E402
from libraries.flashrw import FlashRW  # noqa: E402
from libraries.localdb import DataBase  # noqa: E402
import libraries.adafruit_fingerprint as af  # noqa: E402


# Fingerprint Sensor UART
# Wiring:
# yellow = Sensor TX -> Pico GPIO 5
# white = Sensor RX -> Pico GPIO 4
# red = Sensor VCC -> Pico 3V3
# black = Sensor GND -> Pico GND
uart = UART(1, 57600, parity=None, stop=1, tx=Pin(4), rx=Pin(5))
uart.init(timeout=5000)

# Initialize fingerprint sensor
finger = af.Adafruit_Fingerprint(uart)

# On-board LED
led = Pin(25, Pin.OUT)

# Boot status of Pico
for i in range(5):
    led.on()
    time.sleep(0.2)
    led.off()
    time.sleep(0.2)

# Initialize libraries
frw = FlashRW()
database = DataBase(frw)
fp = Auth(finger)
comms = PicoComm(database, fp)

'''
########################### Note to analysis team
# This section is used to experiment with the fingerprint sensor directly using
# an Adafruit-provided user interface via the CLI for the sensor

# set the master password hash to be null initially
database.master_hash = (4 * b"\x00")

# Use this to enroll and delete fingerprints

# Fingerprint module temp password
FP_PSWD = (0, 0, 0, 0)

# change password
if False:
    print("Change password:", fp.changePswd((0,0,0,0),(0,0,0,0)))


print("Setup sensor status:",fp.setupFp((0,0,0,0))) # this requires fingerprint to already be enrolled

# setup sensor
time.sleep(0.25)

fp.main_loop(finger)
'''

fp.setupFp((0,0,0,0))

while True:
    req = comms.readRequest()
    if req is not None:
        led.on()
        comms.processRequest(req)
        led.off()