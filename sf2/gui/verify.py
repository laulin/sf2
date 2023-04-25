

from pywebio import *

from sf2.gui.tools import *
from sf2.core_with_environment import CoreWithEnvironment

HELP_TITLE = "Help"
HELP_TEXT = """
This is the help
"""


class Verify:
    def __init__(self, configFile:str) -> None:
        self._config_file = configFile
        
    def do_password(self):
        try:
            infilename = check_input_file("verify_password_infilename")
        except Exception as e:
            output.toast(f"{e}", color=RED)
            return

        support_format = pin.pin["verify_password_format"]
        
        core = CoreWithEnvironment()

        if len(pin.pin["verify_password_password"]) == 0:
            output.toast("Empty password is not allowed", color=RED)
            return
            
        password = pin.pin["verify_password_password"]
        try:
            if core.verify(infilename, password, support_format):
                output.toast("Your file is OK", color=BLUE)
            else:
                output.toast("Your file is KO", color=ORANGE)
        except Exception as e:
            output.toast(f"failed to verify ({e})", color=RED)
            return


    def do_ssh(self):
        try:
            infilename = check_input_file("verify_ssh_infilename")
        except Exception as e:
            output.toast(f"{e}", color=RED)
            return

        support_format = pin.pin["verify_ssh_format"]
        
        core = CoreWithEnvironment()

        private_key_file = pin.pin["verify_ssh_private_key_file"]
        auth_id = pin.pin["verify_ssh_auth_id"]
        private_key_password = bytes(pin.pin["verify_ssh_private_key_password"], "utf8")

        try:
            if core.verify_ssh(infilename, private_key_file, private_key_password, auth_id, support_format, self._config_file):
                output.toast("Your file is OK", color=BLUE)
            else:
                output.toast("Your file is KO", color=ORANGE)
        except Exception as e:
            output.toast(f"failed to verify ({e})", color=RED)
            return

    def help_password(self):
        output.popup(HELP_TITLE, HELP_TEXT)

    def help_ssh(self):
        output.popup(HELP_TITLE, HELP_TEXT)

    def create_password(self):
        return output.put_column([
            pin.put_input("verify_password_infilename", help_text="Enter the input file path here", label="Input encrypted file"), 
            pin.put_input("verify_password_password", "password", help_text="Enter your password here", label="Master Password"),
            output.put_text("Options"),
            pin.put_radio("verify_password_format", ["msgpack", "json"], value="msgpack"),
            output.put_row([
                output.put_button("Verify", onclick=self.do_password),
                output.put_button("Help", onclick=self.help_password),
            ])
        ])
    
    def create_ssh(self):
        return output.put_column([
            pin.put_input("verify_ssh_infilename", help_text="Enter the input file path here", label="Input encrypted file"), 
            pin.put_input("verify_ssh_private_key_file", placeholder=".ssh/id_ssh", label="Private key file"),
            pin.put_input("verify_ssh_private_key_password", "password", help_text="Enter your private key password here", label="Private key password"),
            pin.put_input("verify_ssh_auth_id", help_text="Enter your auth_id here", label="Auth ID"), 
            output.put_text("Options"),
            pin.put_radio("verify_ssh_format", ["msgpack", "json"], value="msgpack"),
            output.put_row([
                output.put_button("Verify", onclick=self.do_ssh),
                output.put_button("Help", onclick=self.help_ssh),
            ])
        ])

    def create(self):
        return output.put_tabs([
                {'title': 'SSH', 'content': self.create_ssh()},
                {'title': 'Password', 'content': self.create_password()}
             ])