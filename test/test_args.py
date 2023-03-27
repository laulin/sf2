import unittest
from pprint import pprint

from sf2.args import get_args



class TestGetArgs(unittest.TestCase):

    # def test_help(self):
    #     # args = get_args(["encrypt", "--help"])
    #     args = get_args(["ssh", "--help"])

    # encrypt

    def test_encrypt_mk(self):
        args = get_args(["encrypt", "-i", "in.txt", "-o", "out.x"])
        results = [args.infilename, args.outfilename]
        expected = ["in.txt", "out.x"]

        self.assertEqual(results, expected)

    def test_encrypt_format(self):
        args = get_args(["encrypt", "--format", "json", "-i", "in.txt", "-o", "out.x"])
        results = [args.infilename, args.outfilename, args.format]
        expected = ["in.txt", "out.x", "json"]

        self.assertEqual(results, expected)

    # decrypt

    def test_decrypt_mk(self):
        args = get_args(["decrypt", "--master-password", "-i", "in.txt", "-o", "out.x"])
        results = [args.infilename, args.outfilename, args.decryptpassword]
        expected = ["in.txt", "out.x", True]

        self.assertEqual(results, expected)

    def test_decrypt_ssh_key_no_file(self):
        args = get_args(["decrypt", "--ssh-key", "-i", "in.txt", "-o", "out.x"])
        results = [args.infilename, args.outfilename, args.ssh_key]
        expected = ["in.txt", "out.x", ""]

        self.assertEqual(results, expected)

    def test_decrypt_ssh_key_with_file(self):
        args = get_args(["decrypt", "--ssh-key", "/home/foo/.ssh/id_rsa", "-i", "in.txt", "-o", "out.x"])
        results = [args.infilename, args.outfilename, args.ssh_key]
        expected = ["in.txt", "out.x", "/home/foo/.ssh/id_rsa"]

        self.assertEqual(results, expected)

    # convert
    def test_decrypt_mk(self):
        args = get_args(["convert", "-i", "in.y", "-o", "out.x"])
        results = [args.infilename, args.outfilename]
        expected = ["in.y", "out.x"]
        self.assertEqual(results, expected)

    # open
    def test_open_mk(self):
        args = get_args(["open", "--master-password", "--program", "nano",  "out.x"]) 
        results = [args.commands, args.infilename, args.master_password, args.program]
        expected = ['open', ['out.x'], True, 'nano']

        self.assertEqual(results, expected)

    def test_open_ssh_key_no_file(self):
        args = get_args(["open", "--ssh-key", "--program", "nano",  "out.x"]) 
        results = [args.commands, args.infilename, args.master_password, args.program, args.ssh_key]
        expected = ['open', ['out.x'], False, 'nano', '']

        self.assertEqual(results, expected)

    def test_open_ssh_key_with_file(self):
        args = get_args(["open", "--ssh-key", ".ssh/id_rsa", "--program", "nano",  "out.x"]) 
        results = [args.commands, args.infilename, args.master_password, args.program, args.ssh_key]
        expected = ['open', ['out.x'], False, 'nano', ".ssh/id_rsa"]

        self.assertEqual(results, expected)

    def test_open(self):
        args = get_args(["open", "out.x"]) 
        results = [args.commands, args.infilename, args.master_password, args.program, args.ssh_key]
        expected = ['open', ['out.x'], False, None, None]

        self.assertEqual(results, expected)

    # verify
    def test_verify_mk(self):
        args = get_args(["verify", "--master-password",  "out.x"]) 
        results = [args.commands, args.infilename, args.master_password]
        expected = ['verify', ['out.x'], True]

        self.assertEqual(results, expected)

    def test_verify_ssh_key_no_file(self):
        args = get_args(["verify", "--ssh-key", "", "out.x"]) 
        results = [args.commands, args.infilename, args.master_password, args.ssh_key]
        expected = ['verify', ['out.x'], False, '']

        self.assertEqual(results, expected)

    def test_verify_ssh_key_with_file(self):
        args = get_args(["verify", "--ssh-key", ".ssh/id_rsa", "out.x"]) 
        results = [args.commands, args.infilename, args.master_password, args.ssh_key]
        expected = ['verify', ['out.x'], False, ".ssh/id_rsa"]

        self.assertEqual(results, expected)

    # ssh add
    def test_ssh_add_all(self):
        args = get_args(["ssh", "add", "-k", ".ssh/id_rsa.pub", "-a", "foo@bar", "out.x"]) 
        results = [args.commands, args.ssh_commands, args.public_key, args.auth_id, args.infilename]
        expected = ['ssh', "add", ".ssh/id_rsa.pub", "foo@bar", ["out.x"]]

        self.assertEqual(results, expected)

    def test_ssh_add_default(self):
        args = get_args(["ssh", "add", "-k", "", "out.x"]) 
        results = [args.commands, args.ssh_commands, args.public_key, args.auth_id, args.infilename]
        expected = ['ssh', "add", "", None, ["out.x"]]

        self.assertEqual(results, expected)

    # ssh rm
    def test_ssh_add_all(self):
        args = get_args(["ssh", "rm", "-a", "foo@bar", "out.x"]) 
        results = [args.commands, args.ssh_commands, args.auth_id, args.infilename]
        expected = ['ssh', "rm", ".ssh/id_rsa.pub", "foo@bar", ["out.x"]]

        self.assertEqual(results, expected)

    # ssh ls
    def test_ssh_add_all(self):
        args = get_args(["ssh", "ls", "out.x"]) 
        results = [args.commands, args.ssh_commands, args.infilename]
        expected = ['ssh', "ls",  ["out.x"]]

        self.assertEqual(results, expected)