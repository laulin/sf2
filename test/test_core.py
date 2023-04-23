import unittest
import os
import os.path
import shutil

from sf2.core import Core

TEST_DIR = "/tmp/test"
PUBLIC_KEY = "test/.ssh/id_rsa.pub"
PRIVATE_KEY = "test/.ssh/id_rsa"
AUTH_ID = "test@test"
PASSWORD = "password"

SOURCE = os.path.join(TEST_DIR, "source.txt")
ENCRYPTED = os.path.join(TEST_DIR, "encrypted.x")
OUTPUT = os.path.join(TEST_DIR, "output.txt")

class TestCore(unittest.TestCase):
    def setUp(self) -> None:
        try:
            shutil.rmtree(TEST_DIR)
        except:
            pass
        os.mkdir(TEST_DIR)
        with open(SOURCE, "w") as f:
            f.write("Example ! ")

    def test_encrypt(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED, PASSWORD)

    def test_encrypt_and_decrypt(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED, PASSWORD)

        core.decrypt(ENCRYPTED, OUTPUT, PASSWORD)
        with open(OUTPUT) as f:
            result = f.read()

        expected = "Example ! "

        self.assertEqual(result, expected)

    def test_verify(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED, PASSWORD)

        result = core.verify(ENCRYPTED, PASSWORD)

        self.assertTrue(result)

    def test_verify_failed(self):

        core = Core(_iterations=100)
        result = core.verify(SOURCE, PASSWORD)

        self.assertFalse(result)

    def test_open(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED, PASSWORD)
        program = "cat {filename} > "+OUTPUT
        core.open(ENCRYPTED, program, PASSWORD)
        
        with open(OUTPUT) as f:
            result = f.read()

        expected = "Example ! "

        self.assertEqual(result, expected)

    def test_ssh_add(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED, PASSWORD)

        core.ssh_add(ENCRYPTED, PASSWORD, PUBLIC_KEY)

    def test_ssh_rm(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED, PASSWORD)

        core.ssh_add(ENCRYPTED, PASSWORD, PUBLIC_KEY, AUTH_ID)
        core.ssh_rm(ENCRYPTED, AUTH_ID)

    def test_ssh_ls(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED, PASSWORD)

        core.ssh_add(ENCRYPTED, PASSWORD, PUBLIC_KEY, AUTH_ID)
        result = len(core.ssh_ls(ENCRYPTED))
        excepted = 1
        self.assertEqual(result, excepted)

    def test_decrypt_ssh(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED, PASSWORD)

        core.ssh_add(ENCRYPTED, PASSWORD, PUBLIC_KEY, AUTH_ID)

        core.decrypt_ssh(ENCRYPTED, OUTPUT, PRIVATE_KEY, auth_id=AUTH_ID)

        with open(OUTPUT) as f:
            result = f.read()

        expected = "Example ! "

        self.assertEqual(result, expected)

    def test_verify_ssh(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED, PASSWORD)

        core.ssh_add(ENCRYPTED, PASSWORD, PUBLIC_KEY, AUTH_ID)

        result = core.verify_ssh(ENCRYPTED, PRIVATE_KEY, None, AUTH_ID)
        self.assertTrue(result)

    def test_open_ssh(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED, PASSWORD)

        core.ssh_add(ENCRYPTED, PASSWORD, PUBLIC_KEY, AUTH_ID)

        program = "cat {filename} > "+OUTPUT
        core.open_ssh(ENCRYPTED, program, PRIVATE_KEY, None, AUTH_ID)
        
        with open(OUTPUT) as f:
            result = f.read()

        expected = "Example ! "

        self.assertEqual(result, expected)
