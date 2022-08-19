from tempfile import mkstemp
import os

from sf2.cipher import Cipher

class Extern:
    def __init__(self, password:str, filename:str, editor:str):
        """
        The function __init__() is a constructor that takes three parameters: password, filename, and
        editor
        
        :param password: The password you want to use to encrypt the file
        :type password: str
        :param filename: The name of the file to be encrypted
        :type filename: str
        :param editor: The editor you want to use to edit the file
        :type editor: str
        """
        self._password = password
        self._filename = filename
        self._editor = editor

    def decrypt(self):
        """
        It opens the file, reads the contents, creates a cipher object, and then calls the decrypt
        method on the cipher object.
        :return: The decrypted data.
        """
        with open(self._filename) as f:
            container = f.read()
        cipher = Cipher()
        return cipher.decrypt(self._password, container)

    def encrypt(self, path:str):
        """
        It opens a file, reads the contents, encrypts the contents, and writes the encrypted contents to
        a file
        
        :param path: The path to the file you want to encrypt
        :type path: str
        """
        with open(path) as f:
            plain = f.read()

        cipher = Cipher()
        encrypted = cipher.encrypt(self._password, plain)

        with open(self._filename, "w") as f:
            f.write(encrypted)

    def run(self):
        """
        > It creates a temporary file in the shared memory, writes the decrypted data to it, opens it in
        the editor, encrypts the file and deletes it
        """

        decrypted = self.decrypt()

        try:
            fd, path = mkstemp(dir="/dev/shm")
            with os.fdopen(fd, 'w') as f:
                f.write(decrypted)
                f.flush()
                os.system(f"{self._editor} {path}")

            self.encrypt(path)
            
        except Exception as e:
            print("Something failed : {e}")
        finally:
            os.unlink(path)