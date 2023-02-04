# Library to read/write from the Pico Flash
# Copyright (c), 2023  RasPass

class FlashRW:
    def __init__(self):
        """ Initialize the flash """
        self.state = 0

    def readFlashDB(self) -> bytes:
        """ Read entire database in flash. Must be 256B-aligned. Returns None on failure """
        return bytearray()

    def writeFlashDB(self, raw_block : bytes) -> int:
        """ Write the raw_block to flash (will be 256B aligned). Return 0 on failure, 1 on success. """
        assert len(raw_block)%256 == 0
        return 0

    def getAESKey(self) -> bytes:
        """ TODO: generate a key to store in flash, or use cryptographic co-processor """
        return "s5v8y/B?E(H+MbQeThWmZq4t7w9z$C&F".encode('ascii')

    def getAESIV(self) -> bytes:
        """ TODO: fix this to use actual random IV - should be different for each """
        return "abcdefgh".encode('ascii')