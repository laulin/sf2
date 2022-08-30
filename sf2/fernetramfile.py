import base64
import os
import io
import json
import logging

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class FernetRAMFile:
    def __init__(self, filename:str, secret:bytes, mode:str, iterations:int=480000, salt_size=16):
        self._filename = filename
        self._secret = secret
        self._mode = mode
        self._iterations = iterations
        self._salt_size = salt_size
        self._log = logging.getLogger(f"FernetRAMFile({filename})")
        self._data = None

    def __enter__(self):
        self._log.debug("__enter__")
        self._open_file()
        return self._data
     
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._log.debug("__exit__")
        self._close_file()

    def secret_2_key(self, salt:bytes, secret:bytes) -> str:
        if not isinstance(secret, bytes):
            raise TypeError("secret must be a bytes-like object, not str")

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self._iterations,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret))

        return key

    def create_salt(self, _rand=os.getrandom)->bytes:
        salt = _rand(self._salt_size)
        return base64.urlsafe_b64encode(salt)

    def _open_file(self):
        if "r" in self._mode :
            self._log.debug("Open with r")
            return self._open_file_read()
        elif "w" in self._mode :
            self._log.debug("Open with w")
            return self._open_file_write()
        elif "a" in self._mode :
            self._log.debug("Open with a")
            return self._open_file_read()

    def _open_file_read(self):
        if "b" in self._mode:
            buffer = io.BytesIO
        else:
            buffer = io.StringIO

        with open(self._filename, f"r") as f:
            container_data = f.read()
            container = json.loads(container_data)
            data = bytes(container["data"], "utf8")
            salt = bytes(container["salt"], "utf8")

            self._log.debug(f"Open Salt : {salt}")
            self._log.debug(f"Open Data : {data}")

            key = self.secret_2_key(salt, self._secret)
            f = Fernet(key)
            plain = f.decrypt(data)

            if "b" not in self._mode:
                plain = str(plain, "utf8")

            self._data = buffer(plain)

    def _open_file_write(self):
        if "b" in self._mode:
            self._data = io.BytesIO()
        else:
            self._data = io.StringIO()

    def _close_file(self):
        if "a" in self._mode or "w" in self._mode:
            self._close_write_file()

        self._data.close()
        self._data = None

    def _close_write_file(self):
        data = self._data.getvalue()
        self._log.debug(f"Data len : {len(data)}")

        if "b" not in self._mode:
            data = bytes(data, "utf8")

        salt = self.create_salt()
        self._log.debug(f"Close Salt : {salt}")
        key = self.secret_2_key(salt, self._secret)
        
        f = Fernet(key)
        encrypted = f.encrypt(data)
        self._log.debug(f"Close Encrypted : {encrypted}")

        container = {
            "salt" : str(salt, "utf8"),
            "data" : str(encrypted, "utf8")
        }
        container_data = json.dumps(container, indent=4)

        with open(self._filename, f"w") as f:
            f.write(container_data)
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    with FernetRAMFile('foo.bar', b"secret", "w") as f:
        f.write("hello")