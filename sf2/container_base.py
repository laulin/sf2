
import base64
import secrets
import logging

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from cryptography.exceptions import InvalidSignature

from sf2.cipher import Cipher
from sf2.auth_sign import AuthSign


class ContainerBase:
    """
    Abstract layer on file encryption.
    Support only master password.
    """
    SALT_SIZE = 32
    IV_SIZE = 32
    MASTER_KEY_CHECK_SIZE = 32
    KDF_ITERATION = 48000
    KDF_LENGTH = 32

    def __init__(self, support) -> None:
        self._support = support

        self._log = logging.getLogger(f"{self.__class__.__name__}({support.get_filename()})")

    def b64encode(self, data:bytes)->str:
        """
        It takes a byte string and returns a base64 encoded string
        
        :param data: The data to be encoded
        :type data: bytes
        :return: A string
        """
        return str(base64.urlsafe_b64encode(data), "utf8")
    
    def b64decode(self, data:str)->str:
        """
        It takes a string, decodes it from base64, and returns the decoded string
        
        :param data: The data to be decoded
        :type data: str
        :return: The decoded string.
        """
        return base64.urlsafe_b64decode(data)

    def _create_master_data_key(self)->bytes:
        """
        It creates a random salt of size 16 bytes.
        :return: A random byte string of length SALT_SIZE
        """
        return secrets.token_bytes(ContainerBase.SALT_SIZE)
    
    
    def _create_iv(self)->bytes:
        """
        It creates a random initialization vector (IV) of 16 bytes.
        :return: A random byte string of length 16.
        """
        return secrets.token_bytes(ContainerBase.IV_SIZE)
    

    def kdf(self, salt:bytes, password:str, iterations:int)->str:
        """
        The function takes a password and a salt, and returns a key
        
        :param salt: a random string of bytes
        :type salt: bytes
        :param password: The password used to encrypt the container
        :type password: str
        :param iterations: The number of iterations to use in the key derivation function
        :type iterations: int
        :return: The key is being returned.
        """

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=ContainerBase.KDF_LENGTH,
            salt=salt,
            iterations=iterations,
        )
        
        password_bytes = bytes(password, "utf8")
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))

        return key
    
  
    def set_master_key_signature(self, container:dict, master_key:bytes)->None:
        """
        It takes a container and a master key, and adds a challenge and a signature to the container auth section
        
        :param container: The container dictionary
        :type container: dict
        :param master_key: The master key that will be used to encrypt the container
        :type master_key: bytes
        """
        challenge = secrets.token_bytes(ContainerBase.MASTER_KEY_CHECK_SIZE)

        hmac = HMAC(master_key, hashes.SHA256())
        hmac.update(challenge)
        signature = hmac.finalize()

        container["auth"]["challenge"] = challenge
        container["auth"]["signature"] = signature

    
    def check_master_key_signature(self, container:dict, master_key:bytes)->None:
        """
        The function checks if the signature of the master key is valid
        
        :param container: the container that was decrypted
        :type container: dict
        :param master_key: The master key that was generated by the client
        :type master_key: bytes
        """

        challenge = container["auth"]["challenge"]
        signature = container["auth"]["signature"]

        hmac = HMAC(master_key, hashes.SHA256())
        hmac.update(challenge)
        generated_signature = hmac.finalize()

        if signature != generated_signature:
            self._log.debug(f"signature is {generated_signature}, expected is {signature}")
            raise InvalidSignature("Master key is invalid")
        
    def _create_container(self, password:str, data:bytes, users:dict, _iterations:int=None)->dict:     
        master_iv = self._create_iv()
        master_data_key = self._create_master_data_key()
        master_key = self.kdf(master_iv, password, _iterations)

        fernet_master_data_key = Fernet(master_key)
        encrypted_master_data_key = fernet_master_data_key.encrypt(master_data_key)
        
        fernet_data = Fernet(self.b64encode(master_data_key))
        encrypted_data = fernet_data.encrypt(data)


        container = {
            "version" : "2",
            "auth" : {
                "master_iv" : master_iv,
                "encrypted_master_data_key" : encrypted_master_data_key,
                "users":users,
                "challenge":None,
                "signature":None

            },
            "data" : encrypted_data
        }

        self.set_master_key_signature(container, master_key)

        auth_sign = AuthSign(container, _iterations=_iterations)
        auth_sign.add_keys(password)
        container = auth_sign.sign(password)

        return container


    def create(self, password:str, force:bool=False, _iterations:int=None)->None:
        """
        The function creates a new container file, encrypts the data with a master key, encrypts the
        master key with a password, and stores the encrypted master key in the container file.
        
        :param password: The password used to encrypt the container
        :type password: str
        :param force: If the file already exists, it will raise an error. If force is set to True, it
        will overwrite the file, defaults to False
        :type force: bool (optional)
        :param _iterations: The number of iterations to use when generating the master key
        :type _iterations: int
        """

        if _iterations is None:
            _iterations = ContainerBase.KDF_ITERATION

        if not force and self._support.is_exist():
            raise Exception(f"{self._support.get_filename()} already exists")
        
        container = self._create_container(password, b"", {}, _iterations)
        
        self.dump(container)

        self._log.info(f"Creation of {self._support.get_filename()}")


    def get_master_data_key(self, container:dict, password:str, _iterations:int=None)->bytes:
        """
        The function takes the encrypted master data key from the container, decrypts it using the
        master key, and returns the decrypted master data key
        
        :param container: the container dictionary
        :type container: dict
        :param password: The password you used to encrypt the file
        :type password: str
        :param _iterations: The number of iterations to use when generating the master key
        :type _iterations: int
        :return: The master data key is being returned.
        """

        encrypted_master_data_key = container["auth"]["encrypted_master_data_key"]

        master_key = self.get_master_key(container, password, _iterations)

        fernet_master_data_key = Fernet(master_key)
        master_data_key = fernet_master_data_key.decrypt(encrypted_master_data_key)

        return self.b64encode(master_data_key)


    def get_master_key(self, container:dict, password:str, _iterations:int=None)->bytes:
        """
        It takes a container, a password, and an optional number of iterations, and returns a master
        key.
        
        :param container: the container dictionary
        :type container: dict
        :param password: The password you entered when you created the container
        :type password: str
        :param _iterations: The number of iterations to use for the key derivation function
        :type _iterations: int
        :return: The master key is being returned.
        """
        if _iterations is None:
            _iterations = ContainerBase.KDF_ITERATION

        master_iv = container["auth"]["master_iv"]
        master_key = self.kdf(master_iv, password, _iterations)

        self.check_master_key_signature(container, master_key)

        return master_key
    

    def get_plain_data(self, container:dict, master_data_key:bytes)->bytes:
        """
        Decrypts the data in the container using the master key
        
        :param container: The container that you want to decrypt
        :type container: dict
        :param master_data_key: This is the key that was used to encrypt the data
        :type master_data_key: bytes
        :return: The data is being returned.
        """
        encrypted_data = container["data"]

        fernet_data = Fernet(master_data_key)
        data = fernet_data.decrypt(encrypted_data)

        return data


    def set_plain_data(self, container:dict, data:bytes, master_data_key:bytes)->None:
        """
        set the data in the container.
        
        :param container: The container that will hold the encrypted data
        :type container: dict
        :param data: the data to be encrypted
        :type data: bytes
        :param master_data_key: This is the key that is used to encrypt the data
        :type master_data_key: bytes
        """
        fernet_data = Fernet(master_data_key)
        encrypted_data = fernet_data.encrypt(data)

        container["data"] = encrypted_data


    def read(self, password:str, _iterations:int=None)->bytes:
        """
        It takes a password and returns the plaintext data
        
        :param password: The password used to encrypt the data
        :type password: str
        :param _iterations: The number of iterations to use when generating the master data key. If not
        specified, the number of iterations specified in the container will be used
        :type _iterations: int
        :return: The plain data.
        """
        
        container = self.load()

        # Check if the auth section was not modifier
        auth_sign = AuthSign(container)
        auth_sign.verify()

        master_data_key = self.get_master_data_key(container, password, _iterations)

        return self.get_plain_data(container, master_data_key)
    

    def write(self, data:bytes, password:str, _iterations:int=None)->None:
        """
        It takes a password and a data blob, and writes the data blob to the container as encrypted data.
        
        :param data: the data to be encrypted
        :type data: bytes
        :param password: The password used to encrypt the data
        :type password: str
        :param _iterations: The number of iterations to use when generating the master key
        :type _iterations: int
        """

        container = self.load()

        # Check if the auth section was not modifier
        auth_sign = AuthSign(container)
        auth_sign.verify()

        master_data_key = self.get_master_data_key(container, password, _iterations)

        self.set_plain_data(container, data, master_data_key)

        self.dump(container)


    def convert_v1_to_v2(self, password:str, _iterations:int=None):
        """
        It reads the old version of the file, decrypts it, and then writes it to the new version of
        the file
        
        :param password: The password used to encrypt the data
        :type password: str
        :param _iterations: The number of iterations to use when generating the key
        :type _iterations: int
        """
        
        with open(self._filename, "r") as f:
            container = f.read()

        data = Cipher().decrypt(password, container)

        self.create(password, True, _iterations)
        self.write(data, password, _iterations)

    def load(self)->dict:
        return self._support.load()
    
    def dump(self, container:dict)->None:
        self._support.dump(container)

    def sign_and_dump(self, container:dict, password:str, _iterations:int=None)->None:
        if _iterations is None:
            _iterations = ContainerBase.KDF_ITERATION

        auth_sign = AuthSign(container, _iterations)
        container = auth_sign.sign(password)

        self.dump(container)
