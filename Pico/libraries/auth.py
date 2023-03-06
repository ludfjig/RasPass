# Library for communication via JSON requests/responses over standard IO
# Copyright (c), 2023  RasPass

# Sections of this code are credited to Adafruit under the MIT license


import adafruit_fingerprint as af
import time
import hashlib
import time
from machine import Pin

try:
    from typing import Tuple, Dict
except ImportError:
    pass


class Auth:
    DEFAULT_PSWD: Tuple[int, int, int, int] = (0,0,0,0)     # Default sensor password
    finger: af.Adafruit_Fingerprint
    fingerTemplates: Dict[int,str]  # Fingerprint templates we have
    numAttempts: int                # Number of attempts on sensor
    maxAttempts: int                # Maximum number of attempts before reset
    isDefaultPswd: bool             # Is the sensor using the default password?
    isVerified: bool                # Is this sensor active (verified password)?
    isReset: bool                   # Is this sensor soft-reset (needs power cycle to work again)?

    def __init__(self, fingerprint: af.Adafruit_Fingerprint, maxAttempts : int = 5):
        self.finger = fingerprint
        self.fingerTemplates = {}
        self.numAttempts = 0
        self.maxAttempts = maxAttempts  # Number of attempts. TODO: initialize from settings
        self.led = Pin(25, Pin.OUT)
        self.isDefaultPswd = False
        self.isVerified = False
        self.isReset = False
        self.setupFp(self.DEFAULT_PSWD)

    def blink_yes(self):
        for i in range(4):
            self.led.toggle()
            time.sleep(0.2)

    def blink_no(self):
        for i in range(10):
            self.led.toggle()
            time.sleep(0.1)

    def setupFp(self, fpPasswd: Tuple[int, int, int, int]):
        """Initialize the fingerprint sensor with the password.
        This must be called first, before any other API call.
        Returns true on success, or false on failed authentication/error"""
        if self.isReset:
            return False
        if self.finger.initialize(fpPasswd):
            self.fingerTemplates = {}
            if self.finger.read_templates() == af.OK:
                for fpId in self.finger.templates:
                    if self.finger.load_model(fpId,1) == af.OK:
                        data = self.finger.get_fpdata("char",1)
                        if len(data) > 0:
                            self.fingerTemplates[fpId] = str(hashlib.sha256(bytes(data)).digest().hex())
                        time.sleep(0.1)
                self.isVerified = True
                self.isDefaultPswd = fpPasswd == self.DEFAULT_PSWD
                self.numAttempts = 0 # Reset # of attempts on setup
                return True
        return False

    def changePswd(self, oldFpPasswd: Tuple[int, int, int, int],
                        newFpPasswd: Tuple[int, int, int, int]):
        """Change the fp password, if the old password is correct"""
        if not self.isVerified or self.isReset:
            return False
        if self.finger.verify_password(oldFpPasswd):
            if self.finger.set_password(newFpPasswd):
                self.isDefaultPswd = newFpPasswd == self.DEFAULT_PSWD
                self.isVerified = False
                return True
        return False

    def verifyFingerprint(self) -> Tuple[int, str] | None:
        """Verify a fingerprint is present and matches (matches to id desiredId if not None).
        Returns None on failure, or otherwise a tuple of the fingerprint ID and the hexdigest of the template."""
        if not self.isVerified or self.isReset:
            return None

        if self.get_fingerprint():
            if self.finger.finger_id is not None and self.finger.finger_id >= 0:
                fpId = int(self.finger.finger_id)
                #self.blink_yes()
                return (fpId, self.fingerTemplates[fpId])

        #self.blink_no()
        return None

    def authenticate(self) -> bool:
        """Require fingerprint authentication to continue"""
        if not self.isVerified or self.isReset: # Not setup
            return False
        elif self.numAttempts >= self.maxAttempts: # Too many attempts - reset
            self.softreset()
            return False
        else:
            verifiedUser = self.verifyFingerprint() != None
            self.numAttempts = 0 if verifiedUser else self.numAttempts + 1
            return verifiedUser

    def get_fingerprint(self):
        """Get a finger print image, template it, and see if it matches!"""
        """Credit: Adafruit"""
        #print("Waiting for image...")
        if not self.isVerified or self.isReset:
            return False
        while self.finger.get_image() != af.OK:
            pass
        #print("Templating...")
        if self.finger.image_2_tz(1) != af.OK:
            return False
        #print("Searching...")
        if self.finger.finger_search() != af.OK:
            return False
        return True

    # pylint: disable=too-many-branches
    def get_fingerprint_detail(self):
        """Get a finger print image, template it, and see if it matches!
        This time, print out each error instead of just returning on failure"""
        """Credit: Adafruit"""
        if not self.isVerified or self.isReset:
            return False
        print("Getting image...", end="")
        i = self.finger.get_image()
        if i != af.OK:
            if i == af.NOFINGER:
                print("No finger detected")
            elif i == af.IMAGEFAIL:
                print("Imaging error")
            else:
                print("Other error")
            return False

        print("Templating...", end="")
        i = self.finger.image_2_tz(1)
        if i != af.OK:
            if i == af.IMAGEMESS:
                print("Image too messy")
            elif i == af.FEATUREFAIL:
                print("Could not identify features")
            elif i == af.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        print("Searching...", end="")
        i = self.finger.finger_search()
        # pylint: disable=no-else-return
        # This block needs to be refactored when it can be tested.
        if i == af.OK:
            print("Found fingerprint!")
            print("Confidence:", self.finger.confidence)
            print("ID:", self.finger.finger_id)
            return True
        else:
            """if i == af.NOTFOUND:
                print("No match found")
            else:
                print("Other error")"""
            return False

    def enroll_finger(self, location):
        """Take a 2 finger images and template it, then store in 'location'"""
        """Credit: Adafruit"""
        if not self.isVerified or self.isReset:
            return False
        for fingerimg in range(1, 3):
            if fingerimg == 1:
                print("Place finger on sensor...", end="")
            else:
                print("Place same finger again...", end="")

            while True:
                i = self.finger.get_image()
                if i == af.OK:
                    print("Image taken")
                    break
                if i == af.NOFINGER:
                    print(".", end="")
                elif i == af.IMAGEFAIL:
                    print("Imaging error")
                    return False
                else:
                    print("Other error")
                    return False

            print("Templating...", end="")
            i = self.finger.image_2_tz(fingerimg)
            if i == af.OK:
                print("Templated")
            else:
                if i == af.IMAGEMESS:
                    print("Image too messy")
                elif i == af.FEATUREFAIL:
                    print("Could not identify features")
                elif i == af.INVALIDIMAGE:
                    print("Image invalid")
                else:
                    print("Other error")
                return False

            if fingerimg == 1:
                print("Remove finger")
                time.sleep(1)
                while i != af.NOFINGER:
                    i = self.finger.get_image()

        print("Creating model...", end="")
        i = self.finger.create_model()
        if i == af.OK:
            print("Created")
        else:
            if i == af.ENROLLMISMATCH:
                print("Prints did not match")
            else:
                print("Other error")
            return False

        print("Storing model #%d..." % location, end="")
        i = self.finger.store_model(location)
        if i == af.OK:
            print("Stored")
        else:
            if i == af.BADLOCATION:
                print("Bad storage location")
            elif i == af.FLASHERR:
                print("Flash storage error")
            else:
                print("Other error")
            return False

        return True

    def get_num(self, max_number):
        """Use input() to get a valid number from 0 to the maximum size
        of the library. Retry till success!"""
        i = -1
        while (i > max_number - 1) or (i < 0):
            try:
                i = int(input("Enter ID # from 0-{}: ".format(max_number - 1)))
            except ValueError:
                pass
        return i

    def softreset(self):
        """ Run a soft reset on the sensor
        Locks the sensor until setupFp is called again """
        self.finger.soft_reset()
        self.isVerified = False
        self.isDefaultPswd = False
        self.isReset = True

    def main_loop(self, finger):
        """ Note: this is just used for testing. """
        """Credit: Adafruit"""
        while True:
            print("----------------")
            if finger.read_templates() != af.OK:
                raise RuntimeError("Failed to read templates")
            print("Fingerprint templates: ", finger.templates)
            if finger.count_templates() != af.OK:
                raise RuntimeError("Failed to read templates")
            print("Number of templates found: ", finger.template_count)
            if finger.read_sysparam() != af.OK:
                raise RuntimeError("Failed to get system parameters")
            print("Size of template library: ", finger.library_size)
            print("e) enroll print")
            print("f) find print")
            print("d) delete print")
            print("r) reset library")
            print("q) quit")
            print("----------------")
            c = input("> ")

            if c == "e":
                self.enroll_finger(self.get_num(finger.library_size))
            if c == "f":
                if self.get_fingerprint():
                    print("Detected #", finger.finger_id, "with confidence", finger.confidence)
                else:
                    print("Finger not found")
            if c == "d":
                if finger.delete_model(self.get_num(finger.library_size)) == af.OK:
                    print("Deleted!")
                else:
                    print("Failed to delete")
            if c == "r":
                if finger.empty_library() == af.OK:
                    print("Library empty!")
                else:
                    print("Failed to empty library")
            if c == "q":
                print("Exiting fingerprint example program")
                raise SystemExit