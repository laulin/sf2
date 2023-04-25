from sf2.cipher import Cipher
from sf2.container_base import ContainerBase
from sf2.json_support import JsonSupport
from sf2.msgpack_support import MsgpackSupport

def convert_container(infilename:str, outfilename:str, password:str, support_format:str="msgpack", force:bool=False, _iterations:str=None):
    cipher = Cipher()
    
    with open(infilename, "r") as f:
        data = f.read()

    plain = cipher.decrypt(password, data)

    if support_format == "json":
        support = JsonSupport(outfilename)
    elif support_format == "msgpack":
        support = MsgpackSupport(outfilename)
    else:
        raise Exception("Support format is invalid")
    
    base = ContainerBase(support)
    base.create(password, force, _iterations)
    base.write(plain, password, _iterations)