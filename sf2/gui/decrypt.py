

from pywebio import *

from sf2.gui.tools import *
from sf2.core_with_environment import CoreWithEnvironment

HELP_TITLE = "Help"
HELP_TEXT = """
This is the help
"""


class Decrypt:
    def __init__(self, configFile:str) -> None:
        self._config_file = configFile
        
    def do_password(self):
        try:
            infilename, outfilename = check_input_output_file("decrypt_password_infilename", "decrypt_password_outfilename")
        except Exception as e:
            output.toast(f"{e}", color=RED)
            return

        force = pin.pin["decrypt_password_force"] == ["allow overwrite ?"]
        support_format = pin.pin["decrypt_password_format"]
        
        core = CoreWithEnvironment()

        if len(pin.pin["decrypt_password_password"]) == 0:
            output.toast("Empty password is not allowed", color=RED)
            return
            
        password = pin.pin["decrypt_password_password"]
        try:
            core.decrypt(infilename, outfilename, password, support_format, force)
        except Exception as e:
            output.toast(f"failed to decrypt ({e})", color=RED)
            return


        output.toast("Your file was decrypted", color=BLUE)

    def do_ssh(self):
        try:
            infilename, outfilename = check_input_output_file("decrypt_ssh_infilename", "decrypt_ssh_outfilename")
        except Exception as e:
            output.toast(f"{e}", color=RED)
            return

        force = pin.pin["decrypt_ssh_force"] == ["allow overwrite ?"]
        support_format = pin.pin["decrypt_ssh_format"]
        
        core = CoreWithEnvironment()

        private_key_file = pin.pin.decrypt_private_key_file
        auth_id = pin.pin.decrypt_auth_id
        private_key_password = pin.pin.private_key_password
        try:
            core.decrypt_ssh(infilename, outfilename, private_key_file, private_key_password, auth_id, support_format, force, self._config_file)
        except Exception as e:
            output.toast(f"failed to decrypt ({e})", color=RED)
            return

        output.toast("Your file was decrypted", color=BLUE)

    def help_password(self):
        output.popup(HELP_TITLE, HELP_TEXT)

    def help_ssh(self):
        output.popup(HELP_TITLE, HELP_TEXT)

    def create_password(self):
        return output.put_column([
            pin.put_input("decrypt_password_infilename", help_text="Enter the input file path here", label="Input encrypted file"), 
            pin.put_input("decrypt_password_outfilename", help_text="Enter the output file path here", label="Output plaintext file"),
            pin.put_input("decrypt_password_password", "password", help_text="Enter your password here", label="Master Password"),
            output.put_text("Options"),
            output.put_row([
                pin.put_checkbox("decrypt_password_force",options=["allow overwrite ?"]),
                pin.put_radio("decrypt_password_format", ["msgpack", "json"], value="msgpack")
            ]),
            output.put_row([
                output.put_button("Decrypt", onclick=self.do_password),
                output.put_button("Help", onclick=self.help_password),
            ])
        ])
    
    def create_ssh(self):
        return output.put_column([
            pin.put_input("decrypt_ssh_infilename", help_text="Enter the input file path here", label="Input encrypted file"), 
            pin.put_input("decrypt_ssh_outfilename", help_text="Enter the output file path here", label="Output plaintext file"),
            pin.put_file_upload("decrypt_ssh_private_key_file", placeholder=".ssh/id_ssh"),
            pin.put_input("decrypt_ssh_private_key_password", "password", help_text="Enter your private key password here", label="PK Password"),
            pin.put_input("decrypt_ssh_auth_id", help_text="Enter your auth_id here", label="Input encrypted file"), 
            output.put_text("Options"),
            output.put_row([
                pin.put_checkbox("decrypt_ssh_force",options=["allow overwrite ?"]),
                pin.put_radio("decrypt_ssh_format", ["msgpack", "json"], value="msgpack")
            ]),
            output.put_row([
                output.put_button("Decrypt", onclick=self.do_ssh),
                output.put_button("Help", onclick=self.help_ssh),
            ])
        ])

    def create(self):
        return output.put_tabs([
                {'title': 'SSH', 'content': self.create_ssh()},
                {'title': 'Password', 'content': self.create_password()}
             ])