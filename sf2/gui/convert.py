from pywebio import *

from sf2.gui.tools import *
from sf2.convert_container import convert_container

HELP_TITLE = "Convert Function"
HELP_TEXT = """
# Convert Function - User Manual

The "Convert" function in our cryptographic software allows you to convert encrypted files from SF2 v1.xx format to SF2 v2.xx format. This page will guide you through the process of converting your encrypted files to the newer format.

Please note that future SF2 version 3 will not support version 1 of the file format. It is recommended to convert your SF2 v1.xx files to SF2 v2.xx to ensure compatibility with future software updates.

To convert an encrypted file from SF2 v1.xx to SF2 v2.xx, follow these steps:

1. Enter the existing encrypted file's name in the "Input Encrypted File (v1.xx)" field.
2. Enter the desired file name for the new encrypted file (in v2.xx format) in the "Output Encrypted File (v2.xx)" field.
3. Input the password in the "Password" field. This password must be the same as the one used to encrypt the file.

Please note that by default, the conversion process will not proceed if the output encrypted file already exists. To overwrite the existing file, check the "Overwrite" box.

Once you have filled in the required information, click the "Convert" button to proceed. A new encrypted file in SF2 v2.xx format will be created using the specified password, containing the converted data from the existing encrypted file.

As with the "Decrypt" function, you can choose the format of the new encrypted file (JSON or MSGPACK) using the dropdown menu.

By following the instructions provided in this user manual, you can convert your encrypted files from SF2 v1.xx to SF2 v2.xx format, ensuring compatibility and seamless integration with future software updates.
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
            pin.put_input("convert_password", "password", help_text="Enter your password here", label="Password"),
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