from sf2.container_base import ContainerBase

class FileObject:
    def __init__(self, support, password:str, _iterations:int=None) -> None:
        self._container = ContainerBase(support)
        self._password = password
        self._iterations = _iterations
        self._info = support.get_filename()

    def decrypt(self)->bytes:
        return self._container.read(self._password, self._iterations)
    
    def encrypt(self, path:str)->None:
        with open(path, "rb") as f:
            data = f.read()
        
        self._container.write(data, self._password, self._iterations)

    def __str__(self) -> str:
        return self._info