import unittest
import os
from contextlib import suppress


from sf2.json_support import JsonSupport
from sf2.container_base import ContainerBase
from sf2.file_object import FileObject

ENCRYPTED_FILE = "/tmp/test.x"
PLAIN_FILE = "/tmp/test.txt"
SECRET = "secret"
ITERATIONS = 100

#logging.basicConfig(level=logging.DEBUG)

class TestFileObject(unittest.TestCase):

    def setUp(self) -> None:
        support = JsonSupport(ENCRYPTED_FILE)
        self.c = ContainerBase(support)
        self.c.create(SECRET, False, ITERATIONS)
        self.c.write(b"hello", SECRET, ITERATIONS)

    def tearDown(self) -> None:
        with suppress(FileNotFoundError):
            os.remove(ENCRYPTED_FILE)

        with suppress(FileNotFoundError):
            os.remove(PLAIN_FILE)

    def test_decrypt(self):
        support = JsonSupport(ENCRYPTED_FILE)
        fo = FileObject(support, SECRET, ITERATIONS)
        results = fo.decrypt()

        expected = b"hello"
        self.assertEqual(results, expected)

    def test_encrypt(self): 
        support = JsonSupport(ENCRYPTED_FILE)
        fo = FileObject(support, SECRET, ITERATIONS)
        data = fo.decrypt()

        with open(PLAIN_FILE, "wb") as f:
            f.write(data + b" you")

        fo.encrypt(PLAIN_FILE)

        results = fo.decrypt()

        expected = b"hello you"
        self.assertEqual(results, expected)