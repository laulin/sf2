import unittest
import os
import shutil
import logging
import time
import multiprocessing

from sf2.openinram import OpenInRAM
from sf2.json_support import JsonSupport
from sf2.file_object import FileObject
from sf2.core import Core

TEST_DIR = "/tmp/test_open_ssh"
PUBLIC_KEY = "test/.ssh/id_rsa.pub"
PRIVATE_KEY = "test/.ssh/id_rsa"
AUTH_ID = "test@test"
PASSWORD = "password"

SOURCE = os.path.join(TEST_DIR, "source.txt")
ENCRYPTED = os.path.join(TEST_DIR, "encrypted.x")
OUTPUT = os.path.join(TEST_DIR, "output.txt")

class TestOpenInRAM(unittest.TestCase):
    def setUp(self) -> None:
        try:
            shutil.rmtree(TEST_DIR)
        except:
            pass
        os.mkdir(TEST_DIR)
        with open(SOURCE, "w") as f:
            f.write("Example ! ")

    def test_interpole_command(self):
        oir = OpenInRAM(None, "")
        result = oir.interpole_command("cat {filename}")
        expected = "cat {filename}"

        self.assertEqual(result, expected)

    def test_interpole_command_bracket(self):
        oir = OpenInRAM(None, "")
        result = oir.interpole_command("cat [ filename ]")
        expected = "cat {filename}"

        self.assertEqual(result, expected)

    def test_interpole_command_default(self):
        oir = OpenInRAM(None, "")
        result = oir.interpole_command("cat")
        expected = "cat {filename}"

        self.assertEqual(result, expected)

    def test_open(self):
        c = Core(100)
        c.encrypt(SOURCE, ENCRYPTED, PASSWORD, "json")

        support = JsonSupport(ENCRYPTED)
        file_object = FileObject(support, PASSWORD, 100)

        open_in_ram = OpenInRAM(file_object, "cat {filename} > /tmp/test_open_ssh/output.txt")
        open_in_ram.run()

        with open("/tmp/test_open_ssh/output.txt") as f:
            results = f.read()

        expected = "Example ! "
        self.assertEqual(results, expected)

    def test_open_dual(self):
        c = Core(100)
        c.encrypt(SOURCE, ENCRYPTED, PASSWORD, "json")

        support = JsonSupport(ENCRYPTED)
        file_object = FileObject(support, PASSWORD, 100)

        open_in_ram_w = OpenInRAM(file_object, 'echo "hello" > {filename} && sleep 1')
        process = multiprocessing.Process(target=open_in_ram_w.run)
        process.start()

        time.sleep(0.5)

        open_in_ram_r = OpenInRAM(file_object, "cat {filename}  > /tmp/test_open_ssh/output.txt")
        open_in_ram_r.run()

        with open("/tmp/test_open_ssh/output.txt") as f:
            results = f.read()

        process.join()

        expected = "hello\n"
        self.assertEqual(results, expected)

    def test_open_dual_failed(self):
        #logging.basicConfig(level=logging.DEBUG)
        c = Core(100)
        c.encrypt(SOURCE, ENCRYPTED, PASSWORD, "json")

        support = JsonSupport(ENCRYPTED)
        file_object = FileObject(support, PASSWORD, 100)

        open_in_ram_w = OpenInRAM(file_object, 'echo "hello" > {filename} && sleep 1')
        process = multiprocessing.Process(target=open_in_ram_w.run)
        process.start()

        time.sleep(0.5)

        open_in_ram_r = OpenInRAM(file_object, 'echo "world" > {filename}')
        open_in_ram_r.run()

        process.join()
