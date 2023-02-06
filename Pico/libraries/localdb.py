# Library to support database insert, read, and search functionality
# Copyright (c), 2023  RasPass


# Key-value database stored in the flash of the Pico
# Unique keys required
# Uses crypto library to encrypt/decrypt database entries

import flashrw
import crypto

class DataBase:
    def __init__(self, flashRWI : flashrw.FlashRW, cryptoI : crypto.Crypto):
        """ Initialize the database. Reads and parses database from flash """
        self.frw = flashRWI
        self.cr = cryptoI
        self.__parseFlashDB()

    def __parseFlashDB(self):
        """ Parse db from flash """
        self.db = {}
        raw = self.frw.readFlashDB()
        for c in range(len(raw)//256):
            entry = raw[c*256:(c+1)*256]
            sitename, encrypted_up = self.cr.getStorageSitnameUPPair(entry)
            self.db[sitename] = encrypted_up

    def __storeFlashDB(self):
        """ Store db in flash """
        raw_block = bytes()
        for sitename in self.db:
            raw_block += self.cr.getStorageByteEntry(sitename, self.db[sitename])
        self.frw.writeFlashDB(raw_block)

    def add(self, sitename : str, username : str, password : str):
        """ Inserts a new entry into the database.
        Will return error and not insert if sitename already exists (should use update)
        Returns 0 for success, -1 for error. """
        if sitename in self.db:
            return -1
        encrypted_up = self.cr.getEncryptedUP(self.frw.getAESKey(), self.frw.getAESIV(), username, password)
        self.db[sitename] = encrypted_up
        self.__storeFlashDB()
        return 0

    def get(self, sitename : str) -> tuple[str, str] | None:
        """ Gets a (username, password) tuple corresponding to sitename. Returns None if no entry found. """
        if sitename not in self.db:
            return None
        decrypt = self.cr.getDecryptedUP(self.frw.getAESKey(), self.frw.getAESIV(), self.db[sitename])
        return decrypt

    def update(self, sitename : str, username : str | None, password : str | None):
        """ Update username and/or password for given sitename.
        Will return error if sitename is not part of the db, or if both username and password are None
        Returns 0 on success, -1 on failure. """
        if sitename not in self.db or (username == None and password == None):
            return -1
        orig_username, orig_password = self.cr.getDecryptedUP(self.frw.getAESKey(), self.frw.getAESIV(), self.db[sitename])
        new_username = orig_username if username == None else username
        new_password = orig_password if password == None else password
        encrypted_up = self.cr.getEncryptedUP(self.frw.getAESKey(), self.frw.getAESIV(), new_username, new_password)
        self.db[sitename] = encrypted_up
        self.__storeFlashDB()
        return 0

    def delete(self, sitename : str):
        """ Delete the sitename.
        Will return error if sitename does not exist
        Returns 0 on success, -1 on failure. """
        if sitename not in self.db:
            return -1
        del self.db[sitename]
        self.__storeFlashDB()
        return 0

    def getAllSites(self) -> list[str]:
        """ Get list of all sitename strs """
        return list(self.db.keys())
