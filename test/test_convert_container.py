import unittest
import os

from sf2.convert_container import convert_container
from sf2.cipher import Cipher
from sf2.core import Core

PASSWORD = "foobar"
LEGACY_FILE = "/tmp/legacy.z"
NEW_FILE = "/tmp/new.x"
PLAIN_FILE = "/tmp/plain.txt"

class TestCore(unittest.TestCase):
    def tearDown(self) -> None:
        for f in [LEGACY_FILE, NEW_FILE, PLAIN_FILE]:
            try:
                os.remove(f)
            except:
                pass
    
    def test_convert(self):
        c = Cipher()

        with open(LEGACY_FILE, "w") as f:
            f.write(c.encrypt(PASSWORD, b"sample !"))

        convert_container(LEGACY_FILE, NEW_FILE, PASSWORD, _iterations=100)

        core = Core(_iterations=100)

        core.decrypt(NEW_FILE, PLAIN_FILE, PASSWORD)

        with open(PLAIN_FILE) as f:
            results = f.read()

        expected = "sample !"

        self.assertEqual(results, expected)


        
