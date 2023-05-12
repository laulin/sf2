import logging
import os.path
import re

from sf2.openinram import OpenInRAM
from sf2.file_object import FileObject
from sf2.ssh_file_object import SSHFileObject

from sf2.container_ssh import ContainerSSH
from sf2.container_base import ContainerBase
from sf2.json_support import JsonSupport
from sf2.msgpack_support import MsgpackSupport



class Core:
    def __init__(self, _iterations:int=None) -> None:
        self._iterations = _iterations
        self._log = logging.getLogger(self.__class__.__name__)

    def encrypt(self, infilename:str, outfilename:str, password:str, support_format:str="msgpack", force:bool=False):
        support = self.get_support(outfilename, support_format)
        container = ContainerBase(support)
        
        with open(infilename, "rb") as f:
            data = f.read()

        container.create(password, force, self._iterations)
        container.write(data, password, self._iterations)

    def decrypt(self, infilename:str, outfilename:str, password:str, support_format:str="msgpack", force:bool=False):
        if not force and os.path.exists(outfilename):
            raise Exception(f"file {outfilename} already exist")
        
        support = self.get_support(infilename, support_format)
        container = ContainerBase(support)
        data = container.read(password,self._iterations)


        with open(outfilename, "wb") as f:
            f.write(data)

    def decrypt_ssh(self, infilename:str, outfilename:str, private_key_file:str=None, private_key_password:str=None, auth_id:str=None, support_format:str="msgpack", force:bool=False):
        if not force and os.path.exists(outfilename):
            raise Exception(f"file {outfilename} already exist")
        
        support = self.get_support(infilename, support_format)
        base = ContainerBase(support)
        container = ContainerSSH(base)
        auth_id = self.get_auth_id(auth_id)
        data = container.read(auth_id, private_key_file, private_key_password)

        with open(outfilename, "wb") as f:
            f.write(data)

    def verify(self, filename:str, password:str=None, support_format:str="msgpack")->bool:
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
            self._log.debug(f"Error during verify_ssh : {e}")
            return False


    def open(self, filename:str, program:str, password:str=None, support_format:str="msgpack"):
        support = self.get_support(filename, support_format)

        file_object = FileObject(support, password, self._iterations)

        open_in_ram = OpenInRAM(file_object, program)
        open_in_ram.run()

    def open_ssh(self, filename:str, program:str, private_key_file:str=None, private_key_password:str=None, auth_id:str=None, support_format:str="msgpack" ):

        support = self.get_support(filename, support_format)
        file_object = SSHFileObject(support, auth_id, private_key_file, private_key_password)

        open_in_ram = OpenInRAM(file_object, program)
        open_in_ram.run()

    def ssh_add(self, filename:str, password:str, public_key_file:str=None, auth_id:str=None, support_format:str="msgpack"):
        auth_id = self.get_auth_id(auth_id, public_key_file)

        support = self.get_support(filename, support_format)
        base = ContainerBase(support)
        container = ContainerSSH(base)
        container.add_ssh_key(password, public_key_file, auth_id, self._iterations)

    def ssh_rm(self, filename:str, password:str, auth_id_pattern:str=None, support_format:str="msgpack"):
        support = self.get_support(filename, support_format)
        base = ContainerBase(support)
        container = ContainerSSH(base)
        container.remove_ssh_key(password, auth_id_pattern, self._iterations)

        # Once remove at least one ssh key, we need to change all keys to prevent leaked key to be reused
        base.change_password(password, password)
        container.update_master_key(password)

    def ssh_ls(self, filename:str, auth_id_pattern:str=None, support_format:str="msgpack"):
        output = list()
        support = self.get_support(filename, support_format)
        base = ContainerBase(support)
        container = ContainerSSH(base)
        for user, pk in container.list_ssh_key(auth_id_pattern).items():
            output.append((user, pk))

        return output

    def new(self, filename:str, password:str, force:bool=False, support_format:str="msgpack"):
        if not force and os.path.exists(filename):
            raise Exception(f"file {filename} already exist")
        
        support = self.get_support(filename, support_format)
        container = ContainerBase(support)
        container.create(password, force)
        container.write(b"", password)

    def change_password(self, filename:str, old_password:str, new_password:str, support_format:str="msgpack"):

        support = self.get_support(filename, support_format)
        base = ContainerBase(support)
        container = ContainerSSH(base)
        base.change_password(old_password, new_password, self._iterations)
        container.update_master_key(new_password, self._iterations)

    def get_support(self, filename:str, support_format:str):
        if support_format == "json":
            return JsonSupport(filename)
        elif support_format == "msgpack":
            return MsgpackSupport(filename)
        else:
            raise Exception(f"Format {support_format} is not supported")
        
    def get_private_key(self, filename:str, private_key_file:str):
        if private_key_file is not None:
            if not os.path.exists(private_key_file):
                raise Exception(f"ssh key {private_key_file} defined in configuration doesn't exist")
            return private_key_file
              
    def get_auth_id(self, auth_id:str=None, public_key_file:str=None)->str:
        if auth_id:
            return auth_id
        
        if public_key_file:
            with open(public_key_file) as f:
                key = f.read()
                key = key.strip()

            re_result = re.search(r"ssh-rsa AAAA[0-9A-Za-z+/]+[=]{0,3} ([^@]+@[^@\r\n]+)", key)
            return re_result.group(1)
        
        raise Exception("No auth_id defined nor availaible in public key")
