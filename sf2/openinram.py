from tempfile import mkstemp
import os
from threading import Thread
import logging
import re

import inotify.adapters
from flufl.lock import Lock
from flufl.lock import TimeOutError

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

        i.add_watch(watch_path)

        for event in i.event_gen():

            if not self._running:
                return

            if event is not None:
                (_, type_names, _, _) = event

                if "IN_CLOSE_WRITE" in type_names:
                    try:
                        self._file_object.encrypt(watch_path)
                        self._log.debug(f"Sync plain ({watch_path}) to encrypted")
                    except FileNotFoundError as e:
                        self._log.debug(f"No Sync plain ({watch_path}) : {e}")

    def read_back(self, destination_path:str):
        watch_path = str(self._file_object)
        self._log.debug(f"Watch encrypted file {watch_path} and destination is {destination_path}")
        i = inotify.adapters.Inotify()

        i.add_watch(watch_path)

        for event in i.event_gen():

            if not self._running:
                return

            if event is not None:
                (_, type_names, _, _) = event

                if "IN_CLOSE_WRITE" in type_names:
                    decrypted = self._file_object.decrypt()
                    try:
                        os.chmod(destination_path, 0o600)
                        with open(destination_path, 'wb') as f:
                            f.write(decrypted)
                            f.flush()
                        os.chmod(destination_path, 0o400)
                        self._log.debug(f"Sync plain ({watch_path}) from encrypted")
                    except Exception as e:
                        self._log.warning(f"Failed to sync : {e}")

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
            
        except Exception as e:
            self._log.error(f"Something failed : {e}")
        finally:
            self._log.debug(f"Tmp file {path} safely remove")
            os.unlink(path)
            # stopping the thread
            self._running = False

    def run_read(self):
        decrypted = self._file_object.decrypt()

        try:
            fd, path = mkstemp(dir=RAMFS, suffix=".plain")
            self._log.debug(f"Create tmp file {path} (fd={fd})")
            with os.fdopen(fd, 'wb') as f:
                f.write(decrypted)
                f.flush()
            self._log.debug(f"Tmp file {path} is now read only")
            os.chmod(path, 0o400)

            # Run a thread that monitor file change.
            # This way, modification are automatically write back to the encrypted file
            self._running = True
            read_back_thread = Thread(target=self.read_back, args=(path,))
            read_back_thread.start()

            command = self._command.format(filename=path)
            self._log.debug(f"Run command : {command}")
            os.system(command)
            
        except Exception as e:
            self._log.error(f"Something failed : {e}")
        finally:
            self._log.debug(f"Tmp file {path} safely remove")
            os.unlink(path)
            # stopping the thread
            self._running = False


    def run(self):
        # Remove logs from inotify
        logging.getLogger('inotify.adapters').setLevel(logging.WARNING)

        filename = str(self._file_object)
        lock_file = filename + ".lock"

        try:
            with Lock(lock_file, default_timeout=0):
                self._log.debug(f"Entering in write allowed section")
                self.run_write()
        except TimeOutError:
            self._log.debug(f"Entering in read only section")
            self.run_read()
