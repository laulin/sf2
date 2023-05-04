from tempfile import mkstemp
import os
from threading import Thread
import logging
import re

import inotify.adapters
from flufl.lock import Lock

RAMFS = "/dev/shm"

class OpenInRAM:
    def __init__(self, file_object, command:str):
        """
        This is a constructor for a class that initializes some instance variables and sets a command
        string with a filename placeholder.
        
        :param file_object: The file object is a reference to a file that will be used by the code. It
        could be a file that is being read from or written to
        :param command: The `command` parameter is a string that represents a command to be executed. It
        may contain the placeholder `{filename}` which will be replaced with the actual filename when
        the command is executed
        :type command: str
        """
        
        self._file_object = file_object
        self._log = logging.getLogger(f"{self.__class__.__name__}({file_object})")
        self._running = False

        self._command = self.interpole_command(command)
        self._log.debug(f"Command : {self._command}")

    def interpole_command(self, command:str)->str:
        command = command.strip()
        if re.search(r"[\{\[]\s*filename\s*[\}\]]", command) is None:
            return command + " {filename}"
        else:
            command = re.sub(r"[\[]\s*filename\s*[\]]", "{filename}", command)
            return command

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
                        self._log.debug(f"Sync plain ({watch_path}) to encrypted")
                        self._file_object.encrypt(watch_path)

    def run_write(self):
        decrypted = self._file_object.decrypt()

        try:
            fd, path = mkstemp(dir=RAMFS, suffix=".plain")
            self._log.debug(f"Create tmp file {path} (fd={fd})")
            with os.fdopen(fd, 'wb') as f:
                f.write(decrypted)
                f.flush()

                # Run a thread that monitor file change.
                # This way, modification are automatically write back to the encrypted file
                self._running = True
                write_back_thread = Thread(target=self.write_back, args=(path,))
                write_back_thread.start()

                command = self._command.format(filename=path)
                self._log.debug(f"Run command : {command}")
                os.system(command)
                # stopping the write back thread
                self._running = False
            
        except Exception as e:
            self._log.error(f"Something failed : {e}")
        finally:
            self._log.debug(f"Tmp file {path} safely remove")
            os.unlink(path)


    def run(self):
        """
        It creates a temporary file in the shared memory, writes the decrypted data to it, opens it in
        the editor, encrypts the file and deletes it
        """
        # Remove logs from inotify
        logging.getLogger('inotify.adapters').setLevel(logging.WARNING)

        filename = str(self._file_object)
        lock_file = filename + ".lock"
        lock = Lock(lock_file)

        if not lock.is_locked:
            with lock:
                self.run_write()
        else:
            raise Exception(f"File {filename} is already open")