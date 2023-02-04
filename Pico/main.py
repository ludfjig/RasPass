import time
from machine import Pin

import json

import sys
sys.path.append("/libraries")

import PicoComm

led = Pin(25, machine.Pin.OUT)

# to make it clear whether the pico is loaded
for i in range(5):
    led.on()
    time.sleep(0.2)
    led.off()
    time.sleep(0.2)

comms = PicoComm.PicoComm()

while True:
    # read a command from the host
    res = comms.readRequest()
    if res != None:
        if res["toggle"] == 1:
            led.on()
        else:
            led.off()
    else:
        # Show some error condition
        led.on()
        time.sleep(0.25)
        led.off()
        time.sleep(0.25)
