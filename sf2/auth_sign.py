from hashlib import sha256

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization import PrivateFormat
from cryptography.hazmat.primitives.serialization import PublicFormat
from cryptography.hazmat.primitives.serialization import NoEncryption



class AuthSign:
    def __init__(self, container:dict) -> None:
        self._container = container

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
    
    def add_keys(self, master_key:bytes)->dict:
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        private_key_bytes = private_key.private_bytes(Encoding.Raw, PrivateFormat.Raw, encryption_algorithm=NoEncryption())
        public_key_bytes = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)

        fernet = Fernet(master_key)
        private_key_bytes_encrypted = fernet.encrypt(private_key_bytes)

        self._container["auth"]["public_key"] = public_key_bytes
        self._container["auth"]["encrypted_private_key"] = private_key_bytes_encrypted

        return self._container
    
    def sign(self, master_key:bytes)->dict:
        private_key_bytes_encrypted = self._container["auth"]["encrypted_private_key"]
        fernet = Fernet(master_key)
        private_key_bytes = fernet.decrypt(private_key_bytes_encrypted)
        private_key = Ed25519PrivateKey.from_private_bytes(private_key_bytes)

        hash_value = self.sha256_dict(self._container["auth"])
        signature = private_key.sign(hash_value)
        self._container["auth_signature"] = signature

        return self._container
    
    def verify(self)->None:
        public_key_bytes = self._container["auth"]["public_key"]
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        signature = self._container["auth_signature"] 
        hash_value = self.sha256_dict(self._container["auth"])
        public_key.verify(signature, hash_value)
