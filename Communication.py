class CommunicationInterface:
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