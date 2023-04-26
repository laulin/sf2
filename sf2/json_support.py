import json
import base64
import logging
import os.path




class JsonSupport:
    """
    Json formated file
    """

    def __init__(self, filename:str) -> None:
        self._filename = filename

        self._log = logging.getLogger(f"{self.__class__.__name__}({filename})")

    def b64encode(self, data:bytes)->str:
        """
        It takes a byte string and returns a base64 encoded string
        
        :param data: The data to be encoded
        :type data: bytes
        :return: A string
        """
        return str(base64.urlsafe_b64encode(data), "utf8")
    
    def b64decode(self, data:str)->str:
        """
        It takes a string, decodes it from base64, and returns the decoded string
        
        :param data: The data to be decoded
        :type data: str
        :return: The decoded string.
        """
        return base64.urlsafe_b64decode(data)

    def load(self)->dict:
        """
        The function loads a JSON file and returns a dictionary. Only work with V2
        :return: A dictionary
        """
        with open(self._filename, "r") as f:
            container = json.load(f)

        bin_container = self.decode(container)
        
        return bin_container
        
    def dump(self, bin_container:dict)->None:
        """
        The function takes a dictionary as an argument and writes it to a file
        
        :param container: The container to dump to the file
        :type container: dict
        """
        with open(self._filename, "w") as f:
            container = self.encode(bin_container)
            json_container = json.dumps(container, indent=4)
            f.write(json_container)

    def encode(self, container:dict)->dict:
        return self._walk(container, self._callback_encode)
    
    def decode(self, container:dict)->dict:
        return self._walk(container, self._callback_decode)

    def _walk(self, container:dict, callback)->dict:

        if isinstance(container, dict):
            tmp = dict()
            for k, v in container.items():
                tmp[k] = self._walk(v, callback)
            return tmp
        elif isinstance(container, list):
                return [self._walk(v, callback) for i,v in enumerate(container)]
        elif isinstance(container, (str, bytes)):
            return callback(container)
        else:
            return container
    
    def _callback_encode(self, data):
        if isinstance(data, bytes):
            return self.b64encode(data)
        else:
            return data
        
    def _callback_decode(self, data):
        if isinstance(data, str):
            try:
                return self.b64decode(data)
            except:
                return data
        else:
            return data
        
    def get_filename(self)->str:
        return self._filename
    
    def is_exist(self)->bool:
        return os.path.exists(self._filename)
