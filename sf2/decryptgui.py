import os
import dearpygui.dearpygui as dpg
from sf2.cipher import Cipher

class DecryptGUI:
    def __init__(self, parent:object) -> None:
        self._parent = parent
        self._cipher = Cipher()

    def create(self):
        self._parent.disable_menu()

        with dpg.window(label="Decrypt", tag="decrypt_window", width=500, height=400, pos=(70, 40), show=True, on_close=self.on_close):
            with dpg.group(horizontal=True):
                dpg.add_button(label="Encrypted File", callback=self.on_call_source_dial)
                dpg.add_input_text(tag="source_file", label="", width=-1)
                
            with dpg.group(horizontal=True):
                dpg.add_button(label="Plaintext File", callback=self.on_call_destination_dial)
                dpg.add_input_text(tag="destination_file", label="", width=-1)

            with dpg.group(horizontal=True):
                dpg.add_text("Password")
                dpg.add_input_text(tag="password", label="", password=True, width=-1)
                with dpg.tooltip("password"):
                    dpg.add_text("Recommanded : 12 chars, with a-z, A-Z, 0-9 and special chars")

            dpg.add_button(label="Decrypt !", tag="do_decrypt", callback=self.on_decrypt, width=-1)
            dpg.add_text("", tag="help")

        with dpg.file_dialog(directory_selector=False, show=False, callback=self.on_return_source_dial, file_count=1, id="decrypt_source_file_dialog_id", width=400, height=400, modal=True):
            dpg.add_file_extension(".x", color=(0, 255, 0, 255), custom_text="[SF2]")

        with dpg.file_dialog(directory_selector=False, show=False, callback=self.on_return_destination_dial, file_count=1, id="decrypt_destination_file_dialog_id", width=400, height=400, modal=True):
            dpg.add_file_extension(".*")
            dpg.add_file_extension("", color=(150, 255, 150, 255))
            dpg.add_file_extension(".md", color=(0, 255, 0, 255), custom_text="[Markdown]")
            dpg.add_file_extension(".txt", color=(0, 128, 128, 255), custom_text="[Text]")

    def on_close(self):
        # called when the user closes the windows
        dpg.delete_item("decrypt_window")
        dpg.delete_item("decrypt_source_file_dialog_id")
        dpg.delete_item("decrypt_destination_file_dialog_id")
        self._parent.enable_menu()

    def on_call_source_dial(self):
        # called everytime Source File is clicked
        dpg.show_item("decrypt_source_file_dialog_id")

    def on_call_destination_dial(self):
        # called everytime Destination File is clicked
        dpg.show_item("decrypt_destination_file_dialog_id")

    def on_return_source_dial(self, sender, app_data, user_data):
        # Called by source file dialog, set related input field
        selections = app_data["selections"]
        filename = selections[list(selections.keys())[0]] # return the single file name
        dpg.set_value("source_file", filename)
        dpg.hide_item("decrypt_source_file_dialog_id")

    def on_return_destination_dial(self, sender, app_data, user_data):
        # Called by destination file dialog, set related input field
        selections = app_data["selections"]
        filename = selections[list(selections.keys())[0]] # return the single file name
        dpg.set_value("destination_file", filename)
        dpg.hide_item("decrypt_destination_file_dialog_id")


    def on_decrypt(self):
        # called by used to start encryption
        dpg.set_value("help", "") # reset the help line

        # get and check source/destination path
        source_file = dpg.get_value("source_file")
        destination_file = dpg.get_value("destination_file")

        if not os.path.exists(source_file):
            dpg.bind_item_theme("source_file", "input_error_theme")
            dpg.set_value("help", "The source file is invalid")
            return
        else:
            dpg.bind_item_theme("source_file", "input_ok_theme")

        if not destination_file:
            dpg.bind_item_theme("destination_file", "input_error_theme")
            dpg.set_value("help", "The destination file is empty")
            return
        else:
            dpg.bind_item_theme("destination_file", "input_ok_theme")

        # get passwords and check them
        password = dpg.get_value("password")

        if not self._cipher.verify_file(password, source_file):
            dpg.bind_item_theme("password", "input_error_theme")
            dpg.set_value("help", "Password is not the good one ...")
            return
        else:
            dpg.bind_item_theme("password", "input_ok_theme")

        # Let's do the encryption
        try:
            # if it success, highlight le button with green border
            self._cipher.decrypt_file(password, source_file, destination_file)
            dpg.bind_item_theme("do_decrypt", "input_success_theme")
            source = os.path.split(source_file)[1]
            destination = os.path.split(destination_file)[1]
            dpg.set_value("help", f"Success ! {source} was decrypted to {destination}")
        except Exception as e:
            dpg.set_value("help", f"Something failed : {e}")
            dpg.bind_item_theme("do_decrypt", "input_error_theme")