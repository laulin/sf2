import base64
from operator import contains
import os
import json

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Cipher:
    def __init__(self) -> None:
        pass

    def password_2_key(self, salt:bytes, password:str)->bytes:
        """
        It takes a salt and a password and returns a key for Fernet module
        
        :param salt: a random string of bytes
        :type salt: bytes
        :param password: The password to use for the key derivation
        :type password: str
        :return: The key is being returned.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        password = bytes(password, "utf8")
        key = base64.urlsafe_b64encode(kdf.derive(password))

        return key

    def create_salt(self, _rand=os.getrandom)->bytes:
        """
        It creates a random 16 byte string, and then encodes it using base64
        
        :param _rand: This is a function that returns a random byte string. The default is os.getrandom,
        which is a secure random number generator
        :return: A random string of bytes that is encoded in base64.
        """
        salt = _rand(16)
        return base64.urlsafe_b64encode(salt)

    def encrypt(self, password:str, data:str)->dict:
        """
        > It takes a password and some data, creates a salt, creates a key from the salt and password,
        encrypts the data with the key, and returns the salt and encrypted data in a JSON object.
        
        :param password: The password that will be used to encrypt the data
        :type password: str
        :param data: The data to be encrypted
        :type data: str
        :return: A JSON string containing the salt and the encrypted data.
        """
        salt = self.create_salt()
        key = self.password_2_key(salt, password)
        
        f = Fernet(key)
        encrypted = f.encrypt(bytes(data, "utf8"))

        container = {
            "salt" : str(salt, "utf8"),
            "data" : str(encrypted, "utf8")
        }
        return json.dumps(container, indent=4)


    def decrypt(self, password:str, container_bytes:bytes)->str:
        """
        > It takes a password and a container, and returns the plaintext
        
        :param password: The password you want to use to encrypt the data
        :type password: str
        :param container_bytes: the bytes of the container file
        :type container_bytes: bytes
        :return: The decrypted data.
        """
        container = json.loads(container_bytes)
        data = bytes(container["data"], "utf8")
        salt = bytes(container["salt"], "utf8")

        key = self.password_2_key(salt, password)
        f = Fernet(key)
        plain = f.decrypt(data)

        return str(plain, "utf8")

    def encrypt_file(self, password:str, infilename:str, outfilename:str)->None:
        """
        It opens the file, reads the contents, encrypts the contents, and writes the encrypted contents
        to a file
        
        :param password: The password to use to encrypt the file
        :type password: str
        :param infilename: The name of the file to encrypt
        :type infilename: str
        :param outfilename: The name of the file to write the encrypted data to. If this is None, the
        encrypted data will be printed to the console
        :type outfilename: str
        """
        with open(infilename, "r") as f:
            plain = f.read()

        container = self.encrypt(password, plain)

        if outfilename is None:
            print(container)
        else:
            with open(outfilename, "w") as f:
                f.write(container)

    def decrypt_file(self, password:str, infilename:str, outfilename:str)->None:
        """
        It decrypts a file.
        
        :param password: The password to use for encryption/decryption
        :type password: str
        :param infilename: The name of the file to be decrypted
        :type infilename: str
        :param outfilename: The name of the file to write the decrypted text to. If this is None, then
        the decrypted text is printed to the console
        :type outfilename: str
        """
        with open(infilename, "r") as f:
            container = f.read()

        plain = self.decrypt(password, container)

        if outfilename is None:
            print(plain)
        else:
            with open(outfilename, "w") as f:
                f.write(plain)

    def verify_file(self, password:str, infilename:str)->bool:
        """
        > It opens the file, reads the contents, and then tries to decrypt it. If it can decrypt it, it
        returns True. If it can't decrypt it, it returns False
        
        :param password: The password to use for encryption/decryption
        :type password: str
        :param infilename: the name of the file to be encrypted
        :type infilename: str
        :return: a boolean value.
        """
        
        with open(infilename, "r") as f:
            container = f.read()
        try:
            plain = self.decrypt(password, container)
            return True
        except:
            return False



