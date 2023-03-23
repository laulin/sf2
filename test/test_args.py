import unittest
from pprint import pprint

from sf2.args import get_args



class TestGetArgs(unittest.TestCase):

    # def test_help(self):
    #     args = get_args(["encrypt", "--help"])

    # encrypt

    def test_encrypt_mk(self):
        args = get_args(["encrypt", "--master-password", "-i", "in.txt", "-o", "out.x"])
        results = [args.encrypt_infilename, args.encrypt_outfilename, args.encrypt_master_password]
        expected = ["in.txt", "out.x", True]

        self.assertEqual(results, expected)

    def test_encrypt_ssh_key_no_file(self):
        args = get_args(["encrypt", "--ssh-key", "-i", "in.txt", "-o", "out.x"])
        results = [args.encrypt_infilename, args.encrypt_outfilename, args.encrypt_ssh_key]
        expected = ["in.txt", "out.x", ""]

        self.assertEqual(results, expected)

    def test_encrypt_ssh_key_with_file(self):
        args = get_args(["encrypt", "--ssh-key", "/home/foo/.ssh/id_rsa.pub", "-i", "in.txt", "-o", "out.x"])
        results = [args.encrypt_infilename, args.encrypt_outfilename, args.encrypt_ssh_key]
        expected = ["in.txt", "out.x", "/home/foo/.ssh/id_rsa.pub"]

        self.assertEqual(results, expected)

    # decrypt

    def test_decrypt_mk(self):
        args = get_args(["decrypt", "--master-password", "-i", "in.txt", "-o", "out.x"])
        results = [args.decrypt_infilename, args.decrypt_outfilename, args.decrypt_master_password]
        expected = ["in.txt", "out.x", True]

        self.assertEqual(results, expected)

    def test_decrypt_ssh_key_no_file(self):
        args = get_args(["decrypt", "--ssh-key", "-i", "in.txt", "-o", "out.x"])
        results = [args.decrypt_infilename, args.decrypt_outfilename, args.decrypt_ssh_key]
        expected = ["in.txt", "out.x", ""]

        self.assertEqual(results, expected)

    def test_decrypt_ssh_key_with_file(self):
        args = get_args(["decrypt", "--ssh-key", "/home/foo/.ssh/id_rsa", "-i", "in.txt", "-o", "out.x"])
        results = [args.decrypt_infilename, args.decrypt_outfilename, args.decrypt_ssh_key]
        expected = ["in.txt", "out.x", "/home/foo/.ssh/id_rsa"]

        self.assertEqual(results, expected)

    
        


   