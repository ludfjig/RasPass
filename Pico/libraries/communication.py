import sys
import json
import localdb
import auth

class PicoComm:
  def __init__(self, db : localdb.DataBase, auth : auth.Auth):
    self.db = db
    self.auth = auth

  # send a response to the app
  def writeResponse(self, resp: dict) -> int:
    sys.stdout.write(json.dumps(resp).encode('utf-8') + b"\0")
    return 0

  # expects a json request from the app
  def readRequest(self) -> dict | None:
    print("reading")
    raw = bytearray()
    byte = sys.stdin.buffer.read(1)
    while(byte != b'\0'):
      raw.extend(byte)
      byte = sys.stdin.buffer.read(1)
    print(raw)
    try:
        return json.loads(raw.decode(encoding='utf-8'))
    except:
      return None

  def processRequest(self, req) -> bool:
    """ Process a request, sending a response to the device. Returns true if req was successfully processed, and false otherwise. """
    print("process")
    if "method" not in req:
      return False
    handler = getattr(self, req.method)
    if not handler:
      return False
    resp = handler(req)
    if resp == None:
      return False
    self.writeResponse(resp)
    return True

  def getAllSiteNames(self, req: dict) -> dict | None:
    """Returns all site names stored in password manager"""
    return {
      "method": "getAllSiteNames",
      "status": 0,
      "error": None,
      "sitenames": self.db.getAllSites()
    }

  def getPassword(self, req: dict) -> dict | None:
    """Returns username, password, or error on authentication failure/no entry"""
    if not self.auth.authenticate():
      return {
        "method": "getPassword",
        "status": 1,
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
      if up != None:
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
    """Adds a new username, password, site to the password manager. Returns success/failure"""
    if not self.auth.authenticate():
      return {
        "method": "addPassword",
        "status": 1,
        "error": "Failed biometric authentication"
      }
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
      if self.db.add(req["sitename"], req["username"], req["password"]) == 0:
        return {
          "method": "addPassword",
          "status": 0,
          "error": None
        }
      else:
        return {
          "method": "addPassword",
          "status": 5,
          "error": "Failed to add password (unknown error)"
        }

  def changeUsername(self, req: dict) -> dict | None:
    """Changes the username for a stored site in the password manager. Returns success/failure"""
    if not self.auth.authenticate():
      return {
        "method": "changeUsername",
        "status": 1,
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
    """Changes the password for a stored site in the password manager. Returns success/failure"""
    if not self.auth.authenticate():
      return {
        "method": "changePassword",
        "status": 1,
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
    """Deletes a site, username, password entry from the password manager. Returns success/failure"""
    if not self.auth.authenticate():
      return {
        "method": "removePassword",
        "status": 1,
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
        "status": 1,
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
        "status": 1,
        "error": "Failed biometric authentication"
      }
    else:
      # TODO: implement settings
      return {
        "method": "setSettings",
        "status": 0,
        "error": None
      }