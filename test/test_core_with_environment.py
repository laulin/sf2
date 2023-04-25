import unittest
import os
import os.path
import shutil

from sf2.core_with_environment import CoreWithEnvironment

TEST_DIR = "/tmp/test_core_with_env"
PUBLIC_KEY = os.path.join(os.getcwd(), "test/.ssh/id_rsa.pub")
PRIVATE_KEY = os.path.join(os.getcwd(), "test/.ssh/id_rsa")
CUSTOM_PUBLIC_KEY = os.path.join(os.getcwd(), "test/.ssh/custom_rsa.pub")
CUSTOM_PRIVATE_KEY = os.path.join(os.getcwd(), "test/.ssh/custom_rsa")
CONFIG_FILE_PATH = os.path.join(os.getcwd(), "test/.sf2/config.yaml")
CUSTOM_CONFIG_FILE_PATH = os.path.join(os.getcwd(), "test/.sf2/custom_config.yaml")
AUTH_ID = "test@test"
PASSWORD = "password"

SOURCE = os.path.join(TEST_DIR, "source.txt")
ENCRYPTED = os.path.join(TEST_DIR, "encrypted.x")
OUTPUT = os.path.join(TEST_DIR, "output.txt")

CUSTOM_CONFIG_FILE = f"""
{ENCRYPTED}:
  private_key_file : {CUSTOM_PRIVATE_KEY}
  auth_id: foo@bar
  program: cat [filename] > {OUTPUT}
"""

CONFIG_FILE = f"""
{ENCRYPTED}:
  private_key_file : {PRIVATE_KEY}
  auth_id: test@test
  program: cat [filename] > {OUTPUT}
"""

class TestCore(unittest.TestCase):
    def setUp(self) -> None:
        try:
            shutil.rmtree(TEST_DIR)
        except:
            pass
        os.mkdir(TEST_DIR)
        with open(SOURCE, "w") as f:
            f.write("Example ! ")

        with open(CONFIG_FILE_PATH, "w") as f:
            f.write(CONFIG_FILE)

        with open(CUSTOM_CONFIG_FILE_PATH, "w") as f:
            f.write(CUSTOM_CONFIG_FILE)

        core = CoreWithEnvironment(_iterations=100)
        core.encrypt(SOURCE, ENCRYPTED, PASSWORD)


    def test_ssh_add(self):
        core = CoreWithEnvironment(_iterations=100, 
                                   default_public_key=PUBLIC_KEY, 
                                   default_private_key=PRIVATE_KEY, 
                                   default_auth_id="test@test", 
                                   default_config_file=CONFIG_FILE_PATH)
        core.ssh_add(ENCRYPTED, PASSWORD)
        results = core.ssh_ls(ENCRYPTED)
        auth_id = results[0][0]

        expected = "test@test"
        self.assertEqual(auth_id, expected)

    def test_ssh_add_custom_1(self):
        core = CoreWithEnvironment(_iterations=100, 
                                   default_public_key=PUBLIC_KEY, 
                                   default_private_key=PRIVATE_KEY, 
                                   default_auth_id="test@test", 
                                   default_config_file=CONFIG_FILE_PATH)
        core.ssh_add(ENCRYPTED, PASSWORD, CUSTOM_PUBLIC_KEY)
        results = core.ssh_ls(ENCRYPTED)
        auth_id = results[0][0]

        expected = "foo@bar"
        self.assertEqual(auth_id, expected)

    def test_ssh_add_custom_2(self):
        core = CoreWithEnvironment(_iterations=100, 
                                   default_public_key=PUBLIC_KEY, 
                                   default_private_key=PRIVATE_KEY, 
                                   default_auth_id="test@test", 
                                   default_config_file=CONFIG_FILE_PATH)
        core.ssh_add(ENCRYPTED, PASSWORD, CUSTOM_PUBLIC_KEY, "xx@yy")
        results = core.ssh_ls(ENCRYPTED)
        auth_id = results[0][0]

        expected = "xx@yy"
        self.assertEqual(auth_id, expected)

    def test_ssh_rm(self):

        core = CoreWithEnvironment(_iterations=100, 
                                   default_public_key=PUBLIC_KEY, 
                                   default_private_key=PRIVATE_KEY, 
                                   default_auth_id="test@test", 
                                   default_config_file=CONFIG_FILE_PATH)

        core.ssh_add(ENCRYPTED, PASSWORD)
        core.ssh_rm(ENCRYPTED)

    def test_ssh_rm_custom_1(self):

        core = CoreWithEnvironment(_iterations=100, 
                                   default_public_key=PUBLIC_KEY, 
                                   default_private_key=PRIVATE_KEY, 
                                   default_auth_id="test@test", 
                                   default_config_file=CONFIG_FILE_PATH)

        core.ssh_add(ENCRYPTED, PASSWORD, CUSTOM_PUBLIC_KEY)
        core.ssh_rm(ENCRYPTED, "foo@bar")

    def test_ssh_rm_custom_2(self):

        core = CoreWithEnvironment(_iterations=100, 
                                   default_public_key=PUBLIC_KEY, 
                                   default_private_key=PRIVATE_KEY, 
                                   default_auth_id="test@test", 
                                   default_config_file=CONFIG_FILE_PATH)

        core.ssh_add(ENCRYPTED, PASSWORD, CUSTOM_PUBLIC_KEY, "xx@yy")
        core.ssh_rm(ENCRYPTED, "xx@yy")

    def test_open_ssh(self):

        core = CoreWithEnvironment(_iterations=100, 
                                   default_public_key=PUBLIC_KEY, 
                                   default_private_key=PRIVATE_KEY, 
                                   default_auth_id="test@test", 
                                   default_config_file=CONFIG_FILE_PATH)

        core.ssh_add(ENCRYPTED, PASSWORD)

        core.open_ssh(ENCRYPTED, config_file=CONFIG_FILE_PATH)
        
        with open(OUTPUT) as f:
            result = f.read()
        expected = "Example ! "

        self.assertEqual(result, expected)

    def test_open_ssh_custom(self):

        core = CoreWithEnvironment(_iterations=100, 
                                   default_public_key=PUBLIC_KEY, 
                                   default_private_key=PRIVATE_KEY, 
                                   default_auth_id="test@test", 
                                   default_config_file=CONFIG_FILE_PATH)

        core.ssh_add(ENCRYPTED, PASSWORD, CUSTOM_PUBLIC_KEY) # implicit auth_id from Pk

        core.open_ssh(ENCRYPTED, config_file=CUSTOM_CONFIG_FILE_PATH)
        
        with open(OUTPUT) as f:
            result = f.read()
        expected = "Example ! "

        self.assertEqual(result, expected)

    def test_decrypt_ssh(self):

        core = CoreWithEnvironment(_iterations=100, 
                                   default_public_key=PUBLIC_KEY, 
                                   default_private_key=PRIVATE_KEY, 
                                   default_auth_id="test@test", 
                                   default_config_file=CONFIG_FILE_PATH)

        core.ssh_add(ENCRYPTED, PASSWORD)

        core.decrypt_ssh(ENCRYPTED, OUTPUT, config_file=CONFIG_FILE_PATH)
        
        with open(OUTPUT) as f:
            result = f.read()
        expected = "Example ! "

        self.assertEqual(result, expected)

    def test_decrypt_ssh_custom(self):

        core = CoreWithEnvironment(_iterations=100, 
                                   default_public_key=PUBLIC_KEY, 
                                   default_private_key=PRIVATE_KEY, 
                                   default_auth_id="test@test", 
                                   default_config_file=CONFIG_FILE_PATH)

        core.ssh_add(ENCRYPTED, PASSWORD, CUSTOM_PUBLIC_KEY) # implicit auth_id from Pk

        core.decrypt_ssh(ENCRYPTED, OUTPUT, config_file=CUSTOM_CONFIG_FILE_PATH)
        
        with open(OUTPUT) as f:
            result = f.read()
        expected = "Example ! "

        self.assertEqual(result, expected)

    def test_verify_ssh(self):

        core = CoreWithEnvironment(_iterations=100, 
                                   default_public_key=PUBLIC_KEY, 
                                   default_private_key=PRIVATE_KEY, 
                                   default_auth_id="test@test", 
                                   default_config_file=CONFIG_FILE_PATH)

        core.ssh_add(ENCRYPTED, PASSWORD)

        result = core.verify_ssh(ENCRYPTED, config_file=CONFIG_FILE_PATH)
        self.assertTrue(result)

    def test_verify_ssh_custom(self):

        core = CoreWithEnvironment(_iterations=100, 
                                   default_public_key=PUBLIC_KEY, 
                                   default_private_key=PRIVATE_KEY, 
                                   default_auth_id="test@test", 
                                   default_config_file=CONFIG_FILE_PATH)

        core.ssh_add(ENCRYPTED, PASSWORD, CUSTOM_PUBLIC_KEY) # implicit auth_id from Pk

        result = core.verify_ssh(ENCRYPTED, config_file=CUSTOM_CONFIG_FILE_PATH)
        self.assertTrue(result)

    