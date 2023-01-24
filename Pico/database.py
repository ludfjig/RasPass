# Library to support database insert, read, and search functionality
# Copyright (c), 2023  RasPass


# Key-value database stored in the flash of the Pico
# 

class DB:
    def __init__(self):
        """ Initialize the database. Reads and parses database from flash """

    def __readFlash(self):
        """ Load the database from flash storage """
        return 0

    def __writeFlash(self):
        """ Write the database to flash storage. Calls read after performing the write """
        """ Need to disable interrupts"""
        return 0

    def insert(self, sitename, username, password):
        """ Inserts a new entry into the database """
        return 1

    def get(self, sitename):
        """ Gets an entry corresponding to sitename. Returns None if no entry found. """
        return None
