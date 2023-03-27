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

    subparsers = parser.add_subparsers(help='commands', dest='commands')

    # encrypt
    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt a file')
    encrypt_parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0,
                        help="Verbosity (between 1-4 occurrences with more leading to more "
                            "verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, "
                            "DEBUG=4")
    encrypt_parser.add_argument('-i', "--in", required=True, default=None, dest='infilename', help='Select the encrypt file path')
    encrypt_parser.add_argument('-o', "--out", required=True, default=None, dest='outfilename', help='Select the encrypt file path')
    encrypt_parser.add_argument("--format", required=False, default="msgpack", dest='format', choices=["json", "msgpack"], help='Select the file format')
    encrypt_parser.add_argument("-f", "--force", action='store_true', dest='force', help="Force the output overwrite")

    # decrypt
    decrypt_parser = subparsers.add_parser('decrypt',  help='Decrypt a file')
    secret_source = decrypt_parser.add_mutually_exclusive_group(required=True)
    secret_source.add_argument('--master-password', action='store_true', dest='master_password', help='Use a master password parameters. Will call a prompt.')
    secret_source.add_argument('--ssh-key', action='store', nargs='?', const='', dest="ssh_key", help='Provide path a secret ssh key. If no path is provided, use default SSH key')
    decrypt_parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0,
                        help="Verbosity (between 1-4 occurrences with more leading to more "
                            "verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, "
                            "DEBUG=4")
    decrypt_parser.add_argument('-i', "--in", required=True, default=None, dest='infilename', help='Select the decrypt file path')
    decrypt_parser.add_argument('-o', "--out", required=True, default=None, dest='outfilename', help='Select the decrypt file path')
    decrypt_parser.add_argument("--format", required=False, default="msgpack", dest='format', choices=["json", "msgpack"], help='Select the file format')

    # convert
    convert_parser = subparsers.add_parser('convert', help='Convert v1 to v2 file')
    convert_parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0,
                        help="Verbosity (between 1-4 occurrences with more leading to more "
                            "verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, "
                            "DEBUG=4")
    convert_parser.add_argument('-i', "--in", required=True, default=None, dest='infilename', help='Select the decrypt file path')
    convert_parser.add_argument('-o', "--out", required=True, default=None, dest='outfilename', help='Select the decrypt file path')
    convert_parser.add_argument("--format", required=False, default="msgpack", dest='format', choices=["json", "msgpack"], help='Select the file format')

    # open
    open_parser = subparsers.add_parser('open', help='Open an encrypted file with external software')
    secret_source = open_parser.add_mutually_exclusive_group(required=False)
    secret_source.add_argument('--master-password', action='store_true', dest='master_password', help='Use a master password parameters. Will call a prompt.')
    secret_source.add_argument('--ssh-key', action='store', nargs='?', const='', dest="ssh_key", help='Provide path a secret ssh key. If no path is provided, use default SSH key')
    open_parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0,
                        help="Verbosity (between 1-4 occurrences with more leading to more "
                            "verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, "
                            "DEBUG=4")
    open_parser.add_argument('-p', "--program", required=False, default=None, dest='program', help='Program used to open the plain text file')
    open_parser.add_argument("--format", required=False, default="msgpack", dest='format', choices=["json", "msgpack"], help='Select the file format')
    open_parser.add_argument('infilename', nargs=argparse.REMAINDER)

    # verify
    verify_parser = subparsers.add_parser('verify',  help='verify a file')
    secret_source = verify_parser.add_mutually_exclusive_group(required=True)
    secret_source.add_argument('--master-password', action='store_true', dest='master_password', help='Use a master password parameters. Will call a prompt.')
    secret_source.add_argument('--ssh-key', action='store', nargs='?', const='', dest="ssh_key", help='Provide path a secret ssh key. If no path is provided, use default SSH key')
    secret_source.add_argument("--format", required=False, default="msgpack", dest='format', choices=["json", "msgpack"], help='Select the file format')
    verify_parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0,
                        help="Verbosity (between 1-4 occurrences with more leading to more "
                            "verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, "
                            "DEBUG=4")
    verify_parser.add_argument('infilename', nargs=argparse.REMAINDER)

    # ssh
    ssh_parser = subparsers.add_parser('ssh',  help='Administrate ssh parameters of a file')
    ssh_subparser = ssh_parser.add_subparsers(help='Commands to work on ssh key', dest="ssh_commands")
    # ssh add
    add_ssh_parser = ssh_subparser.add_parser('add',  help='Add an ssh key to a container, need the master password')
    add_ssh_parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0,
                        help="Verbosity (between 1-4 occurrences with more leading to more "
                            "verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, "
                            "DEBUG=4")
    add_ssh_parser.add_argument("-k", '--public', required=False, default=None, dest='public_key', help='Select the public key. Default is ~/{curent_user}/.ssh/id_rsa.pub')
    add_ssh_parser.add_argument("-a", '--auth-id', required=False, default=None, dest='auth_id', help='Define the authentification id, default is the one in the public key')
    add_ssh_parser.add_argument("--format", required=False, default="msgpack", dest='format', choices=["json", "msgpack"], help='Select the file format')
    add_ssh_parser.add_argument('infilename', nargs=argparse.REMAINDER, help="List of containers")
    # ssh remove
    rm_ssh_parser = ssh_subparser.add_parser('rm',  help='Remove an ssh key from a container')
    rm_ssh_parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0,
                        help="Verbosity (between 1-4 occurrences with more leading to more "
                            "verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, "
                            "DEBUG=4")
    rm_ssh_parser.add_argument("-a", '--auth-id', required=False, default=None, dest='auth_id', help='Define the authentification id, default is the one in the public key')
    rm_ssh_parser.add_argument("--format", required=False, default="msgpack", dest='format', choices=["json", "msgpack"], help='Select the file format')
    rm_ssh_parser.add_argument('infilename', nargs=argparse.REMAINDER, help="List of containers")
    # ssh ls
    ls_ssh_parser = ssh_subparser.add_parser('ls',  help='List all ssh public file')
    ls_ssh_parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0,
                        help="Verbosity (between 1-4 occurrences with more leading to more "
                            "verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, "
                            "DEBUG=4")
    ls_ssh_parser.add_argument("--format", required=False, default="msgpack", dest='format', choices=["json", "msgpack"], help='Select the file format')
    ls_ssh_parser.add_argument('infilename', nargs=argparse.REMAINDER, help="List of containers")

    args =  parser.parse_args(cli_args)

    return args
