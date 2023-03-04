import serial
from serial.tools import list_ports
import re
import json
import time
import sys
import base64

# setting path
sys.path.append('../')
from Communication import CommunicationInterface

FRAMESTART = b"\xff"
FRAMESTOP = b"\xfe"

class AppComm(CommunicationInterface):
    def __init__(self):
        self.s = None
        port = list_ports.comports()
        for p in port:
            if (p.vid == 11914):
                device = p.device
                print("[INFO] Found device %s" %p)
                try:
                    try:
                        self.s = serial.Serial(device, timeout=5)
                    except serial.SerialException:
                        # for some reason when I do list_ports.comports on my mac it always
                        # gives me "/dev/cu.usbmodem101" instead of "/dev/tty.usbmodem101"
                        # so this is just forcing it to use tty for my computer if connecting
                        # over cu fails
                        device = re.sub(r'/cu', r'/tty', device)
                        self.s = serial.Serial(device, 9600, timeout=5)
                except:
                    self.s = None
                break

        if self.s is None:
            exit('[ERR]  Failure establishing connection to Pico')
        self.s.write(5*(FRAMESTART+b"hi"+FRAMESTOP))

    def writeRequest(self, req: dict) -> int:
        # will create correct json format to send later
        # right now just trying to set up basic framework
        try:
            # should return number of bytes written
            jstr = json.dumps(req)
            encoded = FRAMESTART + jstr.encode('utf-8') + FRAMESTOP
            print("[INFO] Sending JSON request %s" %jstr)
            size = self.s.write(encoded)
            self.s.flush()
            return (size == len(encoded))
        except serial.SerialTimeoutException:
            # timed out, something went wrong, return -1 to indicate error
            return False

    # expects a json response from pico
    def readResponse(self) -> dict | None:
        # while there is a next line to read from pico, read data
        # failure on error reading
        # structure back to python object from json
        # return object to caller
        try:
            raw = bytearray()
            while FRAMESTOP not in raw:
                b = self.s.read(1)
                if not b:
                    return None
                raw.extend(b)
            if FRAMESTART not in raw:
                self.s.reset_input_buffer()
                return None
            else:
                decoded = raw[raw.index(FRAMESTART)+len(FRAMESTART):raw.index(FRAMESTOP)].decode('utf-8')
                decoded = json.loads(decoded)
                print("[INFO] JSON received:", decoded)
                return decoded
        except:
            return None

    def communicateReq(self, req) -> dict | None:
        """ Communicate with the Pico by sending the request.
        Wait until a timeout and resend if no response from the Pico."""
        TOTAL_ATTEMPTS = 5
        for i in range(1,TOTAL_ATTEMPTS+1):
            if self.writeRequest(req):
                resp = self.readResponse()
                if resp is not None:
                    return resp
            print("[WARN] Failed to receive response from Pico. Retrying... (attempt %d of %d)" %(i, TOTAL_ATTEMPTS))
            time.sleep(0.5)
        exit("[ERR]  Failed to communicate with Pico")

    def getSerial(self):
        return self.s

    def verifyMasterHash(self, pass_hash: str) -> bool:
        req = {
            "method": "verifyMasterHash",
            "hash": pass_hash,
            "authtoken": "1"
        }
        res = self.communicateReq(req)

        """written = self.writeRequest(req)
        if not written:
            print("Failure to communicate with device\n")
            return False"""

        if res is None or "valid" not in res:
            print("[WARN] Failure to verify master password")
            return False
        return res["valid"]

    def getAllSiteNames(self):
        """Returns all site names stored in password manager"""
        req = {
            "method": "getAllSiteNames",
            "authtoken": "1"
        }

        res = self.communicateReq(req)

        if res is None:
            return {}

        return res

    def getPassword(self, sitename: str):
        """Returns username, password, or error on authentication failure/no entry"""
        # sanitize input
        print("[INFO] Get password request for sitename %s" %sitename)
        req = {
            "method": "getPassword",
            "sitename": sitename,
            "authtoken": "1"
        }

        res = self.communicateReq(req)

        if res is None:
            return {}

        # TODO: fix this
        auth_failure_count = 0
        while res != 0 and auth_failure_count < 5:
            auth_failure_count += 1
            print("Authentification failure, Attempt ", auth_failure_count, " of 5")
            if auth_failure_count < 5:
                print("Try again in 3 seconds")
                time.sleep(3)

        # send api command to reset otherwise they don't need to enter master password
        if auth_failure_count >= 5: 
            req = {
                "method": "softReset",
                "authtoken": "1"
            }
            written = self.writeRequest(req)

        return res

    def addPassword(self, sitename: str, user: str, pswd: str):
        """Adds a new username, password, site to the password manager. Returns success/failure"""
        print("[INFO] Add password for sitename %s" %sitename)
        req = {
            "method": "addPassword",
            "sitename": sitename,
            "username": user,
            "password": pswd,
            "authtoken": "1"
        }

        res = self.communicateReq(req)

        if res is None:
            return {}
        return res

    def changeUsername(self, site: str, user: str):
        """Changes the username for a stored site in the password manager. Returns success/failure"""
        req = {
            "method": "changeUsername",
            "sitename": site,
            "username": user,
            "authtoken": "1"
        }

        res = self.communicateReq(req)

        if res is None:
            return False

        # TODO: fix
        return True

    def changePassword(self, site: str, pswd: str):
        """Changes the password for a stored site in the password manager. Returns success/failure"""
        req = {
            "method": "changePassword",
            "sitename": site,
            "password": pswd,
            "authtoken": "1"
        }

        res = self.communicateReq(req)

        if res is None:
            return False

        # TODO: fix
        return True

    def removePassword(self, site: str) -> int:
        """Deletes a site, username, password entry from the password manager. Returns success/failure"""
        req = {
            "method": "removePassword",
            "sitename": site,
            "authtoken": "1"
        }

        res = self.communicateReq(req)

        if res is None or "status" not in res:
            return False

        return res['status']

    def getSettings(self):
        """Returns all the current settings"""
        req = {
            "method": "getSettings",
            "authtoken": "1"
        }

        res = self.communicateReq(req)

        if res is None or "status" not in res:
            return {}

        return res

    def setSettings(self, settings: str):
        """Sets a setting in the password manager. Returns success/failure"""
        req = {
            "method": "setSettings",
            "settings": settings,
            "authtoken": "1"
        }

        res = self.communicateReq(req)

        if res is None or "status" not in res:
            return False

        return True
