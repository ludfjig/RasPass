import adafruit_fingerprint as af
import time


class Auth:
    def __init__(self, fingerprint):
        self.finger = fingerprint

    def authenticate(self) -> bool:
        """Require fingerprint authentication to continue"""
        return True

    def get_fingerprint(self):
        """Get a finger print image, template it, and see if it matches!"""
        print("Waiting for image...")
        while self.finger.get_image() != af.OK:
            pass
        print("Templating...")
        if self.finger.image_2_tz(1) != af.OK:
            return False
        print("Searching...")
        if self.finger.finger_search() != af.OK:
            return False
        return True

    # pylint: disable=too-many-branches
    def get_fingerprint_detail(self):
        """Get a finger print image, template it, and see if it matches!
        This time, print out each error instead of just returning on failure"""
        print("Getting image...", end="")
        i = self.finger.get_image()
        if i == af.OK:
            print("Image taken")
        else:
            if i == af.NOFINGER:
                print("No finger detected")
            elif i == af.IMAGEFAIL:
                print("Imaging error")
            else:
                print("Other error")
            return False

        print("Templating...", end="")
        i = self.finger.image_2_tz(1)
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

        print("Searching...", end="")
        i = self.finger.finger_fast_search()
        # pylint: disable=no-else-return
        # This block needs to be refactored when it can be tested.
        if i == af.OK:
            print("Found fingerprint!")
            return True
        else:
            if i == af.NOTFOUND:
                print("No match found")
            else:
                print("Other error")
            return False

    def enroll_finger(self, location):
        """Take a 2 finger images and template it, then store in 'location'"""
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

    def get_num(self):
        """Use input() to get a valid number from 1 to 127.
        Retry till success!"""
        i = 0
        while (i > 127) or (i < 1):
            try:
                i = int(input("Enter ID # from 1-127: "))
            except ValueError:
                pass
        return i

    def main_loop(self, finger):
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

            if c == "e":
                self.enroll_finger(self.get_num())
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
            if c == "d":
                if finger.delete_model(self.get_num()) == af.OK:
                    print("Deleted!")
                else:
                    print("Failed to delete")
