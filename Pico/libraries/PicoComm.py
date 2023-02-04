import sys
import json

class PicoComm():

  def __init__(self):
    self.state = True

  # send a response to the app
  def writeResponse(self, resp: dict) -> int:
    sys.stdout.write(json.dumps(resp))
    return 0

  # expects a json request from the app
  def readRequest(self) -> dict | None:
    raw = sys.stdin.readline().strip()
    try:
        return json.loads(raw)
    except:
      return None

  def getAllSiteNames(self):
    """Returns all site names stored in password manager"""
    pass

  def getPassword(self, sitename: str):
    """Returns username, password, or error on authentication failure/no entry"""
    pass

  def addPassword(self, sitename: str, user: str, pswd: str):
    """Adds a new username, password, site to the password manager. Returns success/failure"""
    pass

  def changeUsername(self, site: str, user: str):
    """Changes the username for a stored site in the password manager. Returns success/failure"""
    pass

  def changePassword(self, site: str, pswd: str):
    """Changes the password for a stored site in the password manager. Returns success/failure"""
    pass

  def removePassword(self, site: str):
    """Deletes a site, username, password entry from the password manager. Returns success/failure"""
    pass

  def getSettings(self):
    """Returns all the current settings"""
    pass

  def setSettings(self, settings: str):
    """Sets a setting in the password manager. Returns success/failure"""
    pass