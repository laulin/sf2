import dearpygui.dearpygui as dpg

from sf2.cipher import Cipher

KEY_CTRL = 341
KEY_C = 83
KEY_ALL = -1

class Editor:
    def __init__(self, password:str, filename:str) -> None:
        self._password = password
        self._filename = filename

        self._last_saved = None
        self._data = None

    def load(self):
        with open(self._filename) as f:
            container = f.read()
        cipher = Cipher()
        self._data = cipher.decrypt(self._password, container)
        self._last_saved = self._data

    def _create_menu(self)->None:
        with dpg.viewport_menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Save (ctrl+s)", callback=self.save)
                dpg.add_menu_item(label="Quit", callback=self.on_close)

    def create(self):
        dpg.create_context()
        dpg.configure_app(init_file=self._filename+".ini")

        with dpg.window(tag=self._filename, on_close=self.on_close, width=600, height=400):
            self._create_menu()
            dpg.add_input_text(default_value=self._data, multiline=True, readonly=False, tag="text", pos=(5,20), width=-1, height=-1, tab_input=True)
            

            with dpg.handler_registry():
                dpg.add_key_press_handler(key=KEY_CTRL, callback=self.on_key_ctrl)

        with dpg.window(label="Save changes ?", modal=True, show=True, tag="modal_id", no_title_bar=True):
            dpg.add_text("Your document's changed is not save\nDo you want to save ?")
            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_button(label="Yes", width=75, callback=self.save_and_close)
                dpg.add_button(label="No", width=75, callback=self.save_and_discard)

        dpg.create_viewport(title='SF2', width=600, height=400,)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_exit_callback(self.on_exit)
        dpg.start_dearpygui()
        dpg.destroy_context()

    def save(self):
        self._data = dpg.get_value("text")
        cipher = Cipher()
        container = cipher.encrypt(self._password, self._data)
        with open(self._filename, "w") as f:
            f.write(container)

        self._last_saved = self._data

    def on_key_ctrl(self, sender, app_data):
        if dpg.is_key_down(KEY_C):
            self.save()

    def on_close(self):
        self._data = dpg.get_value("text")
        if self._data != self._last_saved:
            dpg.configure_item("modal_id", show=True)
        else:
            dpg.stop_dearpygui()

    def save_and_close(self):
        self.save()
        dpg.stop_dearpygui()

    def save_and_discard(self):
        dpg.stop_dearpygui()

    def on_exit(self):
        dpg.save_init_file(self._filename+".ini")