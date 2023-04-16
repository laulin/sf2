from sf2.container_base import ContainerBase
from sf2.container_ssh import ContainerSSH

class SSHFileObject:
    def __init__(self, support, auth_id:str, private_ssh_file:str, password_private_ssh_file:bytes=None) -> None:
        self._base = ContainerBase(support)
        self._container = ContainerSSH(self._base)
        self._auth_id = auth_id
        self._private_ssh_file = private_ssh_file
        self._password_private_ssh_file = password_private_ssh_file
        self._info = support.get_info()

    def decrypt(self)->bytes:
        return self._container.read(self._auth_id, self._private_ssh_file, self._password_private_ssh_file)
    
    def encrypt(self, path:str)->None:
        with open(path, "rb") as f:
            data = f.read()
        
        self._container.write(data, self._auth_id, self._private_ssh_file, self._password_private_ssh_file)

    def __str__(self) -> str:
        return self._info