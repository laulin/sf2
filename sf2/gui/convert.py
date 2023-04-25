from pywebio import *

from sf2.gui.tools import *
from sf2.convert_container import convert_container

HELP_TITLE = "Help"
HELP_TEXT = """
This is the help
"""


class Convert:
    def __init__(self, configFile:str) -> None:
        self._config_file = configFile
        
    def do(self):

        if len(pin.pin["convert_password"]) == 0:
            output.toast("Empty password is not allowed", color=RED)
            return
        
        password = pin.pin["convert_password"]
              
        try:
            infilename, outfilename = check_input_output_file("convert_infilename", "convert_outfilename")
        except Exception as e:
            output.toast(f"{e}", color=RED)
            return

        force = pin.pin["convert_force"] == ["allow overwrite ?"]
        support_format = pin.pin["convert_format"]
       
        try:
            convert_container(infilename, outfilename, password, support_format, force)
           
        except Exception as e:
            output.toast(f"Can't convert : {e}", color=RED)
            return

        output.toast("Your file was converted", color=BLUE)

    def help(self):
        output.popup(HELP_TITLE, HELP_TEXT)

    def create(self):
        return output.put_column([
            pin.put_input("convert_infilename", help_text="Enter the input file path here", label="Input plaintext file"), 
            pin.put_input("convert_outfilename", help_text="Enter the output file path here", label="Output encrypted file"), 
            pin.put_input("convert_password", "password", help_text="Enter your password here", label="Master Password"),
            output.put_text("Options"),
            output.put_row([
                pin.put_checkbox("convert_force",options=["allow overwrite ?"]),
                pin.put_radio("convert_format", ["msgpack", "json"], value="msgpack")
            ]),
            output.put_row([
                output.put_button("Convert", onclick=self.do),
                output.put_button("Help", onclick=self.help),
            ]),
        ])