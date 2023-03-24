import logging


from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

from cryptography.hazmat.primitives.serialization import load_ssh_public_key
from cryptography.hazmat.primitives.serialization import load_ssh_private_key
from cryptography.hazmat.primitives.asymmetric import padding



class ContainerSSH():
    """
    Add support of SSH keys.
    """

    def __init__(self, base) -> None:
        self._base = base
        self._log = logging.getLogger(f"{self.__class__.__name__}")

    def load_ssh_public_key(self, public_ssh_file:str)->None:
        """
        > This function takes a file path to a public ssh key file, reads the file, and returns the file
        data, the user and host, and the public key
        
        :param public_ssh_file: The path to the public ssh key file
        :type public_ssh_file: str
        :return: The file data, the user host, and the public key.
        """

        with open(public_ssh_file, "r") as f:
            file_data = f.read()
            public_key = load_ssh_public_key(bytes(file_data, "utf8"))

        user_host = file_data.split(" ")[2].strip()

        return file_data, user_host, public_key
    
    
    def load_ssh_private_key(self, private_ssh_file:str, password_private_ssh_file:bytes)->None:
        """
        This function loads a private ssh key from a file and returns it as a string
        
        :param private_ssh_file: The path to the private key file
        :type private_ssh_file: str
        :param password_private_ssh_file: The password for the private key file
        :type password_private_ssh_file: bytes
        :return: The private key is being returned.
        """

        with open(private_ssh_file, "rb") as f:
            private_key = load_ssh_private_key(f.read(), password_private_ssh_file)

        return private_key


    def add_ssh_key(self, password:str, public_ssh_file:str, auth_id:str=None, _iterations:int=None)->None:
        """
        It takes a master password, a public ssh key file, and an optional auth_id, and adds the public key
        to the auth container, encrypting the master key with the public key
        
        :param password: The password you used to create the container
        :type password: str
        :param public_ssh_file: The path to the public key file
        :type public_ssh_file: str
        :param auth_id: The name of the user. This is used to identify the user, like test@computer. If not privided, it uses the one of the SSH key.
        :type auth_id: str
        :param _iterations: The number of iterations to use when generating the master key. If not
        specified, the default value is used
        :type _iterations: int
        """
        container = self._base.load()
        master_key = self._base.get_master_key(container, password, _iterations)
        
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
            "encrypted_master_key" : encrypted_master_key,
        }

        self._base.dump(container)

    def remove_ssh_key(self, auth_id:str)->None:
        """
        This function removes the SSH key of a user
        
        :param auth_id: The user's auth_id
        :type auth_id: str
        """
        container = self._base.load()

        if auth_id in container["auth"]["users"] :
            if "ssh" in container["auth"]["users"][auth_id]:
                del container["auth"]["users"][auth_id]["ssh"]
                if len(container["auth"]["users"][auth_id]) == 0:
                    del container["auth"]["users"][auth_id]

            else:
                raise Exception(f"user {auth_id} doesn't use SSH key")
        else:
            raise Exception(f"user {auth_id} doesn't exists")
            
        self._base.dump(container)

    def get_master_key_ssh(self, container:dict, auth_id:str, private_ssh_file:str, password_private_ssh_file:bytes):
        """
        The function decrypts the master key using the private key of the user.
        
        :param container: the container dictionary
        :type container: dict
        :param auth_id: The user's ID
        :type auth_id: str
        :param private_ssh_file: The path to the private key file
        :type private_ssh_file: str
        :param password_private_ssh_file: The password to decrypt the private ssh key
        :type password_private_ssh_file: bytes
        :return: The master key is being returned.
        """

        private_key = self.load_ssh_private_key(private_ssh_file, password_private_ssh_file)

        if auth_id not in container["auth"]["users"] and "ssh" in container["auth"]["users"][auth_id]:
            raise Exception("Public key is not registed")
        
        chuck = container["auth"]["users"][auth_id]["ssh"]
        encrypted_master_key = chuck["encrypted_master_key"]

        master_key = private_key.decrypt(
            encrypted_master_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        self._base.check_master_key_signature(container, master_key)

        return master_key
    
    
    def get_master_data_key_ssh(self, container:dict, auth_id:str, private_ssh_file:str, password_private_ssh_file:bytes)->str:
        """
        It decrypts the master data key.
        
        :param container: the container dictionary
        :type container: dict
        :param auth_id: The ID of the authentication method you want to use
        :type auth_id: str
        :param private_ssh_file: The path to the private key file
        :type private_ssh_file: str
        :param password_private_ssh_file: The password for the private ssh file
        :type password_private_ssh_file: bytes
        :return: The master data key is being returned.
        """
        master_key = self.get_master_key_ssh(container, auth_id, private_ssh_file, password_private_ssh_file)

        encrypted_master_data_key = container["auth"]["encrypted_master_data_key"]
        fernet_master_data_key = Fernet(master_key)
        master_data_key = fernet_master_data_key.decrypt(encrypted_master_data_key)

        return self._base.b64encode(master_data_key)


    def read(self, auth_id:str, private_ssh_file:str, password_private_ssh_file:bytes=None)->bytes:
        """
        The function reads the encrypted data from the file using SSH KEY and returns the decrypted data
        
        :param auth_id: The ID of the authentication you want to use
        :type auth_id: str
        :param private_ssh_file: The path to the private key file
        :type private_ssh_file: str
        :param password_private_ssh_file: The password for the private ssh file
        :type password_private_ssh_file: bytes
        :return: The plain data.
        """
        
        container = self._base.load()

        master_data_key = self.get_master_data_key_ssh(container, auth_id, private_ssh_file, password_private_ssh_file)

        return self._base.get_plain_data(container, master_data_key)
    
    
    def write(self, data:bytes, auth_id:str, private_ssh_file:str, password_private_ssh_file:bytes=None)->None:
        """
        It writes data to the container.
        
        :param data: the data to be encrypted
        :type data: bytes
        :param auth_id: The ID of the authentication key to use
        :type auth_id: str
        :param private_ssh_file: The path to the private key file
        :type private_ssh_file: str
        :param password_private_ssh_file: The password for the private ssh key file
        :type password_private_ssh_file: bytes
        """

        container = self._base.load()

        master_data_key = self.get_master_data_key_ssh(container, auth_id, private_ssh_file, password_private_ssh_file)
        self._base.set_plain_data(container, data, master_data_key)

        self._base.dump(container)