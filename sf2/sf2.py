from ast import arg
from getpass import getpass
import sys
import logging

from sf2.args import get_args
from sf2.cipher import Cipher
from sf2.extern import Extern

try:
    from sf2.sf2gui import SF2GUI
except:
    def SF2GUI(*args, **kwargs):
        print("No graphical interface available !")
        sys.exit(-1)

def main():
    args = get_args()

    log_levels = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARN,
        3: logging.INFO,
        4: logging.DEBUG,
    }
    
    logging.basicConfig(level=log_levels.get(args.verbosity, logging.DEBUG))

    if args.encrypt:
        print("We recommand min 12 chars with a-z, A-Z, 0-9 and special symbol")
        password1 = getpass("Password : ")
        password2 = getpass("Confirm password : ")
        if password1 != password2:
            print("Password are not the same, abord")
            sys.exit(-1)
        password = password1
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

    if args.new:
        print("We recommand min 12 chars with a-z, A-Z, 0-9 and special symbol")
        password1 = getpass("Password : ")
        password2 = getpass("Confirm password : ")
        if password1 != password2:
            print("Password are not the same, abord")
            sys.exit(-1)
        password = password1
        cipher = Cipher()
        try:
            encrypted = cipher.encrypt(password, b"") 

            with open(args.infilename, "w") as f:
                f.write(encrypted)

        except Exception as e:
            print(f"Failed to encrypt file {args.infilename} : {e}")
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

        editor = Extern(password, args.infilename, args.editor)
        editor.run()

    elif args.gui:
        gui = SF2GUI()
        gui.create()
   

    sys.exit(0)        

if __name__ == "__main__":
    main()