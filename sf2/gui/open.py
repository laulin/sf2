

from pywebio import *

from sf2.gui.tools import *
from sf2.core_with_environment import CoreWithEnvironment

HELP_TITLE = "Help"
HELP_TEXT = """
This is the help
"""


class Open:
    def __init__(self, configFile:str) -> None:
        self._config_file = configFile
        
    def do_password(self):
        try:
            infilename = check_input_file("open_password_infilename")
        except Exception as e:
            output.toast(f"{e}", color=RED)
            return

        support_format = pin.pin["open_password_format"]
        
        core = CoreWithEnvironment()

        if len(pin.pin["open_password_password"]) == 0:
            output.toast("Empty password is not allowed", color=RED)
            return
            
        password = pin.pin["open_password_password"]
        program = pin.pin["open_password_program"]
        try:
            core.open(infilename, program, password, support_format)
        except Exception as e:
            output.toast(f"failed to decrypt ({e})", color=RED)
            return


        output.toast("Your file was decrypted", color=BLUE)

    def do_ssh(self):
        try:
            infilename = check_input_file("open_ssh_infilename")
        except Exception as e:
            output.toast(f"{e}", color=RED)
            return

        support_format = pin.pin["open_ssh_format"]
        
        core = CoreWithEnvironment()

        private_key_file = pin.pin["open_ssh_private_key_file"]
        auth_id = pin.pin["open_ssh_auth_id"]
        private_key_password = bytes(pin.pin["open_ssh_private_key_password"], "utf8")
        program = pin.pin["open_ssh_program"]
        try:
            core.open_ssh(infilename, program, private_key_file, private_key_password, auth_id, support_format, self._config_file)
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
            pin.put_input("open_password_infilename", help_text="Enter the input file path here", label="Input encrypted file"), 
            pin.put_input("open_password_password", "password", help_text="Enter your password here", label="Master Password"),
            pin.put_input("open_password_program", help_text="use {filename} for templating", label="Program"),
            output.put_text("Options"),
            pin.put_radio("open_password_format", ["msgpack", "json"], value="msgpack"),
            output.put_row([
                output.put_button("Decrypt", onclick=self.do_password),
                output.put_button("Help", onclick=self.help_password),
            ])
        ])
    
    def create_ssh(self):
        return output.put_column([
            pin.put_input("open_ssh_infilename", help_text="Enter the input file path here", label="Input encrypted file"), 
            pin.put_input("open_ssh_private_key_file", placeholder=".ssh/id_ssh", label="Private key file"),
            pin.put_input("open_ssh_private_key_password", "password", help_text="Enter your private key password here", label="Private key password"),
            pin.put_input("open_ssh_auth_id", help_text="Enter your auth_id here", label="Auth ID"), 
            pin.put_input("open_ssh_program", help_text="use {filename} for templating", label="Program"),
            output.put_text("Options"),
            pin.put_radio("open_ssh_format", ["msgpack", "json"], value="msgpack"),
            output.put_row([
                output.put_button("Open", onclick=self.do_ssh),
                output.put_button("Help", onclick=self.help_ssh),
            ])
        ])

    def create(self):
        return output.put_tabs([
                {'title': 'SSH', 'content': self.create_ssh()},
                {'title': 'Password', 'content': self.create_password()}
             ])