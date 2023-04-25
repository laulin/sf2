

from pywebio import *

from sf2.gui.tools import *
from sf2.core_with_environment import CoreWithEnvironment

HELP_TITLE = "Verify Function"
HELP_TEXT = """
# Verify Function - User Manual

The "Verify" function in our cryptographic software allows you to check whether it is possible to decrypt an existing encrypted file using the provided cryptographic elements (password or RSA private key). This feature supports both password-based verification (Password tab) and RSA key-based verification (SSH tab). This page will guide you through the process of verifying the decryptability of an encrypted file using either a password or an RSA key.

## Password Tab

To verify the decryptability of an encrypted file using a password, follow these steps:

1. Enter the encrypted file's name in the "Encrypted File" field.
2. Input the password in the "Password" field. This password must be the same as the one used to encrypt the file.

Once you have filled in the required information, click the "Verify" button to proceed. The software will check whether the provided password is correct and display the result.

## SSH Tab

To verify the decryptability of an encrypted file using an RSA private key, follow these steps:

1. Enter the encrypted file's name in the "Encrypted File" field.
2. In the "Private Key File" field, define the path to your RSA private key.
3. (Optional) If your private key is protected with a password, enter it in the "Private Key Password" field.
4. Provide the "Auth ID" associated with your private key in the "Auth ID" field.

Once you have filled in the required information, click the "Verify" button to proceed. The software will check whether the provided RSA private key can decrypt the encrypted file and display the result.

By following the instructions provided in this user manual, you can verify the decryptability of encrypted files, ensuring that you can access your sensitive data when required with the correct cryptographic elements.
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