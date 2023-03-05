import serial
from serial.tools import list_ports
import re
import json
import time
import sys
import base64


class AppComm:
    FRAMESTART: bytes = b"\xff"
    FRAMESTOP: bytes = b"\xfe"
    TOTAL_ATTEMPTS: int = 5        # Number of ARQ attempts before fatal error
    STATUS_SUCCESS = 0
    STATUS_MISSING_PARAM = 3        # Missing request parameter
    STATUS_MALFORMED_REQ = 4        # Malformed request
    STATUS_BAD_METHOD = 5           # Bad/nonexistent method
    STATUS_FAILED_BIOMETRICS = 6    # Failed biometric, but not too many attempts
    STATUS_NOT_VERIFIED = 7         # User must run verifyMasterHash
    # Other (unhandled) exception thrown in code - traceback returned
    STATUS_UNKNOWN_ERR = 10
    STATUS_API_OTHER_ERROR = 11     # Other (handled) error in the API
    STATUS_NOT_YET_IMPLEMENTED = 12  # API method exists, but not implemented

    def __init__(self):
        self.s = None
        port = list_ports.comports()
        for p in port:
            if (p.vid == 11914):
                device = p.device
                print("[INFO] Found device %s" % p)
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
        self.s.write(5*(b"none"+self.FRAMESTOP))

    def writeRequest(self, req: dict) -> int:
        # will create correct json format to send later
        # right now just trying to set up basic framework

        # first, dump out anything in the input buffer
        self.s.reset_input_buffer()

        try:
            # should return number of bytes written
            jstr = json.dumps(req)
            encoded = self.FRAMESTART + jstr.encode('utf-8') + self.FRAMESTOP
            print("[INFO] Sending JSON request %s" % jstr)
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
            while self.FRAMESTOP not in raw:
                b = self.s.read(1)
                if not b:
                    return None
                raw.extend(b)
            if self.FRAMESTART not in raw:
                self.s.reset_input_buffer()
                return None
            else:
                decoded = raw[raw.index(
                    self.FRAMESTART)+len(self.FRAMESTART):raw.index(self.FRAMESTOP)].decode('utf-8')
                decoded = json.loads(decoded)
                print("[INFO] JSON received:", decoded)
                return decoded
        except:
            return None

    def communicateReq(self, req) -> dict | None:
        """ Communicate with the Pico by sending the request.
        Wait until a timeout and resend if no response from the Pico."""
        for i in range(1, self.TOTAL_ATTEMPTS+1):
            if self.writeRequest(req):
                resp = self.readResponse()
                if resp is not None:
                    return resp
            print("[WARN] Failed to receive response from Pico. Retrying... (attempt %d of %d)" % (
                i, self.TOTAL_ATTEMPTS))
            time.sleep(0.5)
        exit("[ERR] Failed to communicate with Pico")

    def communicateAuthenticatedReq(self, req) -> dict | None:
        """ Communicate with Pico by sending this request that needs fingerprint authentication.
        Will retry until device locks or success. Returns response or None on failure. """
        # TODO: show popup that says to put finger on sensor when light turns green
        while True:
            res = self.communicateReq(req)
            if res is None:
                break

            status = res["status"]
            if status == self.STATUS_SUCCESS:
                return res
            elif status == self.STATUS_FAILED_BIOMETRICS:
                # TODO: show popup that says to retry
                pass
            elif status == self.STATUS_NOT_VERIFIED:
                # TODO: Show popup that says too many attempts, and return to homescreen (device will lock itself)
                return res
            else:
                # Not an authentication issue, so just return it
                return res
        return None

    def getSerial(self):
        return self.s

    def verifyMasterHash(self, pass_hash: str) -> dict | None:
        """Verify the master password hash. Returns response or None on failure"""
        assert len(pass_hash) == 4

        req = {
            "method": "verifyMasterHash",
            "hash": pass_hash,
            "authtoken": "1"
        }
        res = self.communicateReq(req)

        if res is None or "valid" not in res:
            print("`[WARN] Failure to verify master password")

        return res

    def getAllSiteNames(self) -> dict | None:
        """Get all sitenames. Returns response or None on failure"""
        req = {
            "method": "getAllSiteNames",
            "authtoken": "1"
        }

        return self.communicateReq(req)

    def getPassword(self, sitename: str) -> dict | None:
        """Get the username,password. Returns response or None on failure"""
        # sanitize input
        print("[INFO] Get password request for sitename %s" % sitename)
        req = {
            "method": "getPassword",
            "sitename": sitename,
            "authtoken": "1"
        }

        return self.communicateAuthenticatedReq(req)

    def addPassword(self, sitename: str, user: str, pswd: str) -> dict | None:
        """Adds a new username, password, site to the password manager. Returns response or None on failure"""
        print("[INFO] Add password for sitename %s" % sitename)
        req = {
            "method": "addPassword",
            "sitename": sitename,
            "username": user,
            "password": pswd,
            "authtoken": "1"
        }

        return self.communicateAuthenticatedReq(req)

    def changeUsername(self, site: str, user: str) -> dict | None:
        """Changes the username for a stored site in the password manager. Returns response or None on failure"""
        req = {
            "method": "changeUsername",
            "sitename": site,
            "username": user,
            "authtoken": "1"
        }

        return self.communicateAuthenticatedReq(req)

    def changePassword(self, site: str, pswd: str) -> dict | None:
        """Changes the password for a stored site in the password manager. Returns response or None on failure"""
        req = {
            "method": "changePassword",
            "sitename": site,
            "password": pswd,
            "authtoken": "1"
        }

        return self.communicateAuthenticatedReq(req)

    def removePassword(self, site: str) -> dict | None:
        """Deletes a site, username, password entry from the password manager. Returns response or None on failure"""
        req = {
            "method": "removePassword",
            "sitename": site,
            "authtoken": "1"
        }

        return self.communicateAuthenticatedReq(req)

    def getSettings(self) -> dict | None:
        """Returns all the current settings"""
        req = {
            "method": "getSettings",
            "authtoken": "1"
        }

        return self.communicateAuthenticatedReq(req)

    def setSettings(self, settings: str) -> dict | None:
        """Sets a setting in the password manager. Returns response or None on failure"""
        req = {
            "method": "setSettings",
            "settings": settings,
            "authtoken": "1"
        }

        return self.communicateAuthenticatedReq(req)
