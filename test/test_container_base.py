import unittest
import os
from contextlib import suppress

from cryptography.exceptions import InvalidSignature

from sf2.json_support import JsonSupport
from sf2.msgpack_support import MsgpackSupport
from sf2.container_base import ContainerBase

WORKING_FILE = "/tmp/test_container.x"
SECRET = "secret"
ITERATIONS = 100

#logging.basicConfig(level=logging.DEBUG)

class TestContainer(unittest.TestCase):

    def setUp(self) -> None:
        support = JsonSupport(WORKING_FILE)
        self.c = ContainerBase(support)

    def tearDown(self) -> None:
        with suppress(FileNotFoundError):
            os.remove(WORKING_FILE)

    def test_create(self):
        self.c.create(SECRET, False, ITERATIONS)

    def test_create_fail(self):
        self.c.create(SECRET, False, ITERATIONS)

        try:
            self.c.create(SECRET, False, ITERATIONS)
            self.assertTrue(False)
        except Exception:
            pass

    def test_read(self):
        self.c.create(SECRET, False, ITERATIONS)
        results = self.c.read(SECRET, ITERATIONS)

        expected = b""

        self.assertEqual(results, expected)

    def test_create_write_read_from_password(self):
        self.c.create(SECRET, False, ITERATIONS)
        self.c.write(b"hello", SECRET, ITERATIONS)
        results = self.c.read(SECRET, ITERATIONS)

        expected = b"hello"

        self.assertEqual(results, expected)

    def test_signature_ok(self):
        container = {"auth":{}}
        
        self.c.set_master_key_signature(container, b"xxx")
        self.c.check_master_key_signature(container, b"xxx")

    def test_signature_ko(self):
        container = {"auth":{}}

        self.c.set_master_key_signature(container, b"xxx")

        try:
            self.c.check_master_key_signature(container, b"yyy")
            self.assertTrue(False)
        except InvalidSignature:
            pass

    def test_create_write_read_with_msgpack(self):
        support = MsgpackSupport(WORKING_FILE)
        self.c = ContainerBase(support)

        self.c.create(SECRET, False, ITERATIONS)
        self.c.write(b"hello", SECRET, ITERATIONS)
        results = self.c.read(SECRET, ITERATIONS)

        expected = b"hello"

        self.assertEqual(results, expected)
        