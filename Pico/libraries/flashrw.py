# Library to read/write from the Pico Flash
# Copyright (c), 2023  RasPass


class FlashRW:
    BLOCKSIZE : int = 2048

    def __init__(self):
        """Initialize the flash"""
        self.mode = ""
        self.file = open("storage.bin", "a")
        self.openRead()

    def openRead(self):
        """Open file in read mode, if not already opened in read mode"""
        if self.mode != "r":
            self.file.close()
            self.mode = "r"
            self.file = open("storage.bin", "r+b")

    def openWrite(self):
        """Open file in write mode, if not already opened in write mode"""
        if self.mode != "w":
            self.file.close()
            self.mode = "w"
            self.file = open("storage.bin", "w+b")

    def readFlashDB(self) -> bytes:
        """Read entire database in flash. Must be 256B-aligned.
        Returns None on failure"""
        self.openRead()
        self.file.seek(self.BLOCKSIZE)
        bytes = bytearray(self.file.read())
        return bytes

    def writeFlashDB(self, raw_block: bytes) -> int:
        """Write the raw_block to flash (will be 256B aligned).
        Return 0 on failure, 1 on success."""
        assert len(raw_block) % self.BLOCKSIZE == 0
        self.openWrite()
        self.file.seek(0)
        if self.file.write(raw_block) == len(raw_block):
            self.file.flush()
            return 1
        return 0

    def storePasswordHash(self, pass_hash):
        assert len(pass_hash) == self.BLOCKSIZE
        self.openWrite()
        self.file.seek(0)
        if self.file.write(pass_hash) == len(pass_hash):
            self.file.flush()
            return 1
        return 0

    def getPasswordHash(self):
        self.openRead()
        self.file.seek(0)
        rawb = self.file.read(4)
        pswdhash = bytearray(rawb if rawb else b"\x00\x00\x00\x00")
        return pswdhash
