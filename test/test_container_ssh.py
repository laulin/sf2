import unittest
import os
from contextlib import suppress
import logging 

from cryptography.exceptions import InvalidSignature

from sf2.container_ssh import ContainerSSH
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

   
    def test_add_ssh_key(self):
        c = ContainerSSH(WORKING_FILE)
        c.create(SECRET, False, _iterations=ITERATIONS)
        c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, _iterations=ITERATIONS)

    def test_add_double_ssh_key(self):
        c = ContainerSSH(WORKING_FILE)
        c.create(SECRET, False, _iterations=ITERATIONS)
        c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, _iterations=ITERATIONS)

        try:
            c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, _iterations=ITERATIONS)
            self.assertTrue(False)
        except Exception as e:
            pass

    def test_create_write_read_private_ssh_key(self):
        c = ContainerSSH(WORKING_FILE)
        c.create(SECRET, False, _iterations=ITERATIONS)
        c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, _iterations=ITERATIONS)
        
        c.write(b"hello", "test@test", PRIVATE_SSH_KEY, None)
        results = c.read("test@test", PRIVATE_SSH_KEY, None)

        expected = b"hello"

        self.assertEqual(results, expected)
        