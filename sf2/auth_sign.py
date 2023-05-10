from hashlib import sha256
import secrets
import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization import PrivateFormat
from cryptography.hazmat.primitives.serialization import PublicFormat
from cryptography.hazmat.primitives.serialization import NoEncryption



class AuthSign:
    IV_SIZE = 32
    KDF_LENGTH = 32
    KDF_ITERATION = 48000
    def __init__(self, container:dict, _iterations:int=None) -> None:
        self._container = container

        if _iterations is None:
            self._iterations = AuthSign.KDF_ITERATION
        else:
            self._iterations = _iterations

    def dict_to_bytes(self, data)->bytes:
        if isinstance(data, dict):
            tmp = b""
            for k in sorted(data.keys()) :
                tmp = tmp + bytes(k, "utf8") + self.dict_to_bytes(data[k])

            return tmp
        elif isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return bytes(data, "utf8")
        else:
            raise Exception(f"Type {type(data)} is not supported")
        
    def sha256_dict(self, data)->str:
        fetch = self.dict_to_bytes(data)
        hash = sha256(fetch).digest()
        return hash
    
    def kdf(self, salt:bytes, password:str, iterations:int)->str:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=AuthSign.KDF_LENGTH,
            salt=salt,
            iterations=iterations,
        )
        
        password_bytes = bytes(password, "utf8")
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))

        return key
    
    def add_keys(self, password:str)->dict:
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        private_key_bytes = private_key.private_bytes(Encoding.Raw, PrivateFormat.Raw, encryption_algorithm=NoEncryption())
        public_key_bytes = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)

        auth_salt = secrets.token_bytes(AuthSign.IV_SIZE)
        key = self.kdf(auth_salt, password, self._iterations)

        fernet = Fernet(key)
        private_key_bytes_encrypted = fernet.encrypt(private_key_bytes)
        self._container["auth"]["sign"] = {
            "public_key" : public_key_bytes,
            "encrypted_private_key" : private_key_bytes_encrypted,
            "auth_iv" : auth_salt
        }

        return self._container
    
    def sign(self, password:str)->dict:
        private_key_bytes_encrypted = self._container["auth"]["sign"]["encrypted_private_key"]
        auth_salt = self._container["auth"]["sign"]["auth_iv"]
        key = self.kdf(auth_salt, password, self._iterations)

        fernet = Fernet(key)
        private_key_bytes = fernet.decrypt(private_key_bytes_encrypted)
        private_key = Ed25519PrivateKey.from_private_bytes(private_key_bytes)

        hash_value = self.sha256_dict(self._container["auth"])
        signature = private_key.sign(hash_value)
        self._container["auth_signature"] = signature

        return self._container
    
    def verify(self)->None:
        public_key_bytes = self._container["auth"]["sign"]["public_key"]
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        signature = self._container["auth_signature"] 
        hash_value = self.sha256_dict(self._container["auth"])
        public_key.verify(signature, hash_value)
