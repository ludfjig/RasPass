import sys
from machine import Pin, UART
import time
sys.path.append('/libraries')
from libraries.communication import PicoComm  # noqa: E402
from libraries.auth import Auth  # noqa: E402
from libraries.crypto import Crypto   # noqa: E402
from libraries.flashrw import FlashRW  # noqa: E402
from libraries.localdb import DataBase  # noqa: E402
from libraries.adafruit_fingerprint import Adafruit_Fingerprint  # noqa: E402


# yellow = Sensor TX
# white = Sensor RX

time.sleep(4)
uart = UART(1, 57600, parity=None, stop=1, tx=Pin(4), rx=Pin(5))
uart.init(timeout=5000, baudrate=57600, bits=8, stop=1, parity=None)#, txbuf=12, rxbuf=12)
time.sleep(1)
print("Write", uart.write(b"\xef\x01\xff\xff\xff\xff\x01\x00\x04\x17\x00\x00\x1c"))
uart.flush()
print(uart.any())
l = 0
recvd = b""
recvd += uart.read(12-len(recvd))
print("Read", recvd)
time.sleep(1)
print("Write", uart.write(b"\xef\x01\xff\xff\xff\xff\x01\x00\x03\x0f\x00\x13"))
uart.flush()
print(uart.any())
l = 0
recvd = b""
recvd += uart.read(13-len(recvd))
print("Read", recvd)
finger = Adafruit_Fingerprint(uart)

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
fp = Auth(finger)
comms = PicoComm(database, fp)

print("hi")
fp.main_loop(finger)

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
