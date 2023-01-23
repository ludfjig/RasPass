import time
from machine import Pin
import sys

led = Pin(25, machine.Pin.OUT)

# to make it clear whether the pico is loaded
for i in range(5):
    led.toggle()
    time.sleep(1)

while True:
    
    # read a command from the host
    v = sys.stdin.readline().strip()

    # perform the requested action
    if v.lower() == "toggle":
        led.toggle()