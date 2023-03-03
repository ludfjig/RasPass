# Library to support database insert, read, and search functionality
# Copyright (c), 2023  RasPass

# Key-value database stored in the flash of the Pico
# Unique keys required

import flashrw


class DataBase:
    def __init__(self, flashRWI: flashrw.FlashRW):
        """Initialize the database. Reads and parses database from flash"""
        self.frw = flashRWI
        self.master_hash = self.frw.getPasswordHash()
        self.__parseFlashDB()

    def __parseFlashDB(self):
        """Parse db from flash"""
        self.db = {}
        raw = self.frw.readFlashDB()
        for c in range(len(raw) // 2048):
            en = raw[c * 2048: (c + 1) * 2048]
            sitename, username, password = self.getStorageSitnameUPPair(en)
            self.db[sitename] = (username, password)

    def __storeFlashDB(self):
        """Store db in flash"""
        raw_block = bytes()
        raw_block += self.master_hash
        raw_block += 2044 * b"\x00"
        for sn in self.db:
            raw_block += self.getStorageByteEntry(sn, self.db[sn])
        self.frw.writeFlashDB(raw_block)

    def addMasterHash(self, pass_hash: bytes):
        """Add hash of last 4 bytes of master password to database"""
        self.master_hash = pass_hash
        self.__storeFlashDB()

    def getStorageSitnameUPPair(self, entry: bytes) -> tuple[str, str, str]:
        """Returns (sitename, username, password)"""
        return (
            self.__getUnPadded(entry[:1024]),
            self.__getUnPadded(entry[1024: 1024 + 512]),
            self.__getUnPadded(entry[1024 + 512:]),
        )

    def getStorageByteEntry(self, sn: str, up_pair: tuple[str, str]) -> bytes:
        """Returns padded sitename and encrypted_up in 256B format"""
        return (
            self.__getPadded(sn, 1024)
            + self.__getPadded(up_pair[0], 512)
            + self.__getPadded(up_pair[1], 512)
        )

    def __getPadded(self, toPad: str, padLen: int) -> bytes:
        """Encodes ASCII string <toPad> into bytes and
        then pads to length <padLen> with null characters"""
        return toPad.encode("ascii") + (padLen - len(toPad)) * b"\x00"

    def __getUnPadded(self, toUnPad: bytes) -> str:
        """Decodes to ASCII string and removes all
        but the last null character in toUnPad"""
        return toUnPad.decode("ascii").rstrip("\x00")

    def add(self, sitename: str, username: str, password: str):
        """Inserts a new entry into the database.
        Will return error and not insert if sitename already exists
        (should use update). Returns 0 for success, -1 for error."""
        if sitename in self.db:
            return -1
        self.db[sitename] = (username, password)
        self.__storeFlashDB()
        return 0

    def get(self, sitename: str) -> tuple[str, str] | None:
        """Gets a (username, password) tuple corresponding to sitename.
        Returns None if no entry found."""
        if sitename not in self.db:
            return None
        return self.db[sitename]

    def update(self, sitename: str, user: str | None, pswd: str | None):
        """Update username and/or password for given sitename.
        Will return error if sitename is not part of the db, or if both
        username and password are None
        Returns 0 on success, -1 on failure."""
        if sitename not in self.db or (user is None and pswd is None):
            return -1
        orig_username, orig_password = self.db[sitename]
        new_username = orig_username if user is None else user
        new_password = orig_password if pswd is None else pswd
        self.db[sitename] = (new_username, new_password)
        self.__storeFlashDB()
        return 0

    def delete(self, sitename: str):
        """Delete the sitename.
        Will return error if sitename does not exist
        Returns 0 on success, -1 on failure."""
        if sitename not in self.db:
            return -1
        del self.db[sitename]
        self.__storeFlashDB()
        return 0

    def getAllSites(self) -> list[str]:
        """Get list of all sitename strs"""
        return list(self.db.keys())
