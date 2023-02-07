import time
from machine import Pin
import sys
sys.path.append('/libraries')

from libraries.communication import PicoComm
from libraries.auth import Auth
from libraries.crypto import Crypto
from libraries.flashrw import FlashRW
from libraries.localdb import DataBase

led = Pin(25, machine.Pin.OUT)

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
    if req != None:
        led.on()
        #time.sleep(1.25)
        #time.sleep(1.25)
        comms.processRequest(req)
        led.off()
    #if req != None:
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

