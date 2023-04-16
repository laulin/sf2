import unittest
import os
import os.path
import shutil
import subprocess

TEST_DIR = "/tmp/test"

class TestCli(unittest.TestCase):
    def setUp(self) -> None:
        try:
            shutil.rmtree(TEST_DIR)
        except:
            pass
        os.mkdir(TEST_DIR)

    def tearDown(self) -> None:
        shutil.rmtree(TEST_DIR)

    def test_encrypt(self):
        source = os.path.join(TEST_DIR, "source.txt")
        encrypted = os.path.join(TEST_DIR, "encrypted.x")

        with open(source, "w") as f:
            f.write("Example ! ")

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", source, "-o", encrypted])

    def test_decrypt(self):
        source = os.path.join(TEST_DIR, "source.txt")
        encrypted = os.path.join(TEST_DIR, "encrypted.x")
        plain = os.path.join(TEST_DIR, "plain.txt")

        with open(source, "w") as f:
            f.write("Example ! ")

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", source, "-o", encrypted])

        subprocess.call(["python3", "-m", "sf2", "decrypt", "--master-password", "-m", "foobar", "-i", encrypted, "-o", plain])

        with open(plain) as f:
            result = f.read()

        expected = "Example ! "

        self.assertEqual(result, expected)

    def test_verify(self):
        source = os.path.join(TEST_DIR, "source.txt")
        encrypted = os.path.join(TEST_DIR, "encrypted.x")

        with open(source, "w") as f:
            f.write("Example ! ")

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", source, "-o", encrypted])
        result = subprocess.check_output(["python3", "-m", "sf2", "verify", "--master-password", "-m", "foobar", encrypted])
        expected = b'/tmp/test/encrypted.x : OK\n'

        self.assertEqual(result, expected)

    def test_verify_failed(self):
        source = os.path.join(TEST_DIR, "source.txt")
        encrypted = os.path.join(TEST_DIR, "encrypted.x")

        with open(source, "w") as f:
            f.write("Example ! ")

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", source, "-o", encrypted])
        # use bad password
        try:
            subprocess.check_output(["python3", "-m", "sf2", "verify", "--master-password", "-m", "stuff", encrypted])
        except Exception as e:
            result = e.output
        
        expected = b'/tmp/test/encrypted.x : KO (Master key is invalid)\n'

        self.assertEqual(result, expected)