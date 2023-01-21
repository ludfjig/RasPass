# Library to support cryptographic operations for RasPass
# Copyright (c), 2023  RasPass

import cryptolib

class Crypto:
    def getStorageEncrypted(self, key : bytes, IV : bytes, sitename : str, username : str, password : str) -> bytes:
        """ Encrypt the username and password and return sitename and padded bytes value in data storage format (256B chunk)"""
        cl = cryptolib.aes(key, cryptolib.MODE_CBC, IV)
        uname = cl.encrypt(self.__getPadded(username.encode('ascii'), 64))
        pswd = cl.encrypt(self.__getPadded(password.encode('ascii'), 64))
        stname = self.__getPadded(sitename.encode('ascii'), 128)
        return stname + uname + pswd

    def getStorageDescrptyed(self, key : bytes, IV : bytes, encrypted : bytes) -> tuple[str, str, str]:
        """ Decrypt the username and password, remove padding, and return strings for sitename, username, and password """
        cl = cryptolib.aes(key, cryptolib.MODE_CBC, IV)
        sitename = self.__getUnPadded(encrypted[:128])
        username = self.__getUnPadded(cl.decrypt(encrypted[128:128+64]))
        password = self.__getUnPadded(cl.decrypt(encrypted[128+64:]))
        return (sitename, username, password)

    def __getPadded(self, toPad : bytes, padLen : int) -> bytes:
        """ Pads bytestring <toPad> to length <padLen> with null characters """
        return toPad + (padLen - len(toPad)) * b'\x00'

    def __getUnPadded(self, toUnPad : bytes) -> str:
        """ Decodes to ASCII string and removes all but the last null character in toUnPad """
        return toUnPad.decode('ascii').rstrip("\x00")
