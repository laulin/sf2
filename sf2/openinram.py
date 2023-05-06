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
        
    def on_write_inotify_thread(self, source_path:str, destination_path:str, callback:callable):
        i = inotify.adapters.Inotify()

        i.add_watch(source_path)

        for event in i.event_gen():

            if not self._running:
                return

            if event is not None:
                (_, type_names, _, _) = event

                if "IN_CLOSE_WRITE" in type_names:
                    callback(destination_path)

    def write_back_callback(self, file_to_encrypt:str):
        try:
            self._file_object.encrypt(file_to_encrypt)
            self._log.debug(f"Sync plain ({file_to_encrypt}) to encrypted")
        except FileNotFoundError as e:
            self._log.debug(f"No Sync plain ({file_to_encrypt}) : {e}")

    def read_back_callback(self, plain_text_path:str):
        decrypted = self._file_object.decrypt()
        try:
            os.chmod(plain_text_path, 0o600)
            with open(plain_text_path, 'wb') as f:
                f.write(decrypted)
                f.flush()
            os.chmod(plain_text_path, 0o400)
            self._log.debug(f"Sync plain ({plain_text_path}) from encrypted")
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
                write_back_thread = Thread(target=self.on_write_inotify_thread, args=(path,path, self.write_back_callback))
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
            read_back_thread = Thread(target=self.on_write_inotify_thread, args=(str(self._file_object), path, self.read_back_callback))
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
                self._log.debug(f"File opened in R/W")
                self.run_write()
        except TimeOutError:
            self._log.debug(f"File opened in RO")
            self.run_read()
