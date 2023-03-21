import unittest
import os
from contextlib import suppress

from cryptography.exceptions import InvalidSignature

from sf2.container_base import ContainerBase

WORKING_FILE = "/tmp/test.x"
SECRET = "secret"
ITERATIONS = 100

#logging.basicConfig(level=logging.DEBUG)

class TestContainer(unittest.TestCase):


    def tearDown(self) -> None:
        with suppress(FileNotFoundError):
            os.remove(WORKING_FILE)

    def test_create(self):
        c = ContainerBase(WORKING_FILE)
        c.create(SECRET, False, ITERATIONS)

    def test_create_fail(self):
        c = ContainerBase(WORKING_FILE)
        c.create(SECRET, False, ITERATIONS)

        try:
            c.create(SECRET, False, ITERATIONS)
            self.assertTrue(False)
        except FileExistsError:
            pass

    def test_read(self):
        c = ContainerBase(WORKING_FILE)
        c.create(SECRET, False, ITERATIONS)
        results = c.read(SECRET, ITERATIONS)

        expected = b""

        self.assertEqual(results, expected)

    def test_create_write_read_from_password(self):
        c = ContainerBase(WORKING_FILE)
        c.create(SECRET, False, ITERATIONS)
        c.write(b"hello", SECRET, ITERATIONS)
        results = c.read(SECRET, ITERATIONS)

        expected = b"hello"

        self.assertEqual(results, expected)

    def test_signature_ok(self):
        container = {"auth":{}}
        c = ContainerBase(WORKING_FILE)

        c.set_master_key_signature(container, b"xxx")
        c.check_master_key_signature(container, b"xxx")

    def test_signature_ko(self):
        container = {"auth":{}}
        c = ContainerBase(WORKING_FILE)

        c.set_master_key_signature(container, b"xxx")

        try:
            c.check_master_key_signature(container, b"yyy")
            self.assertTrue(False)
        except InvalidSignature:
            pass
        