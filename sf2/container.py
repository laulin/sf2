import os.path
import json
import base64
import secrets
import time
import logging
from hashlib import sha256

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from cryptography.hazmat.primitives.serialization import load_ssh_public_key
from cryptography.hazmat.primitives.serialization import load_ssh_private_key
from cryptography.hazmat.primitives.asymmetric import padding


class Container:
    """
    Abstract layer on file encryption.
    """
    SALT_SIZE = 32
    IV_SIZE = 32
    KDF_ITERATION = 48000
    KDF_LENGTH = 32

    def __init__(self, filename:str) -> None:
        self._filename = filename

        self._log = logging.getLogger(f"Container({filename})")

    def b64encode(self, data:bytes)->str:
        return str(base64.urlsafe_b64encode(data), "utf8")
    
    def b64decode(self, data:str)->str:
        return base64.urlsafe_b64decode(data)

    def _create_salt(self)->bytes:
        """
        It creates a random 16 byte string, and then encodes it using base64
        
        :param _rand: This is a function that returns a random byte string. The default is os.getrandom,
        which is a secure random number generator
        :return: A random string of bytes that is encoded in base64.
        """
        return secrets.token_bytes(Container.SALT_SIZE)
    
    def _create_iv(self)->bytes:
        """
        It creates a random 16 byte string, and then encodes it using base64
        
        :param _rand: This is a function that returns a random byte string. The default is os.getrandom,
        which is a secure random number generator
        :return: A random string of bytes that is encoded in base64.
        """
        return secrets.token_bytes(Container.IV_SIZE)

    def _kdf(self, salt:bytes, password:str, iterations:int)->str:
        """
        It takes a salt and a password and returns a key for Fernet module
        
        :param salt: a random string of bytes
        :type salt: str
        :param password: The password to use for the key derivation
        :type password: str
        :return: The key is being returned.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=Container.KDF_LENGTH,
            salt=salt,
            iterations=iterations,
        )
        
        password_bytes = bytes(password, "utf8")
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))

        return key

    def create(self, password:str, _iterations:int=None)->None:
        """
        create an encrypted container.
        
        :param password: The password used to encrypt the container
        :type password: str
        :param _iterations: The number of iterations to use for the key derivation function
        :type _iterations: int
        """

        if _iterations is None:
            _iterations = Container.KDF_ITERATION

        if os.path.exists(self._filename):
            raise FileExistsError(self._filename)
        
        master_iv = self._create_salt()
        master_data_key = self._create_iv()
        master_key = self._kdf(master_iv, password, _iterations)

        fernet_master_data_key = Fernet(master_key)
        encrypted_master_data_key = fernet_master_data_key.encrypt(master_data_key)
        
        fernet_data = Fernet(self.b64encode(master_data_key))
        encrypted_data = fernet_data.encrypt(b"")


        container = {
            "version" : "2",
            "auth" : {
                "master_iv" : self.b64encode(master_iv),
                "encrypted_master_data_key" : self.b64encode(encrypted_master_data_key),
                "alt-keys":{}
            },
            "data" : self.b64encode(encrypted_data) 
        }
        
        with open(self._filename, "w") as f:
            json_container = json.dumps(container)
            f.write(json_container)

        self._log.info(f"Creation of {self._filename}")

    def get_master_data_key(self, container:dict, password:str, _iterations:int=None)->bytes:
        """
        > It takes a password, and returns a key
        
        :param container: the container dictionary
        :type container: dict
        :param password: The password you want to use to encrypt the data
        :type password: str
        :param _iterations: The number of iterations to use for the key derivation function
        :type _iterations: int
        :return: The master data key is being returned.
        """
        encrypted_master_data_key = self.b64decode(container["auth"]["encrypted_master_data_key"])

        master_key = self.get_master_key(container, password, _iterations)

        fernet_master_data_key = Fernet(master_key)
        master_data_key = fernet_master_data_key.decrypt(encrypted_master_data_key)

        return self.b64encode(master_data_key)
    
    def load(self)->dict:
        with open(self._filename, "r") as f:
            return json.load(f)
        
    def dump(self, container:dict)->None:
        with open(self._filename, "w") as f:
            json_container = json.dumps(container)
            f.write(json_container)
    
    def get_master_key(self, container:dict, password:str, _iterations:int=None)->bytes:
        if _iterations is None:
            _iterations = Container.KDF_ITERATION

        master_iv = self.b64decode(container["auth"]["master_iv"])
        master_key = self._kdf(master_iv, password, _iterations)

        return master_key
    
    def get_plain_data(self, container:dict, master_data_key:bytes)->bytes:
        encrypted_data = self.b64decode(container["data"])

        fernet_data = Fernet(master_data_key)
        data = fernet_data.decrypt(encrypted_data)

        return data

    def set_plain_data(self, container:dict, data:bytes, master_data_key:bytes):
        fernet_data = Fernet(master_data_key)
        encrypted_data = fernet_data.encrypt(data)

        container["data"] = self.b64encode(encrypted_data)

    def read_master_password(self, password:str, _iterations:int=None)->bytes:
        
        container = self.load()

        master_data_key = self.get_master_data_key(container, password, _iterations)

        return self.get_plain_data(container, master_data_key)
    
    def write_master_password(self, data:bytes, password:str, _iterations:int=None)->None:

        container = self.load()

        master_data_key = self.get_master_data_key(container, password, _iterations)

        self.set_plain_data(container, data, master_data_key)

        self.dump(container)

    def load_ssh_keys(self, private_ssh_file:str)->None:

        public_ssh_file = private_ssh_file + ".pub"
        with open(public_ssh_file, "rb") as f:
            file_data = f.read()
            file_hash = sha256(file_data).hexdigest()
            public_key = load_ssh_public_key(file_data)

        with open(private_ssh_file, "rb") as f:
            private_key = load_ssh_private_key(f.read(), None)

        return file_data, file_hash, public_key, private_key

    def add_ssh_key(self, password:str, private_ssh_file:str, _iteration:int=None)->None:
        container = self.load()
        master_key = self.get_master_key(container, password, _iteration)

        file_data, file_hash, public_key, private_key = self.load_ssh_keys(private_ssh_file)


        alt_key = public_key.encrypt(
            master_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        signature = private_key.sign(
            alt_key,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        if file_hash in container["auth"]["alt-keys"]:
            pk_utf8 = str(file_data)
            user_host = pk_utf8.split(' ')[2][0:-3]
            raise Exception(f"Public key for {user_host} is already present")
        
        container["auth"]["alt-keys"][file_hash] = {
            "ssh-public" : self.b64encode(file_data),
            "alt-key" : self.b64encode(alt_key),
            "signature" :  self.b64encode(signature)
        }

        self.dump(container)

    def get_master_key_ssh(self, container:dict, private_ssh_file:str):

        _, file_hash, public_key, private_key = self.load_ssh_keys(private_ssh_file)

        if file_hash not in container["auth"]["alt-keys"]:
            raise Exception("Public key is not registed")
        
        chuck = container["auth"]["alt-keys"][file_hash]
        signature = self.b64decode(chuck["signature"])
        alt_key = self.b64decode(chuck["alt-key"])

        public_key.verify(
            signature,
            alt_key,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        master_key = private_key.decrypt(
            alt_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return master_key
    
    def get_master_data_key_ssh(self, container:dict, private_ssh_file:str):
        master_key = self.get_master_key_ssh(container, private_ssh_file)

        encrypted_master_data_key = self.b64decode(container["auth"]["encrypted_master_data_key"])
        fernet_master_data_key = Fernet(master_key)
        master_data_key = fernet_master_data_key.decrypt(encrypted_master_data_key)

        return self.b64encode(master_data_key)


    def read_ssh_key(self, private_ssh_file:str)->bytes:
        
        container = self.load()

        master_data_key = self.get_master_data_key_ssh(container, private_ssh_file)

        return self.get_plain_data(container, master_data_key)
    
    def write_ssh_key(self, data:bytes, private_ssh_file:str)->None:

        container = self.load()

        master_data_key = self.get_master_data_key_ssh(container, private_ssh_file)
        self.set_plain_data(container, data, master_data_key)

        self.dump(container)
