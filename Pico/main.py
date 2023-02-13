import sys
from machine import Pin, UART
import time

sys.path.append("/libraries")

from libraries.communication import PicoComm  # noqa: E402
from libraries.auth import Auth  # noqa: E402
from libraries.crypto import Crypto  # noqa: E402
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

# On-board LED
led = Pin(25, Pin.OUT)

# Boot status of Pico
for i in range(5):
    led.on()
    time.sleep(0.2)
    led.off()
    time.sleep(0.2)

# Initialize fingerprint sensor
finger = af.Adafruit_Fingerprint(uart)
time.sleep(0.25)


# Initialize libraries
frw = FlashRW()
cr = Crypto()
database = DataBase(frw, cr)
fp = Auth(finger)
comms = PicoComm(database, fp)

"""
########################### Note to analysis team
# This section is used to experiment with the fingerprint sensor directly using
# an Adafruit-provided user interface via the CLI for the sensor

# Fingerprint module temp password
FP_PSWD = (1, 2, 3, 4)
CHANGED_PSWD = False

# change password
if False:
    print("Set password", finger.set_password(FP_PSWD))

# setup sensor
#finger.initialize(FP_PSWD if CHANGED_PSWD else (0, 0, 0, 0))
print("Setup:",fp.setupFp((0,0,0,0)))
time.sleep(0.25)
while True:
    fpval = fp.verifyFingerprint()
    if fpval is not None:
        print("Authenticated for fingerprint id", fpval[0])
    time.sleep(1)
#print("Change password:", fp.changePswd((0,0,0,0),(0,0,0,0)))

# enter main loop
#fp.main_loop(finger)
"""

while True:
    req = comms.readRequest()
    if req is not None:
        led.on()
        comms.processRequest(req)
        led.off()