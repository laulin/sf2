

from pywebio import *

from sf2.gui.tools import *
from sf2.core_with_environment import CoreWithEnvironment

HELP_ADD_TITLE = "Help"
HELP_ADD_TEXT = """
This is the help
"""


class SSH:
    def __init__(self, configFile:str) -> None:
        self._config_file = configFile
        
    def do_add(self):
        try:
            infilename = check_input_file("ssh_add_filename")
        except Exception as e:
            output.toast(f"{e}", color=RED)
            return
        
        if len(pin.pin["ssh_add_master_password"]) == 0:
            output.toast("Empty password is not allowed", color=RED)
            return
            
        support_format = pin.pin["ssh_add_format"]
        
        core = CoreWithEnvironment()
        password = pin.pin["ssh_add_master_password"]
        public_key_file = pin.pin["ssh_add_public_key_file"]
        auth_id = pin.pin["ssh_add_auth_id"]
        try:
            core.ssh_add(infilename, password, public_key_file, auth_id, support_format)
        except Exception as e:
            output.toast(f"failed to add ssh public key ({e})", color=RED)
            return

        output.toast("Your public key was added", color=BLUE)

    def do_rm(self):
        try:
            infilename = check_input_file("ssh_rm_filename")
        except Exception as e:
            output.toast(f"{e}", color=RED)
            return
            
        support_format = pin.pin["ssh_rm_format"]
        
        core = CoreWithEnvironment()
        auth_id = pin.pin["ssh_rm_auth_id"]
        try:
            core.ssh_rm(infilename, auth_id, support_format, self._config_file)
        except Exception as e:
            output.toast(f"failed to add ssh public key ({e})", color=RED)
            return

        output.toast("Your public key was remove", color=BLUE)

    def do_ls(self):
        try:
            infilename = check_input_file("ssh_ls_filename")
        except Exception as e:
            output.toast(f"{e}", color=RED)
            return
            
        support_format = pin.pin["ssh_ls_format"]
        
        core = CoreWithEnvironment()
        try:
            results = core.ssh_ls(infilename, support_format)
            print(results)
            output.clear("ssh_ls")

            with output.use_scope("ssh_ls"):
                self._create_ls()
                if len(results) == 0:
                    output.put_text("No key available")
                else:
                    tmp = []
                    for auth_id, key in results:
                        tmp.append(f"* {auth_id} : {key}")
                    output.put_markdown("\n".join(tmp))
            output.scroll_to("ssh_ls", "bottom")
        except Exception as e:
            output.toast(f"failed to add ssh public key ({e})", color=RED)
            return

        output.toast("Done", color=BLUE)

    def help_add(self):
        output.popup(HELP_ADD_TITLE, HELP_ADD_TEXT)

    def help_rm(self):
        output.popup(HELP_ADD_TITLE, HELP_ADD_TEXT)

    def help_ls(self):
        output.popup(HELP_ADD_TITLE, HELP_ADD_TEXT)

    
    def create_add(self):
        return output.put_column([
            pin.put_input("ssh_add_filename", help_text="Enter the entr file path here", label="Input encrypted file"), 
            pin.put_input("ssh_add_master_password", "password", help_text="Enter the master password here", label="Master Password"),
            pin.put_input("ssh_add_public_key_file", help_text="Enter your public key file here", label="Public key file"),
            pin.put_input("ssh_add_auth_id", help_text="Enter your auth_id here", label="Auth ID"), 
            output.put_text("Options"),
            pin.put_radio("ssh_add_format", ["msgpack", "json"], value="msgpack"),

            output.put_row([
                output.put_button("Add", onclick=self.do_add),
                output.put_button("Help", onclick=self.help_add),
            ])
        ])
    
    def create_rm(self):
        return output.put_column([
            pin.put_input("ssh_rm_filename", help_text="Enter the entr file path here", label="Input encrypted file"), 
            pin.put_input("ssh_rm_auth_id", help_text="Enter your auth_id here", label="Auth ID"), 
            output.put_text("Options"),
            pin.put_radio("ssh_rm_format", ["msgpack", "json"], value="msgpack"),

            output.put_row([
                output.put_button("Remove", onclick=self.do_rm),
                output.put_button("Help", onclick=self.help_rm),
            ])
        ])
    
    def create_ls(self):
        tmp = self._create_ls()

        return output.put_scope("ssh_ls", tmp)
    
    def _create_ls(self):
        tmp = output.put_column([
            pin.put_input("ssh_ls_filename", help_text="Enter the entr file path here", label="Input encrypted file"), 
            output.put_text("Options"),
            pin.put_radio("ssh_ls_format", ["msgpack", "json"], value="msgpack"),

            output.put_row([
                output.put_button("List", onclick=self.do_ls),
                output.put_button("Help", onclick=self.help_ls),
            ])

        ])

        return tmp

    def create(self):
        return output.put_tabs([
                {'title': 'Add', 'content': self.create_add()},
                {'title': 'Remove', 'content': self.create_rm()},
                {'title': 'List', 'content': self.create_ls()},
                
             ])
    # {'title': 'Remove', 'content': self.create_remove()},
    # {'title': 'List', 'content': self.create_list()}