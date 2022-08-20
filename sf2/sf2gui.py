import os
import dearpygui.dearpygui as dpg

from sf2.encryptgui import EncryptGUI
from sf2.decryptgui import DecryptGUI
from sf2.editgui import EditGUI

class SF2GUI:
    def __init__(self) -> None:
        self._encrypt_app = EncryptGUI(self)
        self._decrypt_app = DecryptGUI(self)
        self._edit_app = EditGUI(self)

    def create_themes(self):
        # create all themes uses by application

        # hightlight an error in a field
        with dpg.theme(tag="input_error_theme"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Border, [255, 0, 0], category=dpg.mvThemeCat_Core)

        # normal case for input
        with dpg.theme(tag="input_ok_theme"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0, category=dpg.mvThemeCat_Core)

        # hightlight an success in a field
        with dpg.theme(tag="input_success_theme"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Border, [0, 255, 0], category=dpg.mvThemeCat_Core)

    def create(self):

        dpg.create_context()

        self.create_themes()

        dpg.create_viewport(title='SF2', width=1024, height=768)

        def print_me(sender, app_data, user_data):
            print(sender, app_data, user_data)

        with dpg.viewport_menu_bar(tag="viewport_menu_bar"):
            dpg.add_menu_item(label="Encrypt", tag="encrypt_menu", callback=self._encrypt_app.create)
            dpg.add_menu_item(label="Decrypt", tag="decrypt_menu", callback=self._decrypt_app.create)
            dpg.add_menu_item(label="Edit", tag="edit_menu", callback=self._edit_app.create)
            dpg.add_menu_item(label="Verify", callback=print_me)
            dpg.add_menu_item(label="About", callback=print_me)
            dpg.add_menu_item(label="Style", callback=dpg.show_style_editor)

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_viewport_clear_color([4,12,52])
        dpg.start_dearpygui()
        dpg.destroy_context()

    def disable_menu(self):
        dpg.disable_item("encrypt_menu")
        dpg.disable_item("decrypt_menu")
        dpg.disable_item("edit_menu")

    def enable_menu(self):
        dpg.enable_item("encrypt_menu")
        dpg.enable_item("decrypt_menu")
        dpg.enable_item("edit_menu")


def main():
    gui = SF2GUI()
    gui.create()



if __name__ == "__main__":
    main()