from pathlib import Path

from pywebio import *

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
    
def check_input_output_file(input_name, output_name):
    infilename = pin.pin[input_name]
    try:
        Path(infilename).resolve()
        with open(infilename):
            pass
    except (OSError, RuntimeError) as e:
        raise Exception(f"Input file is invalid ({e})")

    outfilename = pin.pin[output_name]
    try:
        Path(outfilename).resolve()
    except (OSError, RuntimeError) as e:
        raise Exception(f"Output file is invalid ({e})")
    
    return infilename, outfilename

def check_input_file(input_name):
    infilename = pin.pin[input_name]
    try:
        Path(infilename).resolve()
        with open(infilename):
            pass
    except (OSError, RuntimeError) as e:
        raise Exception(f"Input file is invalid ({e})")

    return infilename