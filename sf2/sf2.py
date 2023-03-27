from getpass import getpass
import sys
import logging

from sf2.args import get_args
from sf2.cipher import Cipher
from sf2.extern import Extern

from sf2.container_ssh import ContainerSSH
from sf2.container_base import ContainerBase
from sf2.json_support import JsonSupport
from sf2.msgpack_support import MsgpackSupport

try:
    from sf2.gui.sf2gui import SF2GUI
except:
    def SF2GUI(*args, **kwargs):
        print("No graphical interface available !")
        sys.exit(-1)


LOG_LEVELS = {
    0: logging.CRITICAL,
    1: logging.ERROR,
    2: logging.WARN,
    3: logging.INFO,
    4: logging.DEBUG,
}

class SF2:
    def __init__(self, args=None) -> None:
        self._args = get_args(args)

        self._log = logging.getLogger(self.__class__.__class__)

    def main(self):
        commands = {
            "encrypt": self.encrypt,
            "decrypt": self.decrypt,
            "verify": self.verify,
            "open": self.open,
            "ssh": self.ssh
        }

        logging.basicConfig(level=LOG_LEVELS.get(self._args.verbosity, logging.DEBUG))

        commands[self._args.commands]()

    def encrypt(self):
        base = self.get_format(self._args.outfilename)
        container = ContainerBase(base)

        print("We recommand min 12 chars with a-z, A-Z, 0-9 and special symbol")
        password1 = getpass("Password : ")
        password2 = getpass("Confirm password : ")
        if password1 != password2:
            raise("Password are not the same, abord")
        
        with open(self._args.infilename, "rb") as f:
            data = f.read()

        container.create(password1, self._args.force)
        container.write(data, password1)

    def decrypt(self):
        password = getpass()
        base = self.get_format(self._args.infilename)
        container = ContainerBase(base)

        data = container.read(password)

        with open(self._args.outfilename, "wb") as f:
            f.write(data)

    def verify(self):
        pass

    def open(self):
        pass

    def ssh(self):
        pass

    def get_format(self, filename:str):
        if self._args.format == "json":
            return JsonSupport(filename)
        elif self._args.format == "msgpack":
            return MsgpackSupport(filename)
        else:
            raise Exception(f"Format {self._args.format} is not supported")

def main():
    args = get_args()

    
    
    

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

# if __name__ == "__main__":
#     main()

if __name__ == "__main__":
    sf2 = SF2()
    sf2.main()