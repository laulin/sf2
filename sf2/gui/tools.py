from sf2.json_support import JsonSupport
from sf2.msgpack_support import MsgpackSupport


RED = '#ff2121'
ORANGE = '#ff8821'
BLUE = '#2188ff'

def get_format(support_format:str, filename:str):
    if support_format == "json":
        return JsonSupport(filename)
    elif support_format == "msgpack":
        return MsgpackSupport(filename)