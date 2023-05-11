import os.path
from pathlib import Path
import yaml
import socket
from getpass import getuser
import re

from sf2.core import Core

class CoreWithEnvironment:
    def __init__(self, _iterations:int=None, default_public_key:str=None, default_private_key:str=None, default_auth_id:str=None, default_config_file:str=None) -> None:
        self._core = Core(_iterations)

        self._default_public_key = default_public_key
        self._default_private_key = default_private_key
        self._default_auth_id = default_auth_id
        self._default_config_file = default_config_file
 
    def load_configuration(self, config_file:str=None)->dict:
        if config_file is None or config_file == "":
            config_file = self.get_default_config_file()

        if not os.path.exists(config_file):
            return {}

        with open(config_file, "r") as f:
            conf =  yaml.safe_load(f)

        return conf

    def load_specific_configuration(self, filename:str, config_file:str)->dict:
        filename = os.path.abspath(filename)
        conf = self.load_configuration(config_file)
        return conf.get(filename, {})
    
    def encrypt(self, infilename:str, outfilename:str, password:str, support_format:str="msgpack", force:bool=False):
        return self._core.encrypt(infilename, outfilename, password, support_format, force)

    def decrypt(self, infilename:str, outfilename:str, password:str, support_format:str="msgpack", force:bool=False):
        return self._core.decrypt(infilename, outfilename, password, support_format, force)

    def decrypt_ssh(self, infilename:str, outfilename:str, private_key_file:str=None, private_key_password:str=None, auth_id:str=None, support_format:str="msgpack", force:bool=False, config_file:str=None):
        config_file = self.get_config_file(config_file)
        private_key_file, auth_id = self.get_secrets(infilename, config_file, private_key_file, auth_id)
        return self._core.decrypt_ssh(infilename, outfilename, private_key_file, private_key_password, auth_id, support_format, force)
    
    def verify(self, filename:str, password:str=None, support_format:str="msgpack")->bool:
        return self._core.verify(filename, password, support_format)

    def verify_ssh(self, filename:str, private_key_file:str=None, private_key_password:str=None, auth_id:str=None, support_format:str="msgpack", config_file:str=None)->bool:
        config_file = self.get_config_file(config_file)
        private_key_file, auth_id = self.get_secrets(filename, config_file, private_key_file, auth_id)
        return self._core.verify_ssh(filename, private_key_file, private_key_password, auth_id, support_format)

    def open(self, filename:str, program:str, password:str=None, support_format:str="msgpack"):
        return self._core.open(filename, program, password, support_format)

    def open_ssh(self, filename:str, program:str=None, private_key_file:str=None, private_key_password:str=None, auth_id:str=None, support_format:str="msgpack", config_file:str=None):
        config_file = self.get_config_file(config_file)
        private_key_file, auth_id = self.get_secrets(filename, config_file, private_key_file, auth_id)
        program = self.get_program(filename, config_file, program)
        return self._core.open_ssh(filename, program, private_key_file, private_key_password, auth_id, support_format)

    def ssh_add(self, filename:str, password:str, public_key_file:str=None, auth_id:str=None, support_format:str="msgpack"):
        public_key_file = self.get_public_key(public_key_file)
        auth_id = self.get_auth_id(auth_id, public_key_file)
        
        return self._core.ssh_add(filename, password, public_key_file, auth_id, support_format)

    def ssh_rm(self, filename:str, password:str, auth_id:str=None, support_format:str="msgpack", config_file:str=None):
        config_file = self.get_config_file(config_file)
        _, auth_id = self.get_secrets(filename, config_file, "no_key", auth_id)
        return self._core.ssh_rm(filename, password, auth_id, support_format)

    def ssh_ls(self, filename:str, support_format:str="msgpack"):
        return self._core.ssh_ls(filename, support_format)

    def new(self, filename:str, password:str, force:bool=False, support_format:str="msgpack"):
        return self._core.new(filename, password, force, support_format)
    
    def change_password(self, filename:str, old_password:str, new_password:str, support_format:str="msgpack"):
        return self._core.change_password(filename, old_password, new_password, support_format)
    
    def get_default_private_key(self)->str:
        if self._default_private_key is None:
            return os.path.join(str(Path.home()), ".ssh", "id_rsa")
        else:
            return self._default_private_key
    
    def is_default_private_key_exist(self)->bool:
        return os.path.exists(self.get_default_private_key())
    
    def get_default_public_key(self)->str:
        if self._default_public_key is None:
            return os.path.join(str(Path.home()), ".ssh", "id_rsa.pub")
        else:
            return self._default_public_key
    
    def is_default_public_key_exist(self)->bool:
        return os.path.exists(self.get_default_public_key())
    
    def get_config_file(self, config_file:str)->str:
        if config_file:
            return config_file
        else:
            if self._default_config_file is None:
                return os.path.join(str(Path.home()), ".sf2", "config.yaml")
            else:
                return self._default_config_file
    
    def get_default_auth_id(self)->str:
        if self._default_auth_id is None:
            return f"{getuser()}@{socket.gethostname()}"
        else:
            return self._default_auth_id
    
    def get_auth_id(self, auth_id:str, public_key_file:str)->str:
        if auth_id:
            return auth_id
        elif public_key_file is not None:
            return self.get_auth_id_from_public_key(public_key_file)
        else:
            return self.get_default_auth_id()
        
    def get_auth_id_from_public_key(self, public_key_file:str):
        with open(public_key_file) as f:
            key = f.read()
            key = key.strip()

        re_result = re.search(r"ssh-rsa AAAA[0-9A-Za-z+/]+[=]{0,3} ([^@]+@[^@\r\n]+)", key)
        return re_result.group(1)
        
    def get_public_key(self, public_key_file:str):
        if public_key_file:
            return public_key_file
        elif self.is_default_public_key_exist():
            return self.get_default_public_key()
        else:
            raise Exception("Public key is not available")
    
    def get_secrets(self, filename:str, config_file:str, private_key_file:str, auth_id:str):
        sub_conf = self.load_specific_configuration(filename, config_file)

        output_private_key_file = ""
        output_auth_id = ""

        if private_key_file:
            output_private_key_file = private_key_file
        elif "private_key_file" in sub_conf:
            output_private_key_file = sub_conf["private_key_file"]
        elif self.is_default_private_key_exist():
            output_private_key_file = self.get_default_private_key()
        else:
            raise Exception("Private key is not available")
        
        if auth_id:
            output_auth_id = auth_id
        elif "auth_id" in sub_conf:
            output_auth_id = sub_conf["auth_id"]
        else:
            output_auth_id = self.get_default_auth_id()

        return output_private_key_file, output_auth_id
    
    def get_program(self, filename:str, config_file:str, program:str):
        if program:
            return program
        
        sub_conf = self.load_specific_configuration(filename, config_file)

        if "program" in sub_conf:
            return sub_conf["program"]
        else:
            raise Exception("Can't find program args")
        