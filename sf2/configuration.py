import os.path
from pathlib import Path
import yaml

class Configuration:
    def __init__(self, _home_fonction=Path.home) -> None:
        self._home_function = _home_fonction

    def get_home(self)->str:
        return str(self._home_function())
    
    def get_configuration_path(self)->str:
        return os.path.join([self.get_home(), ".sf2", "config"])
    
    def load_configuration(self)->dict:
        full_path = self.get_configuration_path()
        
        if not os.path.exists(full_path):
            return {}

        with open(full_path, "r") as f:
            return yaml.safe_load_all(f)
        
    def get_file_attribute(self, filename:str, data:dict=None)->dict:

        if data is None:
            data = self.load_configuration()

        return data.get(filename)

        