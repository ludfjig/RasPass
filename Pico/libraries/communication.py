import sys
import json
import localdb
import auth
import uselect
import time
import io

# Delimit byte frames with byte stuffing
# Data is encoded utf-8
# Since 0xfe and 0xff are not used in utf-8, these delimit a frame
FRAMESTART = b"\xff"
FRAMESTOP = b"\xfe"

class PicoComm:
    """ Communication interface on Pico via USB """
    def __init__(self, db: localdb.DataBase, auth: auth.Auth):
        self.db = db
        self.auth = auth
        self.inpoll = uselect.poll()
        self.inpoll.register(sys.stdin, uselect.POLLIN)
        self.rawbuf = bytearray()

    def writeResponse(self, resp: dict) -> int:
        """ Send response to app """
        res = json.dumps(resp).encode('utf-8')
        sys.stdout.buffer.write(FRAMESTART + res + FRAMESTOP)
        return 0

    def readRequest(self) -> dict | None:
        """ Receieve a request from the app. Blocking call.
        Returns request or None on error. """
        while FRAMESTOP not in self.rawbuf:
            if not self.inpoll.poll(0):
                time.sleep(0.5)
                return None
            else:
                self.rawbuf.extend(sys.stdin.buffer.read(1))

        stopi = self.rawbuf.index(FRAMESTOP)
        if FRAMESTART not in self.rawbuf:
            self.rawbuf = self.rawbuf[stopi+len(FRAMESTOP):] # delete malformed packet
            #print("cleared buf. curr: ", self.rawbuf)
            return None # Invalid packet

        starti = self.rawbuf.index(FRAMESTART)
        rawPkt = self.rawbuf[starti+len(FRAMESTART):stopi]
        self.rawbuf = self.rawbuf[stopi+len(FRAMESTOP):] # Crop out packet
        #print("raw pkt: ", rawPkt)
        #print("raw buf: ", self.rawbuf)
        try:
            decoded = json.loads(rawPkt.decode('utf-8'))
            #print("json: ", decoded)
            return decoded
        except:
            return None

    def processRequest(self, req) -> bool:
        """ Process a request, sending a response to the device. Returns true
        if req was successfully processed, and false otherwise. """
        if "method" in req:
            method = req["method"]
            try:
                handler = getattr(PicoComm, method)
                resp = handler(self, req)
                if resp is None:
                    return False
                self.writeResponse(resp)
            except Exception as e:
                errMsg = {}
                errMsg["method"] = req["method"]
                errMsg["status"] = 100
                with io.StringIO() as f:
                    sys.print_exception(e, f)
                    f.seek(0)
                    errMsg["error"] = f.read()
                self.writeResponse(errMsg)
            return True
        return False


    def getAllSiteNames(self, req: dict) -> dict | None:
        """Returns all site names stored in password manager"""
        return {
            "method": "getAllSiteNames",
            "status": 0,
            "error": None,
            "sitenames": self.db.getAllSites()
        }

    def getPassword(self, req: dict) -> dict | None:
        """Returns username, password, or error on authentication
        failure/no entry"""
        if not self.auth.authenticate():
            return {
                "method": "getPassword",
                "status": 1 if self.auth.isVerified else 5,
                "error": "Failed biometric authentication"
            }
        elif "sitename" not in req:
            return {
                "method": "getPassword",
                "status": 2,
                "error": "No sitename"
            }
        else:
            up = self.db.get(req["sitename"])
            if up is not None:
                return {
                    "method": "getPassword",
                    "status": 0,
                    "error": None,
                    "sitename": req["sitename"],
                    "username": up[0],
                    "password": up[1]
                }
            else:
                return {
                    "method": "getPassword",
                    "status": 3,
                    "error": "Sitename not known"
                }

    def addPassword(self, req: dict) -> dict | None:
        """Adds a new username, password, site to the password manager.
        Returns success/failure"""
        if not self.auth.authenticate():
            res = {
                "method": "addPassword",
                "status": 1 if self.auth.isVerified else 5,
                "error": "Failed biometric authentication"
            }
            return res
        elif "sitename" not in req:
            return {
                "method": "addPassword",
                "status": 2,
                "error": "No sitename"
            }
        elif "username" not in req:
            return {
                "method": "addPassword",
                "status": 3,
                "error": "No username"
            }
        elif "password" not in req:
            return {
                "method": "addPassword",
                "status": 4,
                "error": "No password"
            }
        else:
            if self.db.add(
                    req["sitename"], req["username"], req["password"]) == 0:
                res = {
                    "method": "addPassword",
                    "status": 0,
                    "error": None
                }
                return res
            else:
                return {
                    "method": "addPassword",
                    "status": 5,
                    "error": "Failed to add password (sitename already exists)"
                }

    def changeUsername(self, req: dict) -> dict | None:
        """Changes the username for a stored site in the password manager.
        Returns success/failure"""
        if not self.auth.authenticate():
            return {
                "method": "changeUsername",
                "status": 1 if self.auth.isVerified else 5,
                "error": "Failed biometric authentication"
            }
        elif "sitename" not in req:
            return {
                "method": "changeUsername",
                "status": 2,
                "error": "No sitename"
            }
        elif "newusername" not in req:
            return {
                "method": "changeUsername",
                "status": 3,
                "error": "No newusername"
            }
        else:
            if self.db.update(req["sitename"], req["newusername"], None) == 0:
                return {
                    "method": "changeUsername",
                    "status": 0,
                    "error": None
                }
            else:
                return {
                    "method": "changeUsername",
                    "status": 4,
                    "error": "Failed to change username (unknown error)"
                }

    def changePassword(self, req: dict) -> dict | None:
        """Changes the password for a stored site in the password manager.
        Returns success/failure"""
        if not self.auth.authenticate():
            return {
                "method": "changePassword",
                "status": 1 if self.auth.isVerified else 5,
                "error": "Failed biometric authentication"
            }
        elif "sitename" not in req:
            return {
                "method": "changePassword",
                "status": 2,
                "error": "No sitename"
            }
        elif "newpassword" not in req:
            return {
                "method": "changePassword",
                "status": 3,
                "error": "No newpassword"
            }
        else:
            if self.db.update(req["sitename"], None, req["newpassword"]) == 0:
                return {
                    "method": "changePassword",
                    "status": 0,
                    "error": None
                }
            else:
                return {
                    "method": "changePassword",
                    "status": 4,
                    "error": "Failed to change password (unknown error)"
                }

    def removePassword(self, req: dict) -> dict | None:
        """Deletes a site, username, password entry from the password manager.
        Returns success/failure"""
        if not self.auth.authenticate():
            return {
                "method": "removePassword",
                "status": 1 if self.auth.isVerified else 5,
                "error": "Failed biometric authentication"
            }
        elif "sitename" not in req:
            return {
                "method": "removePassword",
                "status": 2,
                "error": "No sitename"
            }
        else:
            if self.db.delete(req["sitename"]) == 0:
                return {
                    "method": "removePassword",
                    "status": 0,
                    "error": None
                }
            else:
                return {
                    "method": "removePassword",
                    "status": 3,
                    "error": "Failed to delete password (unknown error)"
                }

    def getSettings(self, req: dict) -> dict | None:
        """Returns all the current settings"""
        if not self.auth.authenticate():
            return {
                "method": "getSettings",
                "status": 1 if self.auth.isVerified else 5,
                "error": "Failed biometric authentication"
            }
        else:
            # TODO: implement settings
            return {
                "method": "getSettings",
                "status": 0,
                "error": None,
                "settings": {}
            }

    def setSettings(self, req: dict) -> dict | None:
        """Sets a setting in the password manager. Returns success/failure"""
        if not self.auth.authenticate():
            return {
                "method": "getSettings",
                "status": 1 if self.auth.isVerified else 5,
                "error": "Failed biometric authentication"
            }
        else:
            # TODO: implement settings
            return {
                "method": "setSettings",
                "status": 0,
                "error": None
            }

    def enrollFingerprint(self, req: dict) -> dict | None:
        """ TODO: @Audrey/Hafsa"""
        pass

    def deleteFingerprint(self, req: dict) -> dict | None:
        """ TODO: @Audrey/Hafsa """
        pass

    def verifyFingerprint(self, req: dict) -> dict | None:
        """Verifies a fingerprint on the sensor that is enrolled is valid.
        If the fpId field is defined in req, will search for that fingerprint."""
        fpId = None
        if "fpId" in req and req["fpId"] > 0 and req["fpId"] < 127:
            fpId = req["fpId"]
        res = self.auth.verifyFingerprint()
        if res is not None:
            return {
                "method": "verifyFpPswd",
                "status": 0,
                "fpId": res[0],
                "fpHash": res[1],
                "error": None
            }
        else:
            return {
                "method": "verifyFpPswd",
                "status": 1,
                "error": "Failed to find user fingerprint after 3 tries"
            }

    def verifyFingerprintPswd(self, req: dict) -> dict | None:
        """Verifies the fingerprint password from 4 byte code"""
        if "authtoken" not in req:
            return {
                "method": "verifyFpPswd",
                "status": 1,
                "error": "No auth token"
            }
        else:
            if self.auth.setupFp(req["authtoken"]):
                return {
                    "method": "verifyFpPswd",
                    "status": 0,
                    "error": None
                }
            else:
                return {
                    "method": "verifyFpPswd",
                    "status": 2,
                    "error": "Failed to authenticate password"
                }

    def verifyMasterHash(self, req: dict) -> dict | None:
        if "hash" not in req or len(req["hash"]) != 4:
            return  {
                "method": "verifyMasterHash",
                "status": 4,
                "valid": False,
                "error": "No hash supplied, or hash incorrect length"
            }
        hashBytes = tuple(req["hash"].encode('utf-8'))
        if self.auth.isDefaultPswd:
            if not self.auth.changePswd(self.auth.DEFAULT_PSWD, hashBytes):
                return {
                    "method": "verifyMasterHash",
                    "status": 3,
                    "valid": False,
                    "error": "Failed to set new master password from default"
                }
        valid = self.auth.setupFp(hashBytes)
        return {
                "method": "verifyMasterHash",
                "status": 0,
                "valid": valid,
                "error": None
        }

    def changeMasterPswd(self, req: dict) -> dict | None:
        """Change the code for the fingerprint sensor"""
        if "oldauthtoken" not in req or "newauthtoken" not in req:
            return {
                "method": "changeMasterPswd",
                "status": 1,
                "error": "No new/old auth token"
            }
        else:
            if self.auth.changePswd(tuple(req["oldauthtoken"]), tuple(req["newauthtoken"])):
                return {
                    "method": "changeMasterPswd",
                    "status": 0,
                    "error": None
                }
            else:
                return {
                    "method": "changeMasterPswd",
                    "status": 2,
                    "error": "Failed to validate old authtoken"
                }
