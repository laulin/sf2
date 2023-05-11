import unittest
import os
from contextlib import suppress

from sf2.container_ssh import ContainerSSH
from sf2.json_support import JsonSupport
from sf2.container_base import ContainerBase


WORKING_FILE = "/tmp/test.x"
SECRET = "secret"
ITERATIONS = 100
PRIVATE_SSH_KEY = "./test/.ssh/id_rsa"
PUBLIC_SSH_KEY = "./test/.ssh/id_rsa.pub"


class TestContainerSSH(unittest.TestCase):

    def setUp(self) -> None:
        support = JsonSupport(WORKING_FILE)
        self.base = ContainerBase(support)
        self.c = ContainerSSH(self.base)

    def tearDown(self) -> None:
        with suppress(FileNotFoundError):
            os.remove(WORKING_FILE)

   
    def test_add_ssh_key(self):
        
        self.base.create(SECRET, False, _iterations=ITERATIONS)
        self.c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, _iterations=ITERATIONS)

    def test_add_double_ssh_key(self):
        
        self.base.create(SECRET, False, _iterations=ITERATIONS)
        self.c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, _iterations=ITERATIONS)

        try:
            self.base.add_ssh_key(SECRET, PUBLIC_SSH_KEY, _iterations=ITERATIONS)
            self.assertTrue(False)
        except Exception as e:
            pass

    def test_create_write_read_private_ssh_key(self):
        
        self.base.create(SECRET, False, _iterations=ITERATIONS)
        self.c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, _iterations=ITERATIONS)
        
        self.c.write(b"hello", "test@test", PRIVATE_SSH_KEY, None)
        results = self.c.read("test@test", PRIVATE_SSH_KEY, None)

        expected = b"hello"

        self.assertEqual(results, expected)

    def test_remove_ssh_key_ok(self):
        self.base.create(SECRET, False, _iterations=ITERATIONS)
        self.c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, _iterations=ITERATIONS)
        self.c.remove_ssh_key(SECRET, "test@test", _iterations=ITERATIONS)

    def test_remove_ssh_key_ko(self):
        
        self.base.create(SECRET, False, _iterations=ITERATIONS)
        
        try:
            self.c.remove_ssh_key(SECRET, "test@test", _iterations=ITERATIONS)
            self.assertTrue(False)
        except:
            pass

    def test_create_write_read_private_ssh_key(self):
        
        self.base.create(SECRET, False, _iterations=ITERATIONS)
        self.c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, _iterations=ITERATIONS)
        
        results = self.c.list_ssh_key()

        self.assertTrue("test@test" in results)

    def test_update_master_key(self):
        
        self.base.create(SECRET, False, _iterations=ITERATIONS)
        self.c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, _iterations=ITERATIONS)
        
        self.c.write(b"hello", "test@test", PRIVATE_SSH_KEY, None)

        self.base.change_password(SECRET, "NEW_SECRET", ITERATIONS)        
        self.c.update_master_key("NEW_SECRET", ITERATIONS)

        results = self.c.read("test@test", PRIVATE_SSH_KEY, None)

        expected = b"hello"

        self.assertEqual(results, expected)

    def test_ls_with_exact_match(self):
        
        self.base.create(SECRET, False, _iterations=ITERATIONS)
        self.c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, _iterations=ITERATIONS)
        
        results = self.c.list_ssh_key("test@test")

        self.assertEqual(["test@test"], list(results))

    def test_ls_with_regex(self):
        
        self.base.create(SECRET, False, _iterations=ITERATIONS)
        self.c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, _iterations=ITERATIONS)
        
        results = self.c.list_ssh_key(".*@test")

        self.assertEqual(["test@test"], list(results))

    def test_ls_no_match(self):
        
        self.base.create(SECRET, False, _iterations=ITERATIONS)
        self.c.add_ssh_key(SECRET, PUBLIC_SSH_KEY, _iterations=ITERATIONS)
        
        results = self.c.list_ssh_key("tesu.*")

        self.assertEqual([], list(results))
        