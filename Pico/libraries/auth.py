import adafruit_fingerprint as af
import time
import hashlib

try:
    from typing import Tuple, Dict
except ImportError:
    pass


class Auth:
    finger: af.Adafruit_Fingerprint
    fingerTemplates: Dict[int,str]
    numAttempts: int
    hasSetup: bool

    def __init__(self, fingerprint : af.Adafruit_Fingerprint):
        self.finger = fingerprint
        self.hasSetup = False
        self.fingerTemplates = {}
        self.numAttempts = 5 # Number of attempts. TODO: initialize from settings

    def setupFp(self, fpPasswd: Tuple[int, int, int, int]):
        """Initialize the fingerprint sensor with the password.
        This must be called first, before any other API call.
        Returns true on success, or false on failed authentication/error"""
        if self.finger.initialize(fpPasswd):
            self.fingerTemplates = {}
            if self.finger.read_templates() == af.OK:
                for fpId in self.finger.templates:
                    if self.finger.load_model(fpId,1) == af.OK:
                        data = self.finger.get_fpdata("char",1)
                        if len(data) > 0:
                            self.fingerTemplates[fpId] = str(hashlib.sha256(bytes(data)).digest().hex())
                        time.sleep(0.1)
                    #print("Hashed template for fingerprint",fpId) # DEBUGGING
                self.hasSetup = True
                return True
        return False

    def changePswd(self, oldFpPasswd: Tuple[int, int, int, int],
                        newFpPasswd: Tuple[int, int, int, int]):
        """Change the fp password, if the old password is correct"""
        if not self.hasSetup:
            return False
        if self.finger.verify_password(oldFpPasswd):
            return self.finger.set_password(newFpPasswd)
        return False

    def verifyFingerprint(self, desiredId: int | None = None) -> Tuple[int, str] | None:
        """Verify a fingerprint is present and matches (matches to id desiredId if not None).
        Returns None on failure, or otherwise a tuple of the fingerprint ID and the hexdigest of the template."""
        if not self.hasSetup:
            return None
        for i in range(self.numAttempts):
            if self.get_fingerprint():
                if self.finger.finger_id is not None and self.finger.finger_id > 0:
                    fpId = int(self.finger.finger_id)
                    if fpId in self.fingerTemplates:
                        if desiredId is None or fpId == desiredId:
                            return (fpId, self.fingerTemplates[fpId])
            time.sleep(2)
        return None

    def authenticate(self) -> bool:
        """Require fingerprint authentication to continue"""
        if not self.hasSetup:
            return False
        return self.verifyFingerprint() != None

    def get_fingerprint(self):
        """Get a finger print image, template it, and see if it matches!"""
        """Credit: Adafruit"""
        #print("Waiting for image...")
        if not self.hasSetup:
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
        if not self.hasSetup:
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
        if not self.hasSetup:
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

    def main_loop(self, finger):
        """ Note: this is just used for testing. """
        """Credit: Adafruit"""
        while True:
            print("----------------")
            if finger.read_templates() != af.OK:
                raise RuntimeError("Failed to read templates")
            print("Fingerprint templates:", finger.templates)
            print("e) enroll print")
            print("f) find print")
            print("d) delete print")
            print("----------------")
            c = input("> ")

            if c == "e" or c == "d":
                i = 0
                while (i > 127) or (i < 1):
                    try:
                        i = int(input("Enter ID # from 1-127: "))
                    except ValueError:
                        pass
                if c == "e":
                    self.enroll_finger(i)
                elif c == "d":
                    if finger.delete_model(i) == af.OK:
                        print("Deleted!")
                    else:
                        print("Failed to delete")
            if c == "f":
                if self.get_fingerprint():
                    print(
                        "Detected #",
                        finger.finger_id,
                        "with confidence",
                        finger.confidence,
                    )
                else:
                    print("Finger not found")