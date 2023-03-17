import unittest
import os
from contextlib import suppress
import logging 

from sf2.container import Container

WORKING_FILE = "/tmp/test.x"
SECRET = "secret"
ITERATIONS = 100

#logging.basicConfig(level=logging.DEBUG)

class TestContainer(unittest.TestCase):


    def tearDown(self) -> None:
        with suppress(FileNotFoundError):
            os.remove(WORKING_FILE)

    def test_create(self):
        c = Container(WORKING_FILE)
        c.create(SECRET, ITERATIONS)

    def test_create_fail(self):
        c = Container(WORKING_FILE)
        c.create(SECRET, ITERATIONS)

        try:
            c.create(SECRET, ITERATIONS)
            self.assertTrue(False)
        except FileExistsError:
            pass

    def test_read_master_password(self):
        c = Container(WORKING_FILE)
        c.create(SECRET, ITERATIONS)
        results = c.read_master_password(SECRET, ITERATIONS)

        expected = b""

        self.assertEqual(results, expected)

    def test_create_write_read_from_password(self):
        c = Container(WORKING_FILE)
        c.create(SECRET, ITERATIONS)
        c.write_master_password(b"hello", SECRET, ITERATIONS)
        results = c.read_master_password(SECRET, ITERATIONS)

        expected = b"hello"

        self.assertEqual(results, expected)
        
