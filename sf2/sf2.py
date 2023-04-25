from getpass import getpass
import sys
import logging
import os.path

from sf2.args import get_args
from sf2.core_with_environment import CoreWithEnvironment

from sf2.gui.gui import run_app



LOG_LEVELS = {
    0: logging.CRITICAL,
    1: logging.ERROR,
    2: logging.WARN,
    3: logging.INFO,
    4: logging.DEBUG,
}

class SF2:
    def __init__(self, args=None, _iterations:int=None) -> None:
        self._args = get_args(args)
        self._core = CoreWithEnvironment(_iterations)
        self._log = logging.getLogger(self.__class__.__name__)

    def main(self):
        commands = {
            "encrypt": self.encrypt,
            "decrypt": self.decrypt,
            "verify": self.verify,
            "open": self.open,
            "ssh": self.ssh,
            "new": self.new,
            "app": self.app
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
        password = self.get_or_create_master_password()
        self._core.encrypt(self._args.infilename, self._args.outfilename, password, self._args.format)

    def decrypt(self):
        if self._args.master_password:
            password = self.get_master_password()
            self._core.decrypt(self._args.infilename, self._args.outfilename, password, self._args.format)
        else:
            self._core.decrypt_ssh(self._args.infilename, self._args.outfilename, self._args.private_key_file, 
                                   self._args.private_key_password, self._args.auth_id, self._args.format,
                                   self._args.force, self._args.config_file)

    def verify(self):
        output = 0
        password = self.get_master_password()
        for filename in self._args.infilenames:

            if self._args.master_password:
                status = self._core.verify(filename, password, self._args.format)
                   
            else:
                status = self._core.verify_ssh(filename, self._args.private_key_file, self._args.private_key_password, 
                                               self._args.auth_id, self._args.format, self._args.config_file)
            
            if status :
                print(f"{filename} : OK")
            else:
                print(f"{filename} : KO")
                output = -1


        sys.exit(output)

    def open(self):
        if len(self._args.infilenames) > 1:
            raise Exception(f"Only one file can be open, not {len(self._args.infilenames)}")
        filename = os.path.abspath(self._args.infilenames[0])
           

        if self._args.master_password:
            password = self.get_master_password()
            self._core.open(filename, self._args.program, password, self._args.format)
        else:
            self._core.open_ssh(filename, self._args.program, self._args.private_key_file, self._args.private_key_password, 
                                self._args.auth_id, self._args.format, self._args.config_file)


    def ssh(self):
        commands = {
            "add": self.ssh_add,
            "rm": self.ssh_rm,
            "ls": self.ssh_ls
        }

        commands[self._args.ssh_commands]()

    def ssh_add(self):
        password = self.get_master_password()
        for filename in self._args.infilenames:
            self._core.ssh_add(filename, password, self._args.public_key_file, self._args.auth_id, self._args.format)

    def ssh_rm(self):
        for filename in self._args.infilenames:
            self._core.ssh_rm(filename, self._args.auth_id, self._args.format, self._args.config_file)

    def ssh_ls(self):
        for filename in self._args.infilenames:
            print(f"{filename} :")
            for user, pk in self._core.ssh_ls(filename, self._args.format):
                print(user, pk)

    def new(self):
        password = self.get_or_create_master_password()

        for filename in self._args.infilenames:
            self._core.new(filename, password, self._args.force, self._args.format)

    def app(self):
        run_app()
            
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
            
    def get_or_create_master_password(self):
        if not self._args.master_password_value:
            print("We recommand min 12 chars with a-z, A-Z, 0-9 and special symbol")
            password = getpass("Password : ")
            password_copy = getpass("Confirm password : ")
            if password != password_copy:
                raise("Password are not the same, abord")
        else:
            password = self._args.master_password_value

        return password
        
if __name__ == "__main__":
    sf2 = SF2()
    sf2.main()