from pathlib import Path

from pywebio import *

from sf2.gui.tools import *
from sf2.core import Core

HELP_TITLE = "Help"
HELP_TEXT = """
This is the help
"""

class New:
    def __init__(self) -> None:
        pass
        
    def do_new(self):

        if len(pin.pin["new_password"]) == 0:
            output.toast("Empty password is not allowed", color=RED)
            return

        if pin.pin["new_password"] != pin.pin["new_password_check"]:
            output.toast("Password are incorrect", color=RED)
            return
        password = pin.pin["new_password"]
        
        try:
            Path(pin.pin["new_filename"]).resolve()
        except (OSError, RuntimeError):
            output.toast("File path is invalid", color=RED)
        filename = pin.pin["new_filename"]

        force = pin.pin["new_force"] == ["allow overwrite ?"]
        support_format = pin.pin["new_format"]

        if support_format is None:
            output.toast("Please select a format", color=ORANGE)
            return
        
        core = Core()
        core.new(filename, password, force, support_format)

        output.toast("Your file was created", color=BLUE)

    def help_new(self):
        output.popup(HELP_TITLE, HELP_TEXT)

    def create(self):
        return output.put_column([
            pin.put_input("new_filename", help_text="Enter the file path here", label="File path"), 
            pin.put_input("new_password", "password", help_text="Enter your password here", label="Master Password"),
            pin.put_input("new_password_check", "password", help_text="Enter your password here, again"),
            output.put_text("Options"),
            output.put_row([
                pin.put_checkbox("new_force",options=["allow overwrite ?"]),
                pin.put_radio("new_format", ["msgpack", "json"])
            ]),
            output.put_row([
                output.put_button("Create", onclick=self.do_new),
                output.put_button("Help", onclick=self.help_new),
            ]),
        ])