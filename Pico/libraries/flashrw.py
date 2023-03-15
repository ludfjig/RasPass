# Library to read/write from the Pico Flash
# Copyright (c), 2023  RasPass

class FlashRW:
    BLOCKSIZE: int = 2048          # Flash storage block size
    MAXSIZE: int = BLOCKSIZE*250   # Maximum flash storage

    def __init__(self):
        """Initialize the flash"""
        self.mode = ""
        self.file = open("storage.bin", "a")
        self.close()

    def openRead(self):
        """Open file in read mode, if not already opened in read mode"""
        self.mode = "r"
        self.file = open("storage.bin", "r+b")

    def openWrite(self):
        """Open file in write mode, if not already opened in write mode"""
        self.mode = "w"
        self.file = open("storage.bin", "w+b")

    def close(self):
        self.file.close()

    def readFlashDB(self) -> bytes:
        """Read entire database in flash. Must be block-aligned.
        Returns None on failure"""
        self.openRead()
        readBytes = bytearray(self.file.read())
        self.close()
        return readBytes

    def writeFlashDB(self, raw_block: bytes) -> bool:
        """Write the raw_block to flash (will be block aligned).
        Return success/failure """
        assert len(raw_block) % self.BLOCKSIZE == 0
        self.openWrite()
        self.file.seek(0)
        if self.file.write(raw_block) == len(raw_block):
            self.file.flush()
            self.close()
            return True
        self.close()
        return False
