import sys
from machine import Pin
import time

sys.path.append('/libraries')

from libraries.communication import PicoComm  # noqa: E402
from libraries.auth import Auth  # noqa: E402
from libraries.crypto import Crypto   # noqa: E402
from libraries.flashrw import FlashRW  # noqa: E402
from libraries.localdb import DataBase  # noqa: E402


led = Pin(25, Pin.OUT)

# to make it clear whether the pico is loaded
for i in range(5):
    led.on()
    time.sleep(0.2)
    led.off()
    time.sleep(0.2)

frw = FlashRW()
cr = Crypto()
database = DataBase(frw, cr)
fp = Auth()
comms = PicoComm(database, fp)

while True:
    # read a command from the host
    req = comms.readRequest()
    if req is not None:
        led.on()
        # time.sleep(1.25)
        # time.sleep(1.25)
        comms.processRequest(req)
        led.off()
    # if req != None:
    #    if "toggle" in req and req["toggle"] == 1:
    #        led.on()
    #    elif "toggle" in req and req["toggle"] == 0:
    #        led.off()
    #    else:
    #        led.on()
    #        time.sleep(1.25)
    #        led.off()
    #        time.sleep(1.25)
    #        comms.processRequest(req)
