
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

from cryptography.hazmat.primitives.serialization import load_ssh_public_key
from cryptography.hazmat.primitives.serialization import load_ssh_private_key
from cryptography.hazmat.primitives.asymmetric import padding


from sf2.container_base import ContainerBase


class ContainerSSH(ContainerBase):
    """
    Abstract layer on file encryption.
    """

    def __init__(self, filename:str) -> None:
        super().__init__(filename)


    def load_ssh_public_key(self, public_ssh_file:str)->None:

        with open(public_ssh_file, "r") as f:
            file_data = f.read()
            public_key = load_ssh_public_key(bytes(file_data, "utf8"))

        user_host = file_data.split(" ")[2].strip()

        return file_data, user_host, public_key
    
    
    def load_ssh_private_key(self, private_ssh_file:str, password_private_ssh_file:bytes)->None:

        with open(private_ssh_file, "rb") as f:
            private_key = load_ssh_private_key(f.read(), password_private_ssh_file)

        return private_key


    def add_ssh_key(self, password:str, public_ssh_file:str, auth_id:str=None, _iterations:int=None)->None:
        container = self.load()
        master_key = self.get_master_key(container, password, _iterations)
        
        file_data, user_host, public_key = self.load_ssh_public_key(public_ssh_file)

        if auth_id is None:
            auth_id = user_host

        encrypted_master_key = public_key.encrypt(
            master_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        if auth_id in container["auth"]["users"] and "ssh" in container["auth"]["users"][auth_id]:
            raise Exception(f"Public key for {auth_id} is already present")
        
        auth_container = container["auth"]["users"].setdefault(auth_id, {})
        auth_container["ssh"] = {
            "public-key" : file_data,
            "encrypted_master_key" : self.b64encode(encrypted_master_key),
        }

        self.dump(container)


    def get_master_key_ssh(self, container:dict, auth_id:str, private_ssh_file:str, password_private_ssh_file:bytes):

        private_key = self.load_ssh_private_key(private_ssh_file, password_private_ssh_file)

        if auth_id not in container["auth"]["users"] and "ssh" in container["auth"]["users"][auth_id]:
            raise Exception("Public key is not registed")
        
        chuck = container["auth"]["users"][auth_id]["ssh"]
        encrypted_master_key = self.b64decode(chuck["encrypted_master_key"])

        master_key = private_key.decrypt(
            encrypted_master_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        self.check_master_key_signature(container, master_key)

        return master_key
    
    
    def get_master_data_key_ssh(self, container:dict, auth_id:str, private_ssh_file:str, password_private_ssh_file:bytes)->str:
        master_key = self.get_master_key_ssh(container, auth_id, private_ssh_file, password_private_ssh_file)

        encrypted_master_data_key = self.b64decode(container["auth"]["encrypted_master_data_key"])
        fernet_master_data_key = Fernet(master_key)
        master_data_key = fernet_master_data_key.decrypt(encrypted_master_data_key)

        return self.b64encode(master_data_key)


    def read(self, auth_id:str, private_ssh_file:str, password_private_ssh_file:bytes=None)->bytes:
        
        container = self.load()

        master_data_key = self.get_master_data_key_ssh(container, auth_id, private_ssh_file, password_private_ssh_file)

        return self.get_plain_data(container, master_data_key)
    
    
    def write(self, data:bytes, auth_id:str, private_ssh_file:str, password_private_ssh_file:bytes=None)->None:

        container = self.load()

        master_data_key = self.get_master_data_key_ssh(container, auth_id, private_ssh_file, password_private_ssh_file)
        self.set_plain_data(container, data, master_data_key)

        self.dump(container)