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

def create_exclusive_secret(subparser):
    secret_choice = subparser.add_mutually_exclusive_group(required=True)
    secret_choice.add_argument('--master-password', action='store_true', dest='master_password', help='Use a master password parameters. Will call a prompt.')
    secret_choice.add_argument('--ssh-key', action='store', nargs='?', const='', dest="ssh_key", help='Provide path a secret ssh key. If no path is provided, use default SSH key')

def add_log(subparser):
    subparser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0,
        help="Verbosity (between 1-4 occurrences with more leading to more "
        "verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, "
        "DEBUG=4")
    
def add_format(subparser):
    subparser.add_argument("--format", required=False, default="msgpack", dest='format', choices=["json", "msgpack"], help='Select the file format')

def add_format_and_tail_file(subparser):
    add_format(subparser)
    subparser.add_argument('infilename', nargs=argparse.REMAINDER)

def add_private_key_options(subparser):
    subparser.add_argument('-a', "--auth_id", required=False, default=None, dest='auth_id', help='Select the authentication id, need for SSH')
    subparser.add_argument('-K', action='store', nargs='?', const=None, required=False, dest="ssh_key_password", help='Provide the password to unlock the private key')

def add_io(subparser):
    subparser.add_argument('-i', "--in", required=True, default=None, dest='infilename', help='Select the plain file path')
    subparser.add_argument('-o', "--out", required=True, default=None, dest='outfilename', help='Select the encrypt file path')
    subparser.add_argument("-f", "--force", action='store_true', dest='force', help="Force the output overwrite")

def add_program(subparser):
    subparser.add_argument('-p', "--program", required=False, default="nano", dest='program', help='Program used to open the plain text file')

def get_args(cli_args=None):
    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=RawTextHelpFormatter)

    subparsers = parser.add_subparsers(help='commands', dest='commands')

    # encrypt
    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt a file')
    add_log(encrypt_parser)
    add_io(encrypt_parser)
    add_format(encrypt_parser)

    # decrypt
    decrypt_parser = subparsers.add_parser('decrypt',  help='Decrypt a file')
    create_exclusive_secret(decrypt_parser)
    add_log(decrypt_parser)
    add_private_key_options(decrypt_parser)
    add_io(decrypt_parser)
    add_format(decrypt_parser)

    # convert
    convert_parser = subparsers.add_parser('convert', help='Convert v1 to v2 file')
    add_log(convert_parser)
    add_io(convert_parser)
    add_format(convert_parser)

    # open
    open_parser = subparsers.add_parser('open', help='Open an encrypted file with external software')
    create_exclusive_secret(open_parser)
    add_log(open_parser)
    add_private_key_options(open_parser)
    add_program(open_parser)
    add_format_and_tail_file(open_parser)

    # verify
    verify_parser = subparsers.add_parser('verify',  help='verify a file')
    create_exclusive_secret(verify_parser)
    add_log(verify_parser)
    add_private_key_options(verify_parser)
    add_format_and_tail_file(verify_parser)

    # ssh
    ssh_parser = subparsers.add_parser('ssh',  help='Administrate ssh parameters of a file')
    ssh_subparser = ssh_parser.add_subparsers(help='Commands to work on ssh key', dest="ssh_commands")
    # ssh add
    add_ssh_parser = ssh_subparser.add_parser('add',  help='Add an ssh key to a container, need the master password')
    add_log(add_ssh_parser)
    add_ssh_parser.add_argument("-k", '--public', required=False, default=None, dest='public_key', help='Select the public key. Default is ~/{curent_user}/.ssh/id_rsa.pub')
    add_ssh_parser.add_argument("-a", '--auth-id', required=False, default=None, dest='auth_id', help='Define the authentification id, default is the one in the public key')
    add_format_and_tail_file(add_ssh_parser)
    # ssh remove
    rm_ssh_parser = ssh_subparser.add_parser('rm',  help='Remove an ssh key from a container')
    add_log(rm_ssh_parser)
    rm_ssh_parser.add_argument("-a", '--auth-id', required=False, default=None, dest='auth_id', help='Define the authentification id, default is the one in the public key')
    add_format_and_tail_file(rm_ssh_parser)
    # ssh ls
    ls_ssh_parser = ssh_subparser.add_parser('ls',  help='List all ssh public file')
    add_log(ls_ssh_parser)
    add_format_and_tail_file(ls_ssh_parser)

    args =  parser.parse_args(cli_args)

    return args
