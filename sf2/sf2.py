from getpass import getpass,getuser
import sys
import logging
import os.path
from pathlib import Path
import re
import socket

from sf2.args import get_args
from sf2.openinram import OpenInRAM
from sf2.file_object import FileObject
from sf2.ssh_file_object import SSHFileObject
from sf2.configuration import Configuration

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
            "ssh": self.ssh,
            "new": self.new
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
        container = ContainerBase(base)

        password = self.get_or_create_master_password()
        
        with open(self._args.infilename, "rb") as f:
            data = f.read()

        container.create(password, self._args.force)
        container.write(data, password)

    def decrypt(self):
        support = self.get_format(self._args.infilename)
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
        if len(self._args.infilenames) > 1:
            raise Exception(f"Only one file can be open, not {len(self._args.infilenames)}")
        filename = os.path.abspath(self._args.infilenames[0])
        
        default_config_path = os.path.join(Path.home(), ".sf2/config")
        if self._args.config_file is None:
            config = Configuration(default_config_path)
        else:
            config = Configuration(self._args.config_file)

        file_config = config.get_file_attribute(filename)
        print(filename)        
        support = self.get_format(filename)

        if self._args.master_password:
            password = self.get_master_password()
            file_object = FileObject(support, password)
        else:
            rsa_key_path = self.get_private_key(file_config.get("private_key"))
            auth_id = file_config.get("auth_id", self.get_auth_id())
            file_object = SSHFileObject(support, auth_id, rsa_key_path, self._args.ssh_key_password)

        open_in_ram = OpenInRAM(file_object, self._args.program)
        open_in_ram.run()

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

    def new(self):
        password = self.get_or_create_master_password()

        for filename in self._args.infilenames:
            support = self.get_format(filename)
            container = ContainerBase(support)
            container.create(password, self._args.force)
            container.write(b"", password)

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
        
    def get_private_key(self, from_config:str=None):
        if from_config is not None:
            if not os.path.exists(from_config):
                raise Exception(f"ssh key {from_config} defined in configuration doesn't exist")
            return from_config
        
        elif self._args.ssh_key_file is None:
            rsa_path = self.get_default_rsa_private_key()
            if os.path.exists(rsa_path):
                return rsa_path
            else:
                raise Exception(f"ssh key is not defined and {rsa_path} doesn't exist")
        else:
            return self._args.ssh_key_file
            
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

if __name__ == "__main__":
    sf2 = SF2()
    sf2.main()