import argparse
from argparse import RawTextHelpFormatter

DESCRIPTION = """

   _____ _________ 
  / ___// ____/__ \\
  \__ \/ /_   __/ /
 ___/ / __/  / __/ 
/____/_/    /____/ 
                   
Simple Fernet File

This tool manages an encrypted file with the Fernet algorithm.

By Laulin
Supported by Spartan Conseil
"""

def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=RawTextHelpFormatter)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('-e', "--encrypt", action='store_true', default=False, dest='encrypt', help='Encrypt a file')
    action.add_argument('-d', "--decrypt", action='store_true', default=False, dest='decrypt', help='Decrypt a file. If -o is not provided, stdout is used')
    action.add_argument('--verify', action='store_true', default=False, dest='verify', help='Check if the key is valid on the file')
    action.add_argument('-n', "--new", action='store_true', default=False, dest='new', help='Create an empty encrypted file')
    action.add_argument('--edit', action='store_true', default=False, dest='edit', help='Run the internal editor')
    action.add_argument('--external', action='store_true', default=False, dest='external', help='Run an external editor')

    parser.add_argument('-i', "--in", default=None, dest='infilename', help='Select the encrypt file pass', required=True)
    parser.add_argument('-o', "--out", default=None, dest='outfilename', help='Select the encrypt file pass')
    parser.add_argument('--editor', default="mousepad", dest='editor', help='Select the external editor')
    parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0,
                        help="Verbosity (between 1-4 occurrences with more leading to more "
                            "verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, "
                            "DEBUG=4")
    return parser.parse_args()
