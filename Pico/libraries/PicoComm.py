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
  def readRequest(self) -> bool: #dict:
    # while there is a next line to read from pico, read data
    # failure on error reading
    # structure back to python object from json
    # return object to caller
    res = "".join(sys.stdin.readlines())
    #return json.load(res)
    self.state = not self.state
    return self.state

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