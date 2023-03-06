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



class PicoComm:
    FRAMESTART = b"\xff"
    FRAMESTOP = b"\xfe"
    STATUS_SUCCESS = 0
    STATUS_MISSING_PARAM = 3        # Missing request parameter
    STATUS_MALFORMED_REQ = 4        # Malformed request
    STATUS_BAD_METHOD = 5           # Bad/nonexistent method
    STATUS_FAILED_BIOMETRICS = 6    # Failed biometric, but not too many attempts
    STATUS_NOT_VERIFIED = 7         # User must run verifyMasterHash
    STATUS_UNKNOWN_ERR = 10         # Other (unhandled) exception thrown in code - traceback returned
    STATUS_API_OTHER_ERROR = 11     # Other (handled) error in the API
    STATUS_NOT_YET_IMPLEMENTED = 12 # API method exists, but not implemented

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
        sys.stdout.buffer.write(self.FRAMESTART + res + self.FRAMESTOP)
        return 0

    def readRequest(self) -> dict | None:
        """ Receieve a request from the app. Blocking call.
        Returns request or None on error. """
        while self.FRAMESTOP not in self.rawbuf:
            if not self.inpoll.poll(0):
                time.sleep(0.5)
                return None
            else:
                self.rawbuf.extend(sys.stdin.buffer.read(1))

        stopi = self.rawbuf.index(self.FRAMESTOP)
        if self.FRAMESTART not in self.rawbuf:
            self.rawbuf = self.rawbuf[stopi+len(self.FRAMESTOP):] # delete malformed packet
            return None # Invalid packet

        starti = self.rawbuf.index(self.FRAMESTART)
        rawPkt = self.rawbuf[starti+len(self.FRAMESTART):stopi]
        self.rawbuf = self.rawbuf[stopi+len(self.FRAMESTOP):] # Crop out packet
        try:
            decoded = json.loads(rawPkt.decode('utf-8'))
            return decoded
        except:
            return None

    def processRequest(self, req) -> bool:
        """ Process a request, sending a response to the device. Returns true
        if req was successfully processed, and false otherwise. """
        try:
            method = req["method"] if "method" in req else "nomethod"
            handler = getattr(PicoComm, method)
            resp = handler(self, req)
            if resp is None:
                return False
            self.writeResponse(resp)
            return True
        except AttributeError:
            self.writeResponse({
                "method": req["method"],
                "status": self.STATUS_BAD_METHOD,
                "error": "Bad method"
            })
        except Exception as e:
            errMsg = {
                "method": req["method"],
                "status": self.STATUS_UNKNOWN_ERR
            }
            with io.StringIO() as f:
                sys.print_exception(e, f)
                f.seek(0)
                errMsg["error"] = f.read()
            self.writeResponse(errMsg)
        return False


    def getAllSiteNames(self, req: dict) -> dict | None:
        """Returns all site names stored in password manager"""
        return {
            "method": "getAllSiteNames",
            "status": self.STATUS_SUCCESS,
            "error": None,
            "sitenames": self.db.getAllSites()
        }

    def getPassword(self, req: dict) -> dict | None:
        """Returns username, password, or error on authentication
        failure/no entry"""
        if not self.auth.authenticate():
            return {
                "method": "getPassword",
                "status": self.STATUS_FAILED_BIOMETRICS if self.auth.isVerified else self.STATUS_NOT_VERIFIED,
                "error": "Authentication error"
            }
        elif "sitename" not in req:
            return {
                "method": "getPassword",
                "status": self.STATUS_MISSING_PARAM,
                "error": "No sitename"
            }
        else:
            up = self.db.get(req["sitename"])
            if up is not None:
                return {
                    "method": "getPassword",
                    "status": self.STATUS_SUCCESS,
                    "error": None,
                    "sitename": req["sitename"],
                    "username": up[0],
                    "password": up[1]
                }
            else:
                return {
                    "method": "getPassword",
                    "status": self.STATUS_API_OTHER_ERROR,
                    "error": "Sitename not known"
                }

    def addPassword(self, req: dict) -> dict | None:
        """Adds a new username, password, site to the password manager.
        Returns success/failure"""
        if not self.auth.authenticate():
            return {
                "method": "addPassword",
                "status": self.STATUS_FAILED_BIOMETRICS if self.auth.isVerified else self.STATUS_NOT_VERIFIED,
                "error": "Authentication error"
            }
        elif "sitename" not in req or "username" not in req or "password" not in req:
            return {
                "method": "addPassword",
                "status": self.STATUS_MISSING_PARAM,
                "error": "Missing parameter"
            }
        else:
            if self.db.add(
                    req["sitename"], req["username"], req["password"]) == 0:
                res = {
                    "method": "addPassword",
                    "status": self.STATUS_SUCCESS,
                    "error": None
                }
                return res
            else:
                return {
                    "method": "addPassword",
                    "status": self.STATUS_API_OTHER_ERROR,
                    "error": "Failed to add password (sitename already exists)"
                }

    def changeUsername(self, req: dict) -> dict | None:
        """Changes the username for a stored site in the password manager.
        Returns success/failure"""
        if not self.auth.authenticate():
            return {
                "method": "changeUsername",
                "status": self.STATUS_FAILED_BIOMETRICS if self.auth.isVerified else self.STATUS_NOT_VERIFIED,
                "error": "Authentication error"
            }
        elif "sitename" not in req or "newusername" not in req:
            return {
                "method": "changeUsername",
                "status": self.STATUS_MISSING_PARAM,
                "error": "No sitename/newusername"
            }
        else:
            if self.db.update(req["sitename"], req["newusername"], None) == 0:
                return {
                    "method": "changeUsername",
                    "status": self.STATUS_SUCCESS,
                    "error": None
                }
            else:
                return {
                    "method": "changeUsername",
                    "status": self.STATUS_API_OTHER_ERROR,
                    "error": "Failed to change username (unknown error)"
                }

    def changePassword(self, req: dict) -> dict | None:
        """Changes the password for a stored site in the password manager.
        Returns success/failure"""
        if not self.auth.authenticate():
            return {
                "method": "changePassword",
                "status": self.STATUS_FAILED_BIOMETRICS if self.auth.isVerified else self.STATUS_NOT_VERIFIED,
                "error": "Authentication error"
            }
        elif "sitename" not in req or "newpassword" not in req:
            return {
                "method": "changePassword",
                "status": self.STATUS_MISSING_PARAM,
                "error": "No sitename/newpassword"
            }
        else:
            if self.db.update(req["sitename"], None, req["newpassword"]) == 0:
                return {
                    "method": "changePassword",
                    "status": self.STATUS_SUCCESS,
                    "error": None
                }
            else:
                return {
                    "method": "changePassword",
                    "status": self.STATUS_API_OTHER_ERROR,
                    "error": "Failed to change password (unknown error)"
                }

    def removePassword(self, req: dict) -> dict | None:
        """Deletes a site, username, password entry from the password manager.
        Returns success/failure"""
        if not self.auth.authenticate():
            return {
                "method": "removePassword",
                "status": self.STATUS_FAILED_BIOMETRICS if self.auth.isVerified else self.STATUS_NOT_VERIFIED,
                "error": "Authentication error"
            }
        elif "sitename" not in req:
            return {
                "method": "removePassword",
                "status": self.STATUS_MISSING_PARAM,
                "error": "No sitename"
            }
        else:
            if self.db.delete(req["sitename"]) == 0:
                return {
                    "method": "removePassword",
                    "status": self.STATUS_SUCCESS,
                    "error": None
                }
            else:
                return {
                    "method": "removePassword",
                    "status": self.STATUS_API_OTHER_ERROR,
                    "error": "Failed to delete password (unknown error)"
                }

    def getSettings(self, req: dict) -> dict | None:
        """Returns all the current settings"""
        """if not self.auth.authenticate():
            return {
                "method": "getSettings",
                "status": self.STATUS_FAILED_BIOMETRICS if self.auth.isVerified else self.STATUS_NOT_VERIFIED,
                "error": "Authentication error"
            }
        else:"""
        if not self.auth.isVerified:
            return {
                "method": "getSettings",
                "status": self.STATUS_NOT_VERIFIED,
                "error": "Not authenticated"
            }
        else:
            return {
                "method": "getSettings",
                "status": self.STATUS_SUCCESS,
                "error": None,
                "settings": self.db.getSettings()
            }

    def setSettings(self, req: dict) -> dict | None:
        """Sets a setting in the password manager. Returns success/failure"""
        if not self.auth.isVerified:
            return {
                "method": "setSettings",
                "status": self.STATUS_NOT_VERIFIED,
                "error": "Not authenticated"
            }
        elif "settings" not in req:
            return {
                "method": "setSettings",
                "status": self.STATUS_MISSING_PARAM,
                "error": "Missing new settings"
            }
        else:
            if self.db.setSettings(req["settings"]):
                return {
                    "method": "setSettings",
                    "status": self.STATUS_SUCCESS,
                    "error": None
                }
            else:
                return {
                    "method": "setSettings",
                    "status": self.STATUS_API_OTHER_ERROR,
                    "error": "Failed to set settings"
                }

    def enrollFingerprint(self, req: dict) -> dict | None:
        """ Enroll a new fingerprint """
        if not self.auth.authenticate():
            return {
                "method": "enrollFingerprint",
                "status": self.STATUS_FAILED_BIOMETRICS if self.auth.isVerified else self.STATUS_NOT_VERIFIED,
                "error": "Authentication error"
            }
        else:
            # TODO: implement enroll
            return {
                "method": "enrollFingerprint",
                "status": self.STATUS_NOT_YET_IMPLEMENTED,
                "error": None
            }

    def deleteFingerprint(self, req: dict) -> dict | None:
        """ Delete a fingerprint """
        if not self.auth.authenticate():
            return {
                "method": "enrollFingerprint",
                "status": self.STATUS_FAILED_BIOMETRICS if self.auth.isVerified else self.STATUS_NOT_VERIFIED,
                "error": "Authentication error"
            }
        else:
            # TODO: implement delete
            return {
                "method": "deleteFingerprint",
                "status": self.STATUS_NOT_YET_IMPLEMENTED,
                "error": None
            }


    def verifyFingerprint(self, req: dict) -> dict | None:
        """Verifies a fingerprint on the sensor that is enrolled is valid.
        If the fpId field is defined in req, will search for that fingerprint."""
        fpId = None
        if "fpId" in req and req["fpId"] > 0 and req["fpId"] < 127:
            fpId = req["fpId"]
        res = self.auth.verifyFingerprint()
        if res is not None:
            return {
                "method": "verifyFingerprint",
                "status": self.STATUS_SUCCESS,
                "fpId": res[0],
                "fpHash": res[1],
                "error": None
            }
        else:
            return {
                "method": "verifyFingerprint",
                "status": self.STATUS_API_OTHER_ERROR,
                "error": "Failed to find user fingerprint after 3 tries"
            }

    def verifyMasterHash(self, req: dict) -> dict | None:
        if "hash" not in req or len(req["hash"]) != 4:
            return  {
                "method": "verifyMasterHash",
                "status": self.STATUS_MISSING_PARAM,
                "valid": False,
                "error": "No hash supplied, or hash incorrect length"
            }
        hashBytes = tuple(req["hash"].encode('utf-8'))
        if self.auth.isDefaultPswd:
            if not self.auth.changePswd(self.auth.DEFAULT_PSWD, hashBytes):
                return {
                    "method": "verifyMasterHash",
                    "status": self.STATUS_API_OTHER_ERROR,
                    "valid": False,
                    "error": "Failed to set new master password from default"
                }
        valid = self.auth.setupFp(hashBytes)
        return {
                "method": "verifyMasterHash",
                "status": self.STATUS_SUCCESS,
                "valid": valid,
                "error": None
        }

    def changeMasterPswd(self, req: dict) -> dict | None:
        """Change the code for the fingerprint sensor"""
        if "oldauthtoken" not in req or "newauthtoken" not in req:
            return {
                "method": "changeMasterPswd",
                "status": self.STATUS_MISSING_PARAM,
                "error": "No new/old auth token"
            }
        else:
            if self.auth.changePswd(tuple(req["oldauthtoken"]), tuple(req["newauthtoken"])):
                return {
                    "method": "changeMasterPswd",
                    "status": self.STATUS_SUCCESS,
                    "error": None
                }
            else:
                return {
                    "method": "changeMasterPswd",
                    "status": self.STATUS_API_OTHER_ERROR,
                    "error": "Failed to validate old authtoken"
                }
