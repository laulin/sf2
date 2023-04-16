import os.path
from pathlib import Path
import yaml

class Configuration:
    def __init__(self, home:str) -> None:
        self._home = home
 
    def load_configuration(self)->dict:
       
        if not os.path.exists(self._home):
            return {}

        with open(self._home, "r") as f:
            conf =  yaml.safe_load(f)

        print(conf)
        return conf
        
    def get_file_attribute(self, filename:str)->dict:
        data = self.load_configuration()
        return data.get(filename, {})

        