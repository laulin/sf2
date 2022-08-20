from tempfile import mkstemp
import os
from threading import Thread

import inotify.adapters

from sf2.cipher import Cipher

RAMFS = "/dev/shm"

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

        self._running = False


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


    def write_back(self, watch_path:str):
        """
        It watches the file at `watch_path` for changes, and when it detects a change, it encrypts the
        file
        
        :param watch_path: The path to the file you want to watch
        :type watch_path: str
        :return: The return value is a tuple of three: the first is an integer representing the event
        mask, the second is the name of the directory or file, and the third is a boolean indicating if
        it is a directory or not.
        """
        i = inotify.adapters.Inotify()

        i.add_watch(RAMFS)

        for event in i.event_gen():

            if not self._running:
                return

            if event is not None:
                (_, type_names, path, filename) = event

                if os.path.join(path, filename) == watch_path:
                    if "IN_CLOSE_WRITE" in type_names:
                        self.encrypt(watch_path)


    def run(self):
        """
        It creates a temporary file in the shared memory, writes the decrypted data to it, opens it in
        the editor, encrypts the file and deletes it
        """

        decrypted = self.decrypt()

        try:
            fd, path = mkstemp(dir=RAMFS, suffix=".plain")
            with os.fdopen(fd, 'w') as f:
                f.write(decrypted)
                f.flush()

                # Run a thread that monitor file change.
                # This way, modification are automatically write back to the encrypted file
                self._running = True
                write_back_thread = Thread(target=self.write_back, args=(path,))
                write_back_thread.start()

                os.system(f"{self._editor} {path}")
                # stopping the write back thread
                self._running = False
            
        except Exception as e:
            print("Something failed : {e}")
        finally:
            os.unlink(path)