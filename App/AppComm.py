import sys

# setting path
sys.path.append('../')

from Communication import CommunicationInterface
import serial
from serial.tools import list_ports
import re


class AppComm(CommunicationInterface):
  def __init__(self):
    self.s = None
    port = list_ports.comports()
    for p in port:
      if (p.vid == 11914):
        print(p.vid)
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
      print("failure establishing connection")
      exit()

  def writeRequest(self, req: str) -> int:
    # will create correct json format to send later
    # right now just trying to set up basic framework
    try:
      # should return number of bytes written
      bytes = self.s.write(req)
      return bytes
    except serial.SerialTimeoutException:
      # timed out, something went wrong, return -1 to indicate error
      print("Failure to communicate with device")
      return -1

  # expects a json response from pico
  def readResponse(self) -> str:
    try:
      res = self.s.read()
      # need to convert to json string from bytes?
      return res
    except serial.SerialTimeoutException:
      print("Failure to communicate with device")
      return ""

  def getSerial(self):
    return self.s

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