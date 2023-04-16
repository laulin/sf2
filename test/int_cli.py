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

    def test_encrypt(self):
        with open(SOURCE, "w") as f:
            f.write("Example ! ")

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", SOURCE, "-o", ENCRYPTED])

    def test_decrypt(self):
        
        plain = os.path.join(TEST_DIR, "plain.txt")

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", SOURCE, "-o", ENCRYPTED])

        subprocess.call(["python3", "-m", "sf2", "decrypt", "--master-password", "-m", "foobar", "-i", ENCRYPTED, "-o", plain])

        with open(plain) as f:
            result = f.read()

        expected = "Example ! "

        self.assertEqual(result, expected)

    def test_decrypt_ssh(self):

        plain = os.path.join(TEST_DIR, "plain.txt")

        with open(SOURCE, "w") as f:
            f.write("Example ! ")

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", SOURCE, "-o", ENCRYPTED])
        subprocess.call(["python3", "-m", "sf2", "ssh", "add", "-k", PUBLIC_KEY, "-m", "foobar", ENCRYPTED])
        subprocess.call(["python3", "-m", "sf2", "decrypt", "--ssh-key", "-y", PRIVATE_KEY, "-a", AUTH_ID, "-i", ENCRYPTED, "-o", plain])

        with open(plain) as f:
            result = f.read()

        expected = "Example ! "

        self.assertEqual(result, expected)

    def test_verify(self):

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", SOURCE, "-o", ENCRYPTED])
        result = subprocess.check_output(["python3", "-m", "sf2", "verify", "--master-password", "-m", "foobar", ENCRYPTED])
        expected = b'/tmp/test/encrypted.x : OK\n'

        self.assertEqual(result, expected)

    def test_verify_ssh(self):
        
        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", SOURCE, "-o", ENCRYPTED])
        subprocess.call(["python3", "-m", "sf2", "ssh", "add", "-k", PUBLIC_KEY, "-m", "foobar", ENCRYPTED])
        result = subprocess.check_output(["python3", "-m", "sf2", "verify", "--ssh-key", "-y", PRIVATE_KEY, "-a", AUTH_ID, ENCRYPTED])
        expected = b'/tmp/test/encrypted.x : OK\n'

        self.assertEqual(result, expected)

    def test_verify_failed(self):

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", SOURCE, "-o", ENCRYPTED])
        # use bad password
        try:
            subprocess.check_output(["python3", "-m", "sf2", "verify", "--master-password", "-m", "stuff", ENCRYPTED])
        except Exception as e:
            result = e.output
        
        expected = b'/tmp/test/encrypted.x : KO (Master key is invalid)\n'

        self.assertEqual(result, expected)

    def test_add_ssh(self):

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", SOURCE, "-o", ENCRYPTED])
        subprocess.check_output(["python3", "-m", "sf2", "ssh", "add", "-k", PUBLIC_KEY, "-m", "foobar", ENCRYPTED])

    def test_rm_ssh(self):

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", SOURCE, "-o", ENCRYPTED])
        subprocess.call(["python3", "-m", "sf2", "ssh", "add", "-k", PUBLIC_KEY, "-m", "foobar", ENCRYPTED])
        subprocess.call(["python3", "-m", "sf2", "ssh", "rm", "-a", AUTH_ID, ENCRYPTED])

    def test_ls_ssh(self):
        
        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", SOURCE, "-o", ENCRYPTED])
        subprocess.call(["python3", "-m", "sf2", "ssh", "add", "-k", PUBLIC_KEY, "-m", "foobar", ENCRYPTED])
        result = subprocess.check_output(["python3", "-m", "sf2", "ssh", "ls", ENCRYPTED])

        lines = result.splitlines()
        self.assertEqual(len(lines), 2 )

    def test_new(self):
        subprocess.call(["python3", "-m", "sf2", "new", "-m", "foobar", ENCRYPTED])

        self.assertTrue(os.path.exists(ENCRYPTED))

    def test_open(self):

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", SOURCE, "-o", ENCRYPTED])
        result = subprocess.check_output(["python3", "-m", "sf2", "open", "--master-password", "-m", "foobar", "-p", "cat", ENCRYPTED])
        expected = b'Example ! '

        self.assertEqual(result, expected)

    def test_open_ssh(self):

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", SOURCE, "-o", ENCRYPTED])
        subprocess.call(["python3", "-m", "sf2", "ssh", "add", "-m", "foobar", "-k", PUBLIC_KEY, "-a", AUTH_ID, ENCRYPTED])
        result = subprocess.check_output(["python3", "-m", "sf2", "open", "--ssh-key", "-y", PRIVATE_KEY, "-a", AUTH_ID, "-p", "cat", ENCRYPTED])
        expected = b'Example ! '

        self.assertEqual(result, expected)
