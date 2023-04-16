import unittest
import os
from contextlib import suppress


from sf2.json_support import JsonSupport
from sf2.container_base import ContainerBase
from sf2.container_ssh import ContainerSSH
from sf2.ssh_file_object import SSHFileObject

ENCRYPTED_FILE = "/tmp/test_ssh_file_object.x"
PLAIN_FILE = "/tmp/test_ssh_file_object.txt"
SECRET = "secret"
PUBLIC_KEY = "test/.ssh/id_rsa.pub"
PRIVATE_KEY = "test/.ssh/id_rsa"
ITERATIONS = 100
AUTH_ID = "test@test"

#logging.basicConfig(level=logging.DEBUG)

class TestSSHFileObject(unittest.TestCase):

    def setUp(self) -> None:
        with suppress(FileNotFoundError):
            os.remove(ENCRYPTED_FILE)

        with suppress(FileNotFoundError):
            os.remove(PLAIN_FILE)

        support = JsonSupport(ENCRYPTED_FILE)
        self.base = ContainerBase(support)
        self.c = ContainerSSH(self.base)

        self.base.create(SECRET, False, _iterations=ITERATIONS)
        self.c.add_ssh_key(SECRET, PUBLIC_KEY, AUTH_ID, _iterations=ITERATIONS)
        self.base.write(b"hello", SECRET, ITERATIONS)

    def tearDown(self) -> None:
        with suppress(FileNotFoundError):
            os.remove(ENCRYPTED_FILE)

        with suppress(FileNotFoundError):
            os.remove(PLAIN_FILE)

    def test_decrypt(self):

        support = JsonSupport(ENCRYPTED_FILE)
        fo = SSHFileObject(support, AUTH_ID, PRIVATE_KEY)
        results = fo.decrypt()

        expected = b"hello"
        self.assertEqual(results, expected)

    def test_encrypt(self):

        support = JsonSupport(ENCRYPTED_FILE)
        fo = SSHFileObject(support, AUTH_ID, PRIVATE_KEY)
        data = fo.decrypt()

        with open(PLAIN_FILE, "wb") as f:
            f.write(data + b" you")

        fo.encrypt(PLAIN_FILE)

        results = fo.decrypt()

        expected = b"hello you"
        self.assertEqual(results, expected)