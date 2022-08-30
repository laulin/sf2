import unittest
import os
from contextlib import suppress
import logging 

from sf2.fernetramfile import FernetRAMFile

WORKING_FILE = "/tmp/test.x"
SECRET = b"secret"
ITERATIONS = 100

#logging.basicConfig(level=logging.DEBUG)

class TestFernetFile(unittest.TestCase):


    def tearDown(self) -> None:
        with suppress(FileNotFoundError):
            os.remove(WORKING_FILE)

    def test_write_utf8(self):
        with FernetRAMFile(WORKING_FILE, SECRET, "w", ITERATIONS) as f:
            f.write("Hello")

    def test_write_bytes(self):
        with FernetRAMFile(WORKING_FILE, SECRET, "wb", ITERATIONS) as f:
            f.write(b"Hello")

    def test_write_read_utf8(self):
        with FernetRAMFile(WORKING_FILE, SECRET, "w", ITERATIONS) as f:
            f.write("Hello")

        with FernetRAMFile(WORKING_FILE, SECRET, "r", ITERATIONS) as f:
            result = f.read()

        expected = "Hello"
        self.assertEqual(result, expected)

    def test_write_read_bytes(self):
        with FernetRAMFile(WORKING_FILE, SECRET, "wb", ITERATIONS) as f:
            f.write(b"Hello")

        with FernetRAMFile(WORKING_FILE, SECRET, "rb", ITERATIONS) as f:
            result = f.read()

        expected = b"Hello"
        self.assertEqual(result, expected)
        
