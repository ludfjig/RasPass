# Library to support cryptographic operations for RasPass
# Copyright (c), 2023  RasPass

import cryptolib


class Crypto:
    def getStorageSitnameUPPair(self, entry: bytes) -> tuple[str, str, str]:
        """Returns (sitename, username, password)"""
        return (
            self.__getUnPadded(entry[:128]),
            self.__getUnPadded(entry[128: 128 + 64]),
            self.__getUnPadded(entry[128 + 64:]),
        )

    def getStorageByteEntry(self, sn: str, up_pair: tuple[str, str]) -> bytes:
        """Returns padded sitename and encrypted_up in 256B format"""
        return (
            self.__getPadded(sn, 128)
            + self.__getPadded(up_pair[0], 64)
            + self.__getPadded(up_pair[1], 64)
        )

    def __getPadded(self, toPad: str, padLen: int) -> bytes:
        """Encodes ASCII string <toPad> into bytes and
        then pads to length <padLen> with null characters"""
        return toPad.encode("ascii") + (padLen - len(toPad)) * b"\x00"

    def __getUnPadded(self, toUnPad: bytes) -> str:
        """Decodes to ASCII string and removes all
        but the last null character in toUnPad"""
        return toUnPad.decode("ascii").rstrip("\x00")
