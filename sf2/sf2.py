from getpass import getpass
import sys

from sf2.args import get_args
from sf2.cipher import Cipher
from sf2.editor import Editor


def main():
    args = get_args()

    if args.encrypt:
        print("We recommand min 12 chars with a-z, A-Z, 0-9 and special symbol")
        password = getpass()
        cipher = Cipher()
        try:
            cipher.encrypt_file(password, args.infilename, args.outfilename)
        except Exception as e:
            print(f"Failed to encrypt file {args.infilename} : {e}")
            sys.exit(-1)

    elif args.decrypt:
        password = getpass()
        cipher = Cipher()
        try:
            cipher.decrypt_file(password, args.infilename, args.outfilename)
        except Exception as e:
            print(f"Failed to decrypt file {args.infilename} : {e}")
            sys.exit(-1)

    elif args.verify:
        password = getpass()
        cipher = Cipher()
        
        try:
            is_ok = cipher.verify_file(password, args.infilename)
        except Exception as e:
            print(f"Failed to verify file {args.infilename} : {e}")
            sys.exit(-1)

        if is_ok :
            print("OK")
        else:
            print("FAILED !")
            sys.exit(-1)
    elif args.edit:
        password = getpass()
        cipher = Cipher()

        try:
            is_ok = cipher.verify_file(password, args.infilename)
        except Exception as e:
            print(f"Failed to open file {args.infilename} : {e}")
            sys.exit(-1)

        if not is_ok :
            print(f"Failed to open file {args.infilename} : bad key ?")
            sys.exit(-1)

        editor = Editor(password, args.infilename)
        editor.load()
        editor.create()

    sys.exit(0)        

if __name__ == "__main__":
    main()