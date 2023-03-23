import argparse
from argparse import RawTextHelpFormatter
import pprint

DESCRIPTION = """

   _____ _________ 
  / ___// ____/__ \\
  \__ \/ /_   __/ /
 ___/ / __/  / __/ 
/____/_/    /____/ V2
                   
Simple Fernet File

This tool manages an encrypted file with the Fernet algorithm.

By Laulin
Supported by Spartan Conseil
"""

# def get_args():
#     parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=RawTextHelpFormatter)
#     action = parser.add_mutually_exclusive_group(required=True)
#     action.add_argument('-e', "--encrypt", action='store_true', default=False, dest='encrypt', help='Encrypt a file')
#     action.add_argument('-d', "--decrypt", action='store_true', default=False, dest='decrypt', help='Decrypt a file. If -o is not provided, stdout is used')
#     action.add_argument('--verify', action='store_true', default=False, dest='verify', help='Check if the key is valid on the file')
#     action.add_argument('-n', "--new", action='store_true', default=False, dest='new', help='Create an empty encrypted file')
#     action.add_argument('--edit', action='store_true', default=False, dest='edit', help='Run the external editor')
#     action.add_argument('--gui', action='store_true', default=False, dest='gui', help='Run the graphical version')

#     parser.add_argument('-i', "--in", default=None, dest='infilename', help='Select the encrypt file pass')
#     parser.add_argument('-o', "--out", default=None, dest='outfilename', help='Select the encrypt file pass')
#     parser.add_argument('--editor', default="mousepad", dest='editor', help='Select the external editor')
#     parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0,
#                         help="Verbosity (between 1-4 occurrences with more leading to more "
#                             "verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, "
#                             "DEBUG=4")
#     args =  parser.parse_args()

#     if not args.gui and args.infilename is None:
#         parser.error("-i is expected")

#     return args


def get_args(cli_args=None):
    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=RawTextHelpFormatter)

    subparsers = parser.add_subparsers(help='commands')

    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt a file')
    secret_source = encrypt_parser.add_mutually_exclusive_group(required=True)
    secret_source.add_argument('--master-password', action='store_true', dest='encrypt_master_password', help='Use a master password parameters. Will call a prompt.')
    secret_source.add_argument('--ssh-key', action='store', nargs='?', const='', dest="encrypt_ssh_key", help='Provide path to a public ssh key. If no path is provided, use default SSH key')
    encrypt_parser.add_argument('-i', "--in", required=True, default=None, dest='encrypt_infilename', help='Select the encrypt file path')
    encrypt_parser.add_argument('-o', "--out", required=True, default=None, dest='encrypt_outfilename', help='Select the encrypt file path')

    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt a file')
    secret_source = decrypt_parser.add_mutually_exclusive_group(required=True)
    secret_source.add_argument('--master-password', action='store_true', dest='decrypt_master_password', help='Use a master password parameters. Will call a prompt.')
    secret_source.add_argument('--ssh-key', action='store', nargs='?', const='', dest="decrypt_ssh_key", help='Provide path a secret ssh key. If no path is provided, use default SSH key')
    decrypt_parser.add_argument('-i', "--in", required=True, default=None, dest='decrypt_infilename', help='Select the decrypt file path')
    decrypt_parser.add_argument('-o', "--out", required=True, default=None, dest='decrypt_outfilename', help='Select the decrypt file path')
    

    args =  parser.parse_args(cli_args)

    return args
