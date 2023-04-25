from pywebio import *

from sf2.gui.tools import *
from sf2.core_with_environment import CoreWithEnvironment

HELP_TITLE = "Encrypt Function"
HELP_TEXT = """
# Encrypt Function - User Manual

The "Encrypt" function in our cryptographic software allows you to create a new encrypted file that contains the data from an existing plaintext file. Like the "New" function, this feature is based on a password and does not support SSH keys. This page will guide you through the process of creating a new encrypted file using a password while encrypting the content of an existing plaintext file.

## Creating an Encrypted File from a Plaintext File

To create a new encrypted file from a plaintext file, follow these steps:

1. Enter the path to the plaintext file you want to encrypt in the "Input Plaintext File" field.
2. Enter the desired file name for the new encrypted file in the "File Name" field.
3. Input a password in the "Password" field. This password will be used to encrypt the file and will be required to access its content later.
4. Re-enter the password in the "Password again" field to ensure that the password is entered correctly.
5. (Optional) Choose the format of the encrypted file (JSON or MSGPACK) using the dropdown menu.

Please note that if a file with the same name already exists, an error message will be displayed. However, you can choose to overwrite the existing file by checking the "Overwrite" box.

Once you have filled in the required information and confirmed that the password matches in both fields, click the "Encrypt" button to proceed. A new encrypted file will be created using the specified password and file format, containing the data from the input plaintext file.

By following the instructions provided in this user manual, you can create encrypted files from existing plaintext files with ease, ensuring that your sensitive data remains protected.
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