# Library to support database insert, read, and search functionality
# Copyright (c), 2023  RasPass

# Key-value database stored in the flash of the Pico
# Unique keys required

from flashrw import FlashRW
import json

class DataBase:
    SETTINGS_START: int = 0
    SETTINGS_END: int = FlashRW.BLOCKSIZE*3
    PSWDS_START: int = SETTINGS_END
    PSWDS_END: int = FlashRW.MAXSIZE

    ENCODING: str = "ascii"

    SITE_SZ: int = FlashRW.BLOCKSIZE//2
    USER_SZ: int = FlashRW.BLOCKSIZE//4
    PSWD_SZ: int = FlashRW.BLOCKSIZE//4

    SETTINGS_KEYS = ["fingerprints"]  # Keys that should be in settings

    def __init__(self, flashRWI: FlashRW):
        """Initialize the database. Reads and parses database from flash"""
        self.frw: FlashRW = flashRWI
        self.settings: dict = {}
        self.__parseFlashDB()
        if not self.__checkSettings(self.settings):
            self.__setDefaultSettings()

    def __parseFlashDB(self):
        """Parse db from flash"""
        self.db = {}
        raw = self.frw.readFlashDB()
        rawSettings = raw[self.SETTINGS_START:self.SETTINGS_END]
        try:
            self.settings = json.loads(self.__getUnPadded(rawSettings))
        except:
            self.settings = {}
        rawSites = raw[self.SETTINGS_END:] # self.PSWDS_END]
        for c in range(len(rawSites) // FlashRW.BLOCKSIZE):
            en = rawSites[c * FlashRW.BLOCKSIZE: (c + 1) * FlashRW.BLOCKSIZE]
            sitename, username, password = self.getStorageSitnameUPPair(en)
            self.db[sitename] = (username, password)

    def __storeFlashDB(self):
        """Store db in flash"""
        raw_block = bytes()
        try:
            raw_block += self.__getPadded(json.dumps(self.settings), self.SETTINGS_END-self.SETTINGS_START)
        except:
            raw_block += b"\x00" * (self.SETTINGS_END-self.SETTINGS_START)
        self.frw.writeSettings(raw_block)
        block = bytes()
        for i, sn in enumerate(self.db):
            block = self.getStorageByteEntry(sn, self.db[sn])
            self.frw.writeFlashDB(block, i)

    def __checkSettings(self, settings):
        """Verify the settings have the expected keys""" 
        for key in self.SETTINGS_KEYS:
            if key not in settings:
                return False
        return True

    def __setDefaultSettings(self):
        """Load the default settings structure and save to flash, if settings is corrupted/not initialized"""
        self.settings = {}
        for key in self.SETTINGS_KEYS:
            self.settings[key] = {}
        self.__storeFlashDB()

    def addMasterHash(self, pass_hash: bytes):
        """Add hash of last 4 bytes of master password to database"""
        # self.master_hash = pass_hash
        self.__storeFlashDB()

    def setSettings(self, settings: dict) -> bool:
        """ Check settings, and store in flash """
        if not self.__checkSettings(settings):  # Check settings
            return False
        try:  # check length
            if len(json.dumps(settings)) > self.SETTINGS_END-self.SETTINGS_START:
                return False
        except:  # not JSON
            return False
        self.settings = settings
        self.__storeFlashDB()
        return True

    def getSettings(self, fpIds) -> dict:
        """ Get settings (combine calculated settings and stored settings)"""
        actualSettings: dict = {}
        actualSettings.update(self.settings)

        # Get num passwords
        actualSettings["numPswdAvail"] = self.getMaxNumPasswords() - self.getNumPasswords()
        self.__storeFlashDB()
        return actualSettings

    def getNumPasswords(self):
        """ Return number of passwords in database """
        return len(list(self.db.keys()))

    def getMaxNumPasswords(self):
        """ Return maximum number of passwords that can be stored in the database """
        return (self.frw.MAXSIZE - self.PSWDS_START)//self.frw.BLOCKSIZE

    def getStorageSitnameUPPair(self, entry: bytes) -> tuple[str, str, str]:
        """Returns (sitename, username, password)"""
        return (
            self.__getUnPadded(entry[:self.SITE_SZ]),
            self.__getUnPadded(entry[self.SITE_SZ:self.SITE_SZ+self.USER_SZ]),
            self.__getUnPadded(entry[self.SITE_SZ+self.USER_SZ:])
        )

    def getStorageByteEntry(self, sn: str, up_pair: tuple[str, str]) -> bytes:
        """Returns padded sitename and encrypted_up in 2048B format"""
        return (
            self.__getPadded(sn, self.SITE_SZ)
            + self.__getPadded(up_pair[0], self.USER_SZ)
            + self.__getPadded(up_pair[1], self.PSWD_SZ)
        )

    def __getPadded(self, toPad: str, padLen: int) -> bytes:
        """Encodes ASCII string <toPad> into bytes and
        then pads to length <padLen> with null characters"""
        return toPad.encode(self.ENCODING) + (padLen - len(toPad)) * b"\x00"

    def __getUnPadded(self, toUnPad: bytes) -> str:
        """Decodes to ASCII string and removes all
        but the last null character in toUnPad"""
        return toUnPad.decode(self.ENCODING).rstrip("\x00")

    def add(self, sitename: str, username: str, password: str) -> bool:
        """Inserts a new entry into the database.
        Will return error and not insert if sitename already exists
        (should use update). Returns success/failure."""
        if sitename in self.db:
            return False
        self.db[sitename] = (username, password)
        self.__storeFlashDB()
        return True

    def get(self, sitename: str) -> tuple[str, str] | None:
        """Gets a (username, password) tuple corresponding to sitename.
        Returns None if no entry found."""
        if sitename not in self.db:
            return None
        return self.db[sitename]

    def update(self, sitename: str, user: str | None, pswd: str | None) -> bool:
        """Update username and/or password for given sitename.
        Will return error if sitename is not part of the db, or if both
        username and password are None
        Returns success/failure."""
        if sitename not in self.db or (user is None and pswd is None):
            return False
        orig_username, orig_password = self.db[sitename]
        new_username = orig_username if user is None else user
        new_password = orig_password if pswd is None else pswd
        self.db[sitename] = (new_username, new_password)
        self.__storeFlashDB()
        return True

    def delete(self, sitename: str) -> bool:
        """Delete the sitename.
        Will return error if sitename does not exist
        Returns success/failure."""
        if sitename not in self.db:
            return False
        del self.db[sitename]
        self.__storeFlashDB()
        return True

    def getAllSites(self) -> list[str]:
        """Get list of all sitename strs"""
        return list(filter(None, self.db.keys()))
