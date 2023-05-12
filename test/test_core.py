import unittest
import os
import os.path
import shutil

from sf2.core import Core

TEST_DIR = "/tmp/test_core"
PUBLIC_KEY = "test/.ssh/id_rsa.pub"
PRIVATE_KEY = "test/.ssh/id_rsa"
AUTH_ID = "test@test"
PASSWORD = "password"

SOURCE = os.path.join(TEST_DIR, "source.txt")
ENCRYPTED_FILE = os.path.join(TEST_DIR, "encrypted.x")
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
        core.encrypt(SOURCE, ENCRYPTED_FILE, PASSWORD)

    def test_new(self):

        core = Core(_iterations=100)
        core.new(ENCRYPTED_FILE, PASSWORD)

    def test_encrypt_and_decrypt(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED_FILE, PASSWORD)

        core.decrypt(ENCRYPTED_FILE, OUTPUT, PASSWORD)
        with open(OUTPUT) as f:
            result = f.read()

        expected = "Example ! "

        self.assertEqual(result, expected)

    def test_verify(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED_FILE, PASSWORD)

        result = core.verify(ENCRYPTED_FILE, PASSWORD)

        self.assertTrue(result)

    def test_verify_failed(self):

        core = Core(_iterations=100)
        result = core.verify(SOURCE, PASSWORD)

        self.assertFalse(result)

    def test_open(self):
        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED_FILE, PASSWORD)
        program = "cat {filename} > "+OUTPUT
        core.open(ENCRYPTED_FILE, program, PASSWORD)
        
        with open(OUTPUT) as f:
            result = f.read()
        expected = "Example ! "

        self.assertEqual(result, expected)

    def test_ssh_add(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED_FILE, PASSWORD)

        core.ssh_add(ENCRYPTED_FILE, PASSWORD, PUBLIC_KEY)

    def test_ssh_rm(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED_FILE, PASSWORD)

        core.ssh_add(ENCRYPTED_FILE, PASSWORD, PUBLIC_KEY, AUTH_ID)
        core.ssh_rm(ENCRYPTED_FILE, PASSWORD, AUTH_ID)

    def test_ssh_ls(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED_FILE, PASSWORD)

        core.ssh_add(ENCRYPTED_FILE, PASSWORD, PUBLIC_KEY, AUTH_ID)
        result = len(core.ssh_ls(ENCRYPTED_FILE))
        excepted = 1
        self.assertEqual(result, excepted)

    def test_ssh_ls_full_match(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED_FILE, PASSWORD)

        core.ssh_add(ENCRYPTED_FILE, PASSWORD, PUBLIC_KEY, AUTH_ID)
        result = len(core.ssh_ls(ENCRYPTED_FILE, "test@test"))
        excepted = 1
        self.assertEqual(result, excepted)

    def test_decrypt_ssh(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED_FILE, PASSWORD)

        core.ssh_add(ENCRYPTED_FILE, PASSWORD, PUBLIC_KEY, AUTH_ID)

        core.decrypt_ssh(ENCRYPTED_FILE, OUTPUT, PRIVATE_KEY, auth_id=AUTH_ID)

        with open(OUTPUT) as f:
            result = f.read()

        expected = "Example ! "

        self.assertEqual(result, expected)

    def test_verify_ssh(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED_FILE, PASSWORD)

        core.ssh_add(ENCRYPTED_FILE, PASSWORD, PUBLIC_KEY, AUTH_ID)

        result = core.verify_ssh(ENCRYPTED_FILE, PRIVATE_KEY, None, AUTH_ID)
        self.assertTrue(result)

    def test_open_ssh(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED_FILE, PASSWORD)

        core.ssh_add(ENCRYPTED_FILE, PASSWORD, PUBLIC_KEY, AUTH_ID)

        program = "cat {filename} > "+OUTPUT
        core.open_ssh(ENCRYPTED_FILE, program, PRIVATE_KEY, None, AUTH_ID)
        
        with open(OUTPUT) as f:
            result = f.read()

        expected = "Example ! "

        self.assertEqual(result, expected)

    def test_change_password(self):

        core = Core(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED_FILE, PASSWORD)

        core.ssh_add(ENCRYPTED_FILE, PASSWORD, PUBLIC_KEY)

        core.change_password(ENCRYPTED_FILE, PASSWORD, "NEW SECRET")

        result = core.verify_ssh(ENCRYPTED_FILE, PRIVATE_KEY, None, AUTH_ID)
        self.assertTrue(result)