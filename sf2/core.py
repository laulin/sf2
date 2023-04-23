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



class Core:
    def __init__(self, configuration_file:str=None, _iterations:int=None) -> None:
        if configuration_file is None:
            configuration_file = os.path.join(self.get_home(), ".sf2", "config")

        self._configuration = Configuration(configuration_file)
        self._iterations = _iterations
        self._log = logging.getLogger(self.__class__.__name__)

    def encrypt(self, infilename:str, outfilename:str, password:str, support_format:str="msgpack", force:bool=False):
        support = self.get_support(outfilename, support_format)
        container = ContainerBase(support)
        
        with open(infilename, "rb") as f:
            data = f.read()

        container.create(password, force, self._iterations)
        container.write(data, password, self._iterations)

    def decrypt(self, infilename:str, outfilename:str, password:str, support_format:str="msgpack"):
        support = self.get_support(infilename, support_format)
        container = ContainerBase(support)
        data = container.read(password,self._iterations)

        with open(outfilename, "wb") as f:
            f.write(data)

    def decrypt_ssh(self, infilename:str, outfilename:str, private_key_file:str=None, private_key_password:str=None, auth_id:str=None, support_format:str="msgpack"):
        support = self.get_support(infilename, support_format)
        base = ContainerBase(support)
        container = ContainerSSH(base)
        auth_id = self.get_auth_id(auth_id)
        data = container.read(auth_id, private_key_file, private_key_password)

        with open(outfilename, "wb") as f:
            f.write(data)

    def verify(self, filename:str, password:str=None, support_format:str="msgpack")->bool:
        password = self.get_master_password(password)
        support = self.get_support(filename, support_format)
        try:
            container = ContainerBase(support)
            container.read(password, self._iterations)
            return True
        except Exception as e:
            return False

    def verify_ssh(self, filename:str, private_key_file:str=None, private_key_password:str=None, auth_id:str=None, support_format:str="msgpack")->bool:
        support = self.get_support(filename, support_format)
        try:
            base = ContainerBase(support)
            container = ContainerSSH(base)
            auth_id = self.get_auth_id(auth_id)
            container.read(auth_id, private_key_file, private_key_password)
            return True
        except Exception as e:
            print(e)
            return False


    def open(self, filename:str, program:str, password:str=None, support_format:str="msgpack"):
        support = self.get_support(filename, support_format)

        master_password = self.get_master_password(password)
        file_object = FileObject(support, master_password, self._iterations)

        open_in_ram = OpenInRAM(file_object, program)
        open_in_ram.run()

    def open_ssh(self, filename:str, program:str, private_key_file:str=None, private_key_password:str=None, auth_id:str=None, support_format:str="msgpack" ):

        support = self.get_support(filename, support_format)
        file_object = SSHFileObject(support, auth_id, private_key_file, private_key_password)

        open_in_ram = OpenInRAM(file_object, program)
        open_in_ram.run()

    def ssh_add(self, filename:str, password:str, public_key_file:str=None, auth_id:str=None, support_format:str="msgpack"):
        password = self.get_master_password(password)
        public_key_file = self.get_public_key(public_key_file)
        auth_id = self.get_auth_id(auth_id, public_key_file)

        support = self.get_support(filename, support_format)
        base = ContainerBase(support)
        container = ContainerSSH(base)
        container.add_ssh_key(password, public_key_file, auth_id, self._iterations)

    def ssh_rm(self, filename:str, auth_id:str=None, support_format:str="msgpack"):
        auth_id = self.get_auth_id(auth_id)
        support = self.get_support(filename, support_format)
        container = ContainerSSH(support)
        container.remove_ssh_key(auth_id)

    def ssh_ls(self, filename:str, support_format:str="msgpack"):
        output = list()
        support = self.get_support(filename, support_format)
        container = ContainerSSH(support)
        for user, pk in container.list_ssh_key().items():
            output.append((user, pk))

        return output

    def new(self, filename:str, password:str, force:bool=False):
        support = self.get_support(filename)
        container = ContainerBase(support)
        container.create(password, force)
        container.write(b"", password)

    def get_support(self, filename:str, support_format:str):
        if support_format == "json":
            return JsonSupport(filename)
        elif support_format == "msgpack":
            return MsgpackSupport(filename)
        else:
            raise Exception(f"Format {support_format} is not supported")
        
    def get_home(self)->str:
        return str(Path.home())
    
    def get_default_rsa_private_key(self)->str:
        return os.path.join(self.get_home(), ".ssh", "id_rsa")
        
    def get_private_key(self, filename:str, private_key_file:str):
        if private_key_file is not None:
            if not os.path.exists(private_key_file):
                raise Exception(f"ssh key {private_key_file} defined in configuration doesn't exist")
            return private_key_file
        
        if self._configuration.get_file_attribute(filename).get("private_key") is None:
            rsa_path = self.get_default_rsa_private_key()
            if os.path.exists(rsa_path):
                return rsa_path
            else:
                raise Exception(f"ssh key is not defined and {rsa_path} doesn't exist")
        else:
            return self._args.ssh_key_file
            
    def get_master_password(self, password:str)->str:
        if password :
            return password
        else:
            return getpass("Master password : ")

            
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
        
    def get_public_key(self,  public_key_file:str):
        if public_key_file:
            return public_key_file
        
        if os.path.exists(f"/home/{getuser()}/.ssh/id_rsa.pub"):
            return f"/home/{getuser()}/.ssh/id_rsa.pub"
        
        raise Exception(f"Public key file is not provided and default one is not available (/home/{getuser()}/.ssh/id_rsa.pub)")
    
    def get_auth_id(self, auth_id:str=None, public_key_file:str=None)->str:
        if auth_id:
            return auth_id
        
        if public_key_file:
            with open(public_key_file) as f:
                key = f.read()
                key = key.strip()

            re_result = re.search(r"ssh-rsa AAAA[0-9A-Za-z+/]+[=]{0,3} ([^@]+@[^@\r\n]+)", key)
            return re_result.group(1)
        
        return f"{getuser()}@{socket.gethostname()}"
