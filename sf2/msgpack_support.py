import msgpack
import logging
import os.path




class MsgpackSupport:
    """
    Message pack formated file
    """

    def __init__(self, filename:str) -> None:
        self._filename = filename

        self._log = logging.getLogger(f"{self.__class__.__name__}({filename})")

   
    def load(self)->dict:
        """
        The function loads a Message pack file and returns a dictionary
        :return: A dictionary
        """
        with open(self._filename, "rb") as f:
            data = f.read()
            container = msgpack.unpackb(data)

        return container
    
        
    def dump(self, container:dict)->None:
        """
        The function takes a dictionary as an argument and writes it to a file
        
        :param container: The container to dump to the file
        :type container: dict
        """
        with open(self._filename, "wb") as f:
            msgpack_container = msgpack.packb(container)
            f.write(msgpack_container)

        
    def get_info(self)->str:
        return self._filename
    
    
    def is_exist(self)->bool:
        return os.path.exists(self._filename)
