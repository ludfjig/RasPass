# Library to support cryptographic operations for RasPass
# Copyright (c), 2023  RasPass

import cryptolib

class Crypto:
    def getStorageSitnameUPPair(self, entry : bytes) -> tuple[str, bytes]:
        """ Returns (sitename, encrypted username+password)"""
        return (self.__getUnPadded(entry[:128]), entry[128:])

    def getStorageByteEntry(self, sitename : str, encrypted_up : bytes) -> bytes:
        """ Returns padded sitename and encrypted_up in 256B format """
        return self.__getPadded(sitename, 128) + encrypted_up

    def getEncryptedUP(self, key : bytes, IV : bytes, username : str, password : str) -> bytes:
        """ Encrypt the username and password and return padded bytes value in data storage format (128B chunk)"""
        cl = cryptolib.aes(key, 2, IV)
        uname = cl.encrypt(self.__getPadded(username, 64))
        pswd = cl.encrypt(self.__getPadded(password, 64))
        return uname + pswd

    def getDecryptedUP(self, key : bytes, IV : bytes, encrypted_up: bytes) -> tuple[str, str]:
        """ Decrypt the username and password, remove padding, and return strings for username, and password """
        cl = cryptolib.aes(key, 2, IV)
        username = self.__getUnPadded(cl.decrypt(encrypted_up[128:128+64]))
        password = self.__getUnPadded(cl.decrypt(encrypted_up[128+64:]))
        return (username, password)

    def __getPadded(self, toPad : str, padLen : int) -> bytes:
        """ Encodes ASCII string <toPad> into bytes and then pads to length <padLen> with null characters """
        return toPad.encode('ascii') + (padLen - len(toPad)) * b'\x00'

    def __getUnPadded(self, toUnPad : bytes) -> str:
        """ Decodes to ASCII string and removes all but the last null character in toUnPad """
        return toUnPad.decode('ascii').rstrip("\x00")
