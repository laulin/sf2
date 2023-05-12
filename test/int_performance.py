import unittest
import os
import os.path
import shutil
import subprocess

TEST_DIR = "/tmp/test"
PUBLIC_KEY = "test/.ssh/id_rsa.pub"
PRIVATE_KEY = "test/.ssh/id_rsa"
AUTH_ID = "test@test"

SOURCE = os.path.join(TEST_DIR, "source.txt")
ENCRYPTED = os.path.join(TEST_DIR, "encrypted.x")

class TestCli(unittest.TestCase):
    def setUp(self) -> None:
        try:
            shutil.rmtree(TEST_DIR)
        except:
            pass
        os.mkdir(TEST_DIR)
        with open(SOURCE, "w") as f:
            f.write("Example ! ")

    def test_rm_ssh(self):

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-w", "-i", SOURCE, "-o", ENCRYPTED])
        for i in range(41):
            print(f"add user{i}")
            subprocess.call(["python3", "-m", "sf2", "ssh", "add", "-k", PUBLIC_KEY, "-a", f"user{i}@test", "-m", "foobar", ENCRYPTED])
        print(f"remove user0")
        subprocess.call(["python3", "-m", "sf2", "ssh", "rm", "-m", "foobar", "-p", "user0@test", ENCRYPTED])

    