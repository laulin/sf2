from pywebio import *

from sf2.gui.tools import *
from sf2.core_with_environment import CoreWithEnvironment

HELP_TITLE = "Password Function"
HELP_TEXT = """
# Password Function - User Manual

"""


class ChangePassword:
    def __init__(self, configFile:str) -> None:
        self._config_file = configFile
        
    def do(self):

        if len(pin.pin["change_password_old_password"]) == 0 or len(pin.pin["change_password_new_password"]) == 0:
            output.toast("Empty password is not allowed", color=RED)
            return

        if pin.pin["change_password_new_password"] != pin.pin["change_password_new_password_retry"]:
            output.toast("New password are incorrect", color=RED)
            return
        old_password = pin.pin["change_password_old_password"]
        new_password = pin.pin["change_password_new_password"]
              
        try:
            filename = check_input_file("change_password_filename")
        except Exception as e:
            output.toast(f"{e}", color=RED)
            return

        support_format = pin.pin["change_password_format"]
       
        core = CoreWithEnvironment()
        try:
            core.change_password(filename, old_password, new_password , support_format)
           
        except Exception as e:
            output.toast(f"Oups : {e}", color=RED)
            return

        output.toast("Your password was changed", color=BLUE)

    def help(self):
        output.popup(HELP_TITLE, HELP_TEXT)

    def create(self):
        return output.put_column([
            pin.put_input("change_password_filename", help_text="Enter the encrypted file path here", label="Encrypted file"), 
            pin.put_input("change_password_old_password", "password", help_text="Enter your old password here", label="Password"),
            pin.put_input("change_password_new_password", "password", help_text="Enter your new password here"),
            pin.put_input("change_password_new_password_retry", "password", help_text="Enter your new password here, again"),
            output.put_text("Options"),
            output.put_row([
                pin.put_radio("change_password_format", ["msgpack", "json"], value="msgpack")
            ]),
            output.put_row([
                output.put_button("Change password", onclick=self.do),
                output.put_button("Help", onclick=self.help),
            ]),
        ])