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

    def test_decrypt_ssh(self):
        source = os.path.join(TEST_DIR, "source.txt")
        encrypted = os.path.join(TEST_DIR, "encrypted.x")
        plain = os.path.join(TEST_DIR, "plain.txt")

        with open(source, "w") as f:
            f.write("Example ! ")

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", source, "-o", encrypted])
        subprocess.call(["python3", "-m", "sf2", "ssh", "add", "-k", "test/.ssh/id_rsa.pub", "-m", "foobar", encrypted])
        subprocess.call(["python3", "-m", "sf2", "decrypt", "--ssh-key", "-y", "test/.ssh/id_rsa", "-a", "test@test", "-i", encrypted, "-o", plain])

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

    def test_verify_ssh(self):
        source = os.path.join(TEST_DIR, "source.txt")
        encrypted = os.path.join(TEST_DIR, "encrypted.x")

        with open(source, "w") as f:
            f.write("Example ! ")

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", source, "-o", encrypted])
        subprocess.call(["python3", "-m", "sf2", "ssh", "add", "-k", "test/.ssh/id_rsa.pub", "-m", "foobar", encrypted])
        result = subprocess.check_output(["python3", "-m", "sf2", "verify", "--ssh-key", "-y", "test/.ssh/id_rsa", "-a", "test@test", encrypted])
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

    def test_add_ssh(self):
        source = os.path.join(TEST_DIR, "source.txt")
        encrypted = os.path.join(TEST_DIR, "encrypted.x")

        with open(source, "w") as f:
            f.write("Example ! ")

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", source, "-o", encrypted])
        subprocess.check_output(["python3", "-m", "sf2", "ssh", "add", "-k", "test/.ssh/id_rsa.pub", "-m", "foobar", encrypted])

    def test_rm_ssh(self):
        source = os.path.join(TEST_DIR, "source.txt")
        encrypted = os.path.join(TEST_DIR, "encrypted.x")

        with open(source, "w") as f:
            f.write("Example ! ")

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", source, "-o", encrypted])
        subprocess.call(["python3", "-m", "sf2", "ssh", "add", "-k", "test/.ssh/id_rsa.pub", "-m", "foobar", encrypted])
        subprocess.call(["python3", "-m", "sf2", "ssh", "rm", "-a", "test@test", encrypted])

    def test_ls_ssh(self):
        source = os.path.join(TEST_DIR, "source.txt")
        encrypted = os.path.join(TEST_DIR, "encrypted.x")

        with open(source, "w") as f:
            f.write("Example ! ")

        subprocess.call(["python3", "-m", "sf2", "encrypt", "-m", "foobar", "-i", source, "-o", encrypted])
        subprocess.call(["python3", "-m", "sf2", "ssh", "add", "-k", "test/.ssh/id_rsa.pub", "-m", "foobar", encrypted])
        result = subprocess.check_output(["python3", "-m", "sf2", "ssh", "ls", encrypted])

        lines = result.splitlines()
        self.assertEqual(len(lines), 2 )
