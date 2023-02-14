# Library to read/write from the Pico Flash
# Copyright (c), 2023  RasPass

PICO_FLASH_SIZE_BYTES = 2097152
DATA_CHUNK = 256

class FlashRW:
    def __init__(self):
        """Initialize the flash"""
        self.mode = "r"
        self.file = open("storage.bin", "w+b")
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
        bytes = bytearray(self.file.read())
        return bytes

    def writeFlashDB(self, raw_block: bytes) -> int:
        """Write the raw_block to flash (will be 256B aligned).
        Return 0 on failure, 1 on success."""
        assert len(raw_block) % 256 == 0
        self.openWrite()
        if self.file.write(raw_block) == len(raw_block):
            self.file.flush()
            return 1
        return 0