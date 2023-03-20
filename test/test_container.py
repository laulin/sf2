import unittest
import os
from contextlib import suppress
import logging 

from sf2.container import Container
from sf2.cipher import Cipher

WORKING_FILE = "/tmp/test.x"
SECRET = "secret"
ITERATIONS = 100
PRIVATE_SSH_KEY = "./test/.ssh/id_rsa"
PUBLIC_SSH_KEY = "./test/.ssh/id_rsa.pub"

#logging.basicConfig(level=logging.DEBUG)

class TestContainer(unittest.TestCase):


    def tearDown(self) -> None:
        with suppress(FileNotFoundError):
            os.remove(WORKING_FILE)

    def test_create(self):
        c = Container(WORKING_FILE)
        c.create(SECRET, False, ITERATIONS)

    def test_create_fail(self):
        c = Container(WORKING_FILE)
        c.create(SECRET, False, ITERATIONS)

        try:
            c.create(SECRET, False, ITERATIONS)
            self.assertTrue(False)
        except FileExistsError:
            pass

    def test_read_master_password(self):
        c = Container(WORKING_FILE)
        c.create(SECRET, False, ITERATIONS)
        results = c.read_master_password(SECRET, ITERATIONS)

        expected = b""

        self.assertEqual(results, expected)

    def test_create_write_read_from_password(self):
        c = Container(WORKING_FILE)
        c.create(SECRET, False, ITERATIONS)
        c.write_master_password(b"hello", SECRET, ITERATIONS)
        results = c.read_master_password(SECRET, ITERATIONS)

        expected = b"hello"

        self.assertEqual(results, expected)

    def test_add_ssh_key(self):
        c = Container(WORKING_FILE)
        c.create(SECRET, False, ITERATIONS)
        c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, PRIVATE_SSH_KEY, None, ITERATIONS)

    def test_add_double_ssh_key(self):
        c = Container(WORKING_FILE)
        c.create(SECRET, False, ITERATIONS)
        c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, PRIVATE_SSH_KEY, None, ITERATIONS)

        try:
            c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, PRIVATE_SSH_KEY, None, ITERATIONS)
            self.assertTrue(False)
        except Exception as e:
            print(e)
            pass

    def test_create_write_read_PRIVATE_SSH_KEY(self):
        c = Container(WORKING_FILE)
        c.create(SECRET, False, ITERATIONS)
        c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, PRIVATE_SSH_KEY, None, ITERATIONS)
        
        c.write_ssh_key(b"hello", PUBLIC_SSH_KEY, PRIVATE_SSH_KEY)
        results = c.read_ssh_key(PUBLIC_SSH_KEY, PRIVATE_SSH_KEY)

        expected = b"hello"

        self.assertEqual(results, expected)

    def test_convertion_v1_to_v2(self):

        # create legacy container
        with open(WORKING_FILE, "w") as f:
            container = Cipher().encrypt(SECRET, b"hello")
            f.write(container)

        c = Container(WORKING_FILE)
        c.convert_v1_to_v2(SECRET, ITERATIONS)

        results = c.read_master_password(SECRET, ITERATIONS)

        expected = b"hello"

        self.assertEqual(results, expected)