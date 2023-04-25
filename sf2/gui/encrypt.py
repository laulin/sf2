from pathlib import Path

from pywebio import *

from sf2.gui.tools import *
from sf2.core_with_environment import CoreWithEnvironment

HELP_TITLE = "Help"
HELP_TEXT = """
This is the help
"""


class Encrypt:
    def __init__(self, configFile:str) -> None:
        self._config_file = configFile
        
    def do(self):

        if len(pin.pin["encrypt_password"]) == 0:
            output.toast("Empty password is not allowed", color=RED)
            return

        if pin.pin["encrypt_password"] != pin.pin["encrypt_password_check"]:
            output.toast("Password are incorrect", color=RED)
            return
        password = pin.pin["encrypt_password"]
              
        try:
            infilename, outfilename = check_input_output_file("encrypt_infilename", "encrypt_outfilename")
        except Exception as e:
            output.toast(f"{e}", color=RED)
            return

        force = pin.pin["encrypt_force"] == ["allow overwrite ?"]
        support_format = pin.pin["encrypt_format"]
       
        core = CoreWithEnvironment()
        try:
            core.encrypt(infilename, outfilename, password, support_format, force)
           
        except Exception as e:
            output.toast(f"Oups : {e}", color=RED)
            return

        output.toast("Your file was encrypted", color=BLUE)

    def help(self):
        output.popup(HELP_TITLE, HELP_TEXT)

    def create(self):
        return output.put_column([
            pin.put_input("encrypt_infilename", help_text="Enter the input file path here", label="Input plaintext file"), 
            pin.put_input("encrypt_outfilename", help_text="Enter the output file path here", label="Output encrypted file"), 
            pin.put_input("encrypt_password", "password", help_text="Enter your password here", label="Master Password"),
            pin.put_input("encrypt_password_check", "password", help_text="Enter your password here, again"),
            output.put_text("Options"),
            output.put_row([
                pin.put_checkbox("encrypt_force",options=["allow overwrite ?"]),
                pin.put_radio("encrypt_format", ["msgpack", "json"], value="msgpack")
            ]),
            output.put_row([
                output.put_button("Encrypt", onclick=self.do),
                output.put_button("Help", onclick=self.help),
            ]),
        ])