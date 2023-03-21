import os.path
import json
import base64
import secrets
import logging

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from cryptography.exceptions import InvalidSignature

from sf2.cipher import Cipher


class ContainerBase:
    """
    Abstract layer on file encryption.
    """
    SALT_SIZE = 32
    IV_SIZE = 32
    MASTER_KEY_CHECK_SIZE = 32
    KDF_ITERATION = 48000
    KDF_LENGTH = 32

    def __init__(self, filename:str) -> None:
        self._filename = filename

        self._log = logging.getLogger(f"{self.__class__.__name__}({filename})")

    def b64encode(self, data:bytes)->str:
        return str(base64.urlsafe_b64encode(data), "utf8")
    
    def b64decode(self, data:str)->str:
        return base64.urlsafe_b64decode(data)

    def _create_salt(self)->bytes:
        return secrets.token_bytes(ContainerBase.SALT_SIZE)
    
    def _create_iv(self)->bytes:

        return secrets.token_bytes(ContainerBase.IV_SIZE)

    def kdf(self, salt:bytes, password:str, iterations:int)->str:

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=ContainerBase.KDF_LENGTH,
            salt=salt,
            iterations=iterations,
        )
        
        password_bytes = bytes(password, "utf8")
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))

        return key
    
    def load(self)->dict:
        with open(self._filename, "r") as f:
            container = json.load(f)

        version = container.get("version", "1")
        if version != "2":
            raise Exception(f"Container version {version} not supported")
        
        return container
        
    def dump(self, container:dict)->None:
        with open(self._filename, "w") as f:
            json_container = json.dumps(container, indent=4)
            f.write(json_container)
    
    def set_master_key_signature(self, container:dict, master_key:bytes)->None:
        challenge = secrets.token_bytes(ContainerBase.MASTER_KEY_CHECK_SIZE)

        hmac = HMAC(master_key, hashes.SHA256())
        hmac.update(challenge)
        signature = hmac.finalize()

        container["auth"]["challenge"] = self.b64encode(challenge)
        container["auth"]["signature"] = self.b64encode(signature)

    
    def check_master_key_signature(self, container:dict, master_key:bytes)->None:

        challenge = self.b64decode(container["auth"]["challenge"])
        signature = self.b64decode(container["auth"]["signature"])

        hmac = HMAC(master_key, hashes.SHA256())
        hmac.update(challenge)
        generated_signature = hmac.finalize()

        if signature != generated_signature:
            raise InvalidSignature("Master key is invalid")


    def create(self, password:str, force:bool=False, _iterations:int=None)->None:

        if _iterations is None:
            _iterations = ContainerBase.KDF_ITERATION

        if not force and os.path.exists(self._filename):
            raise FileExistsError(self._filename)
        
        master_iv = self._create_salt()
        master_data_key = self._create_iv()
        master_key = self.kdf(master_iv, password, _iterations)

        fernet_master_data_key = Fernet(master_key)
        encrypted_master_data_key = fernet_master_data_key.encrypt(master_data_key)
        
        fernet_data = Fernet(self.b64encode(master_data_key))
        encrypted_data = fernet_data.encrypt(b"")


        container = {
            "version" : "2",
            "auth" : {
                "master_iv" : self.b64encode(master_iv),
                "encrypted_master_data_key" : self.b64encode(encrypted_master_data_key),
                "users":{}
            },
            "data" : self.b64encode(encrypted_data) 
        }

        self.set_master_key_signature(container, master_key)
        
        with open(self._filename, "w") as f:
            json_container = json.dumps(container)
            f.write(json_container)

        self._log.info(f"Creation of {self._filename}")

    def get_master_data_key(self, container:dict, password:str, _iterations:int=None)->bytes:

        encrypted_master_data_key = self.b64decode(container["auth"]["encrypted_master_data_key"])

        master_key = self.get_master_key(container, password, _iterations)

        fernet_master_data_key = Fernet(master_key)
        master_data_key = fernet_master_data_key.decrypt(encrypted_master_data_key)

        return self.b64encode(master_data_key)
    
    def get_master_key(self, container:dict, password:str, _iterations:int=None)->bytes:
        if _iterations is None:
            _iterations = ContainerBase.KDF_ITERATION

        master_iv = self.b64decode(container["auth"]["master_iv"])
        master_key = self.kdf(master_iv, password, _iterations)

        self.check_master_key_signature(container, master_key)

        return master_key
    
    def get_plain_data(self, container:dict, master_data_key:bytes)->bytes:
        encrypted_data = self.b64decode(container["data"])

        fernet_data = Fernet(master_data_key)
        data = fernet_data.decrypt(encrypted_data)

        return data

    def set_plain_data(self, container:dict, data:bytes, master_data_key:bytes)->None:
        fernet_data = Fernet(master_data_key)
        encrypted_data = fernet_data.encrypt(data)

        container["data"] = self.b64encode(encrypted_data)

    def read(self, password:str, _iterations:int=None)->bytes:
        
        container = self.load()

        master_data_key = self.get_master_data_key(container, password, _iterations)

        return self.get_plain_data(container, master_data_key)
    
    def write(self, data:bytes, password:str, _iterations:int=None)->None:

        container = self.load()

        master_data_key = self.get_master_data_key(container, password, _iterations)

        self.set_plain_data(container, data, master_data_key)

        self.dump(container)

    def convert_v1_to_v2(self, password:str, _iterations:int=None):
        
        with open(self._filename, "r") as f:
            container = f.read()

        data = Cipher().decrypt(password, container)

        self.create(password, True, _iterations)
        self.write(data, password, _iterations)
