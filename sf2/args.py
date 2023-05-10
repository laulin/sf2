import argparse
from argparse import RawTextHelpFormatter

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


def create_exclusive_secret(subparser):
    secret_choice = subparser.add_mutually_exclusive_group(required=False)
    secret_choice.add_argument('--password', action='store_true', default=False, dest='password_method', help='Use password method. Will call a prompt if -m is not called')
    secret_choice.add_argument('--ssh', action='store_true', default=True, dest="ssh_method", help='Provide path a secret ssh key. If no path is provided, use default SSH key. This is the default behaviour')

    subparser.add_argument('-a', "--auth_id", required=False, dest='auth_id', help='Select the authentication id, need for SSH')
    subparser.add_argument('-K', action='store', required=False, dest="private_key_password", help='Provide the password to unlock the private key')
    subparser.add_argument('-y', action='store', required=False, dest="private_key_file", help='Provide the private key')

    add_password(subparser)

def add_password(subparser):
    subparser.add_argument('-m', action='store', required=False, dest="password", help='Provide the password')
    subparser.add_argument('-w', action='store_true', required=False, dest="allow_weak_password", default=False, help='Allow weak_password')

def add_log(subparser):
    subparser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0,
        help="Verbosity (between 1-4 occurrences with more leading to more "
        "verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, "
        "DEBUG=4")
    
def add_format(subparser):
    subparser.add_argument("--format", required=False, default="msgpack", dest='format', choices=["json", "msgpack"], help='Select the file format')

def add_format_and_tail_file(subparser):
    add_format(subparser)
    subparser.add_argument('infilenames', nargs=argparse.REMAINDER)

def add_io(subparser):
    subparser.add_argument('-i', "--in", required=True, default=None, dest='infilename', help='Select the plain file path')
    subparser.add_argument('-o', "--out", required=True, default=None, dest='outfilename', help='Select the encrypt file path')
    subparser.add_argument("-f", "--force", action='store_true', dest='force', help="Force the output overwrite")

def add_program(subparser):
    subparser.add_argument('-p', "--program", required=False, default="nano", dest='program', help='Program used to open the plain text file')

def add_configFile(subparser):
    subparser.add_argument('-F', action='store', required=False, dest="config_file", help='Provide the config file')

def get_args(cli_args=None):
    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=RawTextHelpFormatter)

    subparsers = parser.add_subparsers(help='commands', dest='commands')

    # encrypt
    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt a file')
    add_password(encrypt_parser)
    add_log(encrypt_parser)
    add_io(encrypt_parser)
    add_format(encrypt_parser)

    # decrypt
    decrypt_parser = subparsers.add_parser('decrypt',  help='Decrypt a file')
    create_exclusive_secret(decrypt_parser)
    add_log(decrypt_parser)
    add_io(decrypt_parser)
    add_configFile(decrypt_parser)
    add_format(decrypt_parser)

    # convert
    convert_parser = subparsers.add_parser('convert', help='Convert v1 to v2 file')
    add_log(convert_parser)
    add_io(convert_parser)
    add_password(convert_parser)
    add_format(convert_parser)

    # open
    open_parser = subparsers.add_parser('open', help='Open an encrypted file with external software')
    create_exclusive_secret(open_parser)
    add_log(open_parser)
    open_parser.add_argument('-c', "--config", required=False, default=None, dest='config_file', help='Define the configuration path. Default is /home/[dude]/.sf2/config')
    add_program(open_parser)
    add_configFile(open_parser)
    add_format_and_tail_file(open_parser)

    # verify
    verify_parser = subparsers.add_parser('verify',  help='verify a file')
    create_exclusive_secret(verify_parser)
    add_log(verify_parser)
    add_configFile(verify_parser)
    add_format_and_tail_file(verify_parser)

    # ssh
    ssh_parser = subparsers.add_parser('ssh',  help='Administrate ssh parameters of a file')
    ssh_subparser = ssh_parser.add_subparsers(help='Commands to work on ssh key', dest="ssh_commands")
    # ssh add
    add_ssh_parser = ssh_subparser.add_parser('add',  help='Add an ssh key to a container, need the master password')
    add_log(add_ssh_parser)
    add_ssh_parser.add_argument("-k", '--public', required=False, default=None, dest='public_key_file', help='Select the public key. Default is ~/{curent_user}/.ssh/id_rsa.pub')
    add_ssh_parser.add_argument("-a", '--auth-id', required=False, default=None, dest='auth_id', help='Define the authentification id, default is the one in the public key')
    add_password(add_ssh_parser)
    add_format_and_tail_file(add_ssh_parser)
    # ssh remove
    rm_ssh_parser = ssh_subparser.add_parser('rm',  help='Remove an ssh key from a container')
    add_log(rm_ssh_parser)
    rm_ssh_parser.add_argument("-a", '--auth-id', required=False, default=None, dest='auth_id', help='Define the authentification id, default is the one in the public key')
    rm_ssh_parser.add_argument('-m', action='store', required=False, dest="password", help='Provide the password')
    add_configFile(rm_ssh_parser)
    add_format_and_tail_file(rm_ssh_parser)
    # ssh ls
    ls_ssh_parser = ssh_subparser.add_parser('ls',  help='List all ssh public file')
    add_log(ls_ssh_parser)
    add_format_and_tail_file(ls_ssh_parser)

    # new
    new_parser = subparsers.add_parser('new', help='Create an empty encrypted container')
    add_password(new_parser)
    new_parser.add_argument("-f", "--force", action='store_true', dest='force', help="Force the output overwrite")
    add_log(new_parser)
    add_format_and_tail_file(new_parser)

    # app
    app_parser = subparsers.add_parser('app', help='Run gui')
    add_configFile(app_parser)
    add_log(app_parser)

    args =  parser.parse_args(cli_args)

    return args
