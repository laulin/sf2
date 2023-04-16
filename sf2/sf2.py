from getpass import getpass,getuser
import sys
import logging
import os.path
from pathlib import Path
import re
import socket

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

        self._log = logging.getLogger(self.__class__.__name__)

    def main(self):
        commands = {
            "encrypt": self.encrypt,
            "decrypt": self.decrypt,
            "verify": self.verify,
            "open": self.open,
            "ssh": self.ssh
        }

        try:
            logging.basicConfig(level=LOG_LEVELS.get(self._args.verbosity, logging.DEBUG))
        except AttributeError:
            print("Usage --help for information")
            return

        commands[self._args.commands]()
        # try:
        #     commands[self._args.commands]()
        # except Exception as e:
        #     self._log.critical(str(e))

    def encrypt(self):
        base = self.get_format(self._args.outfilename)
        self.prevent_output_overwrite()
        container = ContainerBase(base)

        if not self._args.master_password_value:
            print("We recommand min 12 chars with a-z, A-Z, 0-9 and special symbol")
            password = getpass("Password : ")
            password_copy = getpass("Confirm password : ")
            if password != password_copy:
                raise("Password are not the same, abord")
        else:
            password = self._args.master_password_value
        
        with open(self._args.infilename, "rb") as f:
            data = f.read()

        container.create(password, self._args.force)
        container.write(data, password)

    def decrypt(self):
        support = self.get_format(self._args.infilename)
        self.prevent_output_overwrite()
        if self._args.master_password:
            password = self.get_master_password()
            container = ContainerBase(support)

            data = container.read(password)
        else:
            base = ContainerBase(support)
            container = ContainerSSH(base)
            rsa_key_path = self.get_private_key()
            auth_id = self.get_auth_id()
            data = container.read(auth_id, rsa_key_path, self._args.ssh_key_password)

        with open(self._args.outfilename, "wb") as f:
            f.write(data)

    def verify(self):
        output = 0
        password = self.get_master_password()
        for filename in self._args.infilenames:
            support = self.get_format(filename)
            try:
                if self._args.master_password:
                    container = ContainerBase(support)
                    container.read(password)
                else:
                    base = ContainerBase(support)
                    container = ContainerSSH(base)
                    rsa_key_path = self.get_private_key()
                    auth_id = self.get_auth_id()
                    container.read(auth_id, rsa_key_path, self._args.ssh_key_password)
                print(f"{filename} : OK")
            except Exception as e:
                print(f"{filename} : KO ({e})")
                output = -1

        sys.exit(output)

    def open(self):
        pass

    def ssh(self):
        commands = {
            "add": self.ssh_add,
            "rm": self.ssh_rm,
            "ls": self.ssh_ls
        }

        commands[self._args.ssh_commands]()

    def ssh_add(self):
        password = self.get_master_password()
        public_key_file = self.get_public_key()
        auth_id = self.get_auth_id(public_key_file)
        for filename in self._args.infilenames:
            support = self.get_format(filename)
            base = ContainerBase(support)
            container = ContainerSSH(base)
            container.add_ssh_key(password, public_key_file, auth_id)

    def ssh_rm(self):
        auth_id = self.get_auth_id()
        for filename in self._args.infilenames:
            support = self.get_format(filename)
            container = ContainerSSH(support)
            container.remove_ssh_key(auth_id)

    def ssh_ls(self):
        for filename in self._args.infilenames:
            support = self.get_format(filename)
            container = ContainerSSH(support)
            print(f"{filename} :")
            for user, pk in container.list_ssh_key().items():
                print(user, pk)

    def get_format(self, filename:str):
        if self._args.format == "json":
            return JsonSupport(filename)
        elif self._args.format == "msgpack":
            return MsgpackSupport(filename)
        else:
            raise Exception(f"Format {self._args.format} is not supported")
        
    def get_home(self)->str:
        return str(Path.home())
    
    def get_default_rsa_private_key(self)->str:
        return os.path.join(self.get_home(), ".ssh", "id_rsa")
        
    def get_private_key(self):
        if self._args.ssh_key_file is None:
            rsa_path = self.get_default_rsa_private_key()
            if os.path.exists(rsa_path):
                return rsa_path
            else:
                raise Exception(f"ssh key is not defined and {rsa_path} doesn't exist")
        else:
            return self._args.ssh_key_file
        
    def prevent_output_overwrite(self):
        if self._args.force == False:
            if os.path.exists(self._args.outfilename):
                raise Exception(f"Output file {self._args.outfilename} is already existing")
            
    def get_master_password(self)->str:
        try: 
            if self._args.master_password:
                if not self._args.master_password_value:
                    return getpass()
                else:
                    return self._args.master_password_value
        except AttributeError:
            if not self._args.master_password_value:
                return getpass()
            else:
                return self._args.master_password_value
        
    def get_public_key(self):
        if self._args.public_key_file:
            return self._args.public_key_file
        
        if os.path.exists(f"/home/{getuser()}/.ssh/id_rsa.pub"):
            return f"/home/{getuser()}/.ssh/id_rsa.pub"
        
        raise Exception(f"Public key file is not provided and default one is not available (/home/{getuser()}/.ssh/id_rsa.pub)")
    
    def get_auth_id(self, public_key_file=None):
        if self._args.auth_id:
            return self._args.auth_id
        
        if public_key_file:
            with open(public_key_file) as f:
                key = f.read()
                key = key.strip()

            re_result = re.search(r"ssh-rsa AAAA[0-9A-Za-z+/]+[=]{0,3} ([^@]+@[^@\r\n]+)", key)
            return re_result.group(1)
        
        return f"{getuser()}@{socket.gethostname()}"

# def main():
#     args = get_args()


#     if args.encrypt:
#         print("We recommand min 12 chars with a-z, A-Z, 0-9 and special symbol")
#         password1 = getpass("Password : ")
#         password2 = getpass("Confirm password : ")
#         if password1 != password2:
#             print("Password are not the same, abord")
#             sys.exit(-1)
#         password = password1
#         cipher = Cipher()
#         try:
#             cipher.encrypt_file(password, args.infilename, args.outfilename)
#         except Exception as e:
#             print(f"Failed to encrypt file {args.infilename} : {e}")
#             sys.exit(-1)

#     elif args.decrypt:
#         password = getpass()
#         cipher = Cipher()
#         try:
#             cipher.decrypt_file(password, args.infilename, args.outfilename)
#         except Exception as e:
#             print(f"Failed to decrypt file {args.infilename} : {e}")
#             sys.exit(-1)

#     elif args.verify:
#         password = getpass()
#         cipher = Cipher()
        
#         try:
#             is_ok = cipher.verify_file(password, args.infilename)
#         except Exception as e:
#             print(f"Failed to verify file {args.infilename} : {e}")
#             sys.exit(-1)

#         if is_ok :
#             print("OK")
#         else:
#             print("FAILED !")
#             sys.exit(-1)

#     if args.new:
#         print("We recommand min 12 chars with a-z, A-Z, 0-9 and special symbol")
#         password1 = getpass("Password : ")
#         password2 = getpass("Confirm password : ")
#         if password1 != password2:
#             print("Password are not the same, abord")
#             sys.exit(-1)
#         password = password1
#         cipher = Cipher()
#         try:
#             encrypted = cipher.encrypt(password, b"") 

#             with open(args.infilename, "w") as f:
#                 f.write(encrypted)

#         except Exception as e:
#             print(f"Failed to encrypt file {args.infilename} : {e}")
#             sys.exit(-1)

#     elif args.edit:
#         password = getpass()
#         cipher = Cipher()

#         try:
#             is_ok = cipher.verify_file(password, args.infilename)
#         except Exception as e:
#             print(f"Failed to open file {args.infilename} : {e}")
#             sys.exit(-1)

#         if not is_ok :
#             print(f"Failed to open file {args.infilename} : bad key ?")
#             sys.exit(-1)

#         editor = Extern(password, args.infilename, args.editor)
#         editor.run()

#     elif args.gui:
#         gui = SF2GUI()
#         gui.create()
   

#     sys.exit(0)        

# if __name__ == "__main__":
#     main()

if __name__ == "__main__":
    sf2 = SF2()
    sf2.main()