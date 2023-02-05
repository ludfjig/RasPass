import sys

# setting path
sys.path.append('../')

from Communication import CommunicationInterface
import serial
from serial.tools import list_ports
import re
import json

class AppComm(CommunicationInterface):
  def __init__(self):
    self.s = None
    port = list_ports.comports()
    for p in port:
      if (p.vid == 11914):
        device = p.device
        try:
          self.s = serial.Serial(device)
        except serial.SerialException:
          # for some reason when I do list_ports.comports on my mac it always
          # gives me "/dev/cu.usbmodem101" instead of "/dev/tty.usbmodem101"
          # so this is just forcing it to use tty for my computer if connecting
          # over cu fails
          device = re.sub(r'/cu', r'/tty', device)
          self.s = serial.Serial(device)
        break

    if self.s == None:
      exit('failure establishing connection\n')

  def writeRequest(self, req: dict) -> int:
    # will create correct json format to send later
    # right now just trying to set up basic framework
    try:
      # should return number of bytes written
      print(req)
      encoded = json.dumps(req).encode('utf-8') + b'\0'
      size = self.s.write(encoded)
      print(size)
      return (size == len(encoded))
    except serial.SerialTimeoutException:
      # timed out, something went wrong, return -1 to indicate error
      return False

  # expects a json response from pico
  def readResponse(self) -> dict:
    # while there is a next line to read from pico, read data
    # failure on error reading
    # structure back to python object from json
    # return object to caller
    while(1):
      try:
        raw = self.s.readline().strip()
        # need to convert to json string from bytes?
        res = raw.decode('utf8').replace("'", '"')
        print("Read response: ", res)
        return json.loads(res)
      except serial.SerialTimeoutException:
        return {}

  def getSerial(self):
    return self.s

  def getAllSiteNames(self):
    """Returns all site names stored in password manager"""
    req = {
        "method" : "getAllSiteNames",
        "authtoken" : "1"
    }
    written = self.writeRequest(req)
    if not written:
      print("Failure to communicate with device\n")
      return {}

    res = self.readResponse()
    if res == {}:
      print("Failure retrieving sitenames")
      return {}

    return res

  def getPassword(self, sitename: str):
    """Returns username, password, or error on authentication failure/no entry"""
    # sanitize input
    print("get pass")
    req = {
        "method" : "getPassword",
        "sitename" : sitename,
        "authtoken" : "1"
    }
    written = self.writeRequest(req)
    if not written:
      print("Failure to communicate with device\n")
      return {}

    res = self.readResponse()
    if res == {}:
      print("Failure retrieving passwords")
      return {}

    return res

  def addPassword(self, sitename: str, user: str, pswd: str):
    """Adds a new username, password, site to the password manager. Returns success/failure"""
    print("add pass")
    req = {
        "method" : "addPassword",
        "sitename" : sitename,
        "username" : user,
        "password" : pswd,
        "authtoken" : "1"
    }
    written = self.writeRequest(req)
    if not written:
      print("Failure to communicate with device\n")
      return False

    return True

  def changeUsername(self, site: str, user: str):
    """Changes the username for a stored site in the password manager. Returns success/failure"""
    req = {
        "method" : "changeUsername",
        "sitename" : site,
        "username" : user,
        "authtoken" : "1"
    }
    written = self.writeRequest(req)
    if not written:
      print("Failure to communicate with device\n")
      return False

    return True

  def changePassword(self, site: str, pswd: str):
    """Changes the password for a stored site in the password manager. Returns success/failure"""
    req = {
        "method" : "changePassword",
        "sitename" : site,
        "password" : pswd,
        "authtoken" : "1"
    }
    written = self.writeRequest(req)
    if not written:
      print("Failure to communicate with device\n")
      return False

    return True

  def removePassword(self, site: str):
    """Deletes a site, username, password entry from the password manager. Returns success/failure"""
    req = {
        "method" : "removePassword",
        "sitename" : site,
        "authtoken" : "1"
    }
    written = self.writeRequest(req)
    if not written:
      print("Failure to communicate with device\n")
      return False
    return True

  def getSettings(self):
    """Returns all the current settings"""
    req = {
        "method" : "getSettings",
        "authtoken" : "1"
    }
    written = self.writeRequest(req)
    if not written:
      print("Failure to communicate with device\n")
      return {}

    res = self.readResponse()
    if res == {}:
      print("Failure retrieving settings")
      return{}

    return res

  def setSettings(self, settings: str):
    """Sets a setting in the password manager. Returns success/failure"""
    req = {
        "method" : "setSettings",
        "settings" : settings,
        "authtoken" : "1"
    }
    written = self.writeRequest(req)
    if not written:
      print("Failure to communicate with device\n")
      return False
    return True
