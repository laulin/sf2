import os
import dearpygui.dearpygui as dpg
from sf2.cipher import Cipher
from sf2.extern import Extern

class EditGUI:
    def __init__(self, parent:object) -> None:
        self._parent = parent
        self._cipher = Cipher()

    def set_source_file(self, path:str):
        dpg.set_value("source_file", path)

    def create(self):
        self._parent.disable_menu()

        with dpg.window(label="Edit", tag="edit_window", width=500, height=146, pos=(70, 40), show=True, on_close=self.on_close):
            with dpg.group(horizontal=True):
                dpg.add_button(label="Encrypted File", callback=self.on_call_source_dial)
                dpg.add_input_text(tag="source_file", label="", width=-1)
                
            with dpg.group(horizontal=True):
                dpg.add_text("Password")
                dpg.add_input_text(tag="password", label="", password=True, width=-1)

            with dpg.group(horizontal=True):
                dpg.add_text("Editor")
                dpg.add_input_text(default_value="mousepad", tag="editor", width=-1)

            dpg.add_button(label="Edit !", tag="do_edit", callback=self.on_edit, width=-1)
            dpg.add_text("", tag="help")

        with dpg.file_dialog(directory_selector=False, show=False, callback=self.on_return_source_dial, file_count=1, id="edit_source_file_dialog_id", width=400, height=400, modal=True):
            dpg.add_file_extension(".x", color=(0, 255, 0, 255), custom_text="[SF2]")

    def on_close(self):
        # called when the user closes the windows
        dpg.delete_item("edit_window")
        dpg.delete_item("edit_source_file_dialog_id")
        self._parent.enable_menu()

    def on_call_source_dial(self):
        # called everytime Source File is clicked
        dpg.show_item("edit_source_file_dialog_id")


    def on_return_source_dial(self, sender, app_data, user_data):
        # Called by source file dialog, set related input field
        selections = app_data["selections"]
        filename = selections[list(selections.keys())[0]] # return the single file name
        dpg.set_value("source_file", filename)
        dpg.hide_item("edit_source_file_dialog_id")


    def on_edit(self):
        # called by used to start encryption
        dpg.set_value("help", "") # reset the help line

        # get and check source path
        source_file = dpg.get_value("source_file")
        editor = dpg.get_value("editor")

        if not os.path.exists(source_file):
            dpg.bind_item_theme("source_file", "input_error_theme")
            dpg.set_value("help", "The source file is invalid")
            return
        else:
            dpg.bind_item_theme("source_file", "input_ok_theme")

        # get passwords and check them
        password = dpg.get_value("password")

        if not self._cipher.verify_file(password, source_file):
            dpg.bind_item_theme("password", "input_error_theme")
            dpg.set_value("help", "Password is not the good one ...")
            return
        else:
            dpg.bind_item_theme("password", "input_ok_theme")

        dpg.set_value("password", "")
        # Let's edit it
        editor = Extern(password, source_file, editor)
        editor.run()
