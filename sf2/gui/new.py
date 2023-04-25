from pathlib import Path

from pywebio import *

from sf2.gui.tools import *
from sf2.core import Core

HELP_TITLE = "New Function"
HELP_TEXT = """
# New Function - User Manual

The "New" function in our cryptographic software allows you to create a new, empty encrypted file based on a password. Please note that this feature does not support SSH keys. This page will guide you through the process of creating a new encrypted file using a password.

## Creating a New Encrypted File

To create a new encrypted file, follow these steps:

1. Enter the desired file name for the new encrypted file in the "File Name" field.
2. Input a password in the "Password" field. This password will be used to encrypt the file and will be required to access its content later.
3. Re-enter the password in the "Password again" field to ensure that the password is entered correctly.
4. (Optional) Choose the format of the encrypted file (JSON or MSGPACK) using the dropdown menu.

Please note that if a file with the same name already exists, an error message will be displayed. However, you can choose to overwrite the existing file by checking the "Overwrite" box.

Once you have filled in the required information and confirmed that the password matches in both fields, click the "Create" button to proceed. A new, empty encrypted file will be created using the specified password and file format.

By following the instructions provided in this user manual, you can create new encrypted files with ease and ensure that your sensitive data remains protected.
"""

class New:
    def __init__(self, config_file) -> None:
        self._config_file = config_file
        
    def do_new(self):

        if len(pin.pin["new_password"]) == 0:
            output.toast("Empty password is not allowed", color=RED)
            return

        if pin.pin["new_password"] != pin.pin["new_password_check"]:
            output.toast("Password are incorrect", color=RED)
            return
        password = pin.pin["new_password"]
        
        filename = pin.pin["new_filename"]
        try:
            Path(filename).resolve()
        except (OSError, RuntimeError):
            output.toast("File path is invalid", color=RED)

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
                pin.put_radio("new_format", ["msgpack", "json"], value="msgpack")
            ]),
            output.put_row([
                output.put_button("Create", onclick=self.do_new),
                output.put_button("Help", onclick=self.help_new),
            ]),
        ])