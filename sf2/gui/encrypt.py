from pathlib import Path

from pywebio import *

from sf2.gui.tools import *
from sf2.core import Core

HELP_TITLE = "Help"
HELP_TEXT = """
This is the help
"""


class Encrypt:
    def __init__(self) -> None:
        pass
        
    def do(self):

        if len(pin.pin["encrypt_password"]) == 0:
            output.toast("Empty password is not allowed", color=RED)
            return

        if pin.pin["encrypt_password"] != pin.pin["encrypt_password_check"]:
            output.toast("Password are incorrect", color=RED)
            return
        password = pin.pin["encrypt_password"]
        
        try:
            Path(pin.pin["encrypt_infilename"]).resolve()
        except (OSError, RuntimeError):
            output.toast("Input input file path is invalid", color=RED)
        infilename = pin.pin["encrypt_filename"]

        try:
            Path(pin.pin["encrypt_outfilename"]).resolve()
        except (OSError, RuntimeError):
            output.toast("Input output file path is invalid", color=RED)
        outfilename = pin.pin["encrypt_outfilename"]

        force = pin.pin["encrypt_force"] == ["allow overwrite ?"]
        support_format = pin.pin["encrypt_format"]

        if support_format is None:
            output.toast("Please select a format", color=ORANGE)
            return
        
        core = Core()
        core.encrypt(infilename, outfilename, password, support_format, force)

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
                pin.put_radio("encrypt_format", ["msgpack", "json"])
            ]),
            output.put_row([
                output.put_button("Create", onclick=self.do),
                output.put_button("Help", onclick=self.help),
            ]),
        ])