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
    action.add_argument('-e', action='store_true', default=False, dest='encrypt', help='Encrypt a file')
    action.add_argument('-d', action='store_true', default=False, dest='decrypt', help='Decrypt a file. If -o is not provided, stdout is used')
    action.add_argument('-v', action='store_true', default=False, dest='verify', help='Check if the key is valid on the file')
    action.add_argument('-n', action='store_true', default=False, dest='new', help='Create an empty encrypted file')
    action.add_argument('--edit', action='store_true', default=False, dest='edit', help='Run the internal editor [not implemented]')

    parser.add_argument('-i', default=None, dest='infilename', help='Select the encrypt file pass', required=True)
    parser.add_argument('-o', default=None, dest='outfilename', help='Select the encrypt file pass')
    return parser.parse_args()
