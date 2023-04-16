import multiprocessing
import os.path
from pathlib import Path

from pywebio import *
import webview

from sf2.openinram import OpenInRAM
from sf2.file_object import FileObject
from sf2.ssh_file_object import SSHFileObject
from sf2.configuration import Configuration

from sf2.container_ssh import ContainerSSH
from sf2.container_base import ContainerBase
from sf2.json_support import JsonSupport
from sf2.msgpack_support import MsgpackSupport

HEADER = """
   _____ _________ 
  / ___// ____/__ \\
  \__ \/ /_   __/ /
 ___/ / __/  / __/ 
/____/_/    /____/ V2
"""

RED = '#ff2121'
ORANGE = '#ff8821'
BLUE = '#2188ff'

FOOTER_REMOVER = """
// remove the footer
document.addEventListener('DOMContentLoaded', () => {
// Sélectionnez l'élément footer en utilisant la balise, l'ID ou la classe
const footerElement = document.querySelector('footer');

// Masquez l'élément footer en modifiant le style CSS s'il existe
if (footerElement) {
    footerElement.style.display = 'none';
}
});
"""

ABOUT = """# SF2
Version 2.0.0,
By Laulin

__Special thanks to:__
* [Spartan Conseil](https://spartan-conseil.fr) for giving me time and money, which allows me to give you a free software

__Thanks to:__
* [Cryptography](https://cryptography.io/en/latest/)
* [PyWebIO](https://www.pyweb.io/) (Thank you for making GUI so easy !!!)
* [Webview](https://pywebview.flowrl.com/)
* [Msgpack](https://msgpack.org/) (what a greatful format)
* [Inotify](https://pypi.org/project/inotify/)"""

def get_format(support_format:str, filename:str):
    if support_format == "json":
        return JsonSupport(filename)
    elif support_format == "msgpack":
        return MsgpackSupport(filename)

def do_new():

    if len(pin.pin["new_password"]) == 0:
        output.toast("Empty password is not allowed", color=RED)
        return

    if pin.pin["new_password"] != pin.pin["new_password_check"]:
        output.toast("Password are incorrect", color=RED)
        return
    password = pin.pin["new_password"]
    
    try:
        Path(pin.pin["new_filename"]).resolve()
    except (OSError, RuntimeError):
        output.toast("File path is invalid", color=RED)
    filename = pin.pin["new_filename"]

    force = pin.pin["new_force"] == ["allow overwrite ?"]
    support_format = pin.pin["new_format"]

    if support_format is None:
        output.toast("Please select a format", color=ORANGE)
        return

    support = get_format(support_format, filename)
    container = ContainerBase(support)
    try:
        container.create(password, force)
    except Exception as e:
        output.toast(f"Ooops : {e}", color=RED)
        return
    
    container.write(b"", password)

    output.toast("Your file was created", color=BLUE)

def new():
    return output.put_column([
        pin.put_input("new_filename", help_text="Enter the file path here"), 
        pin.put_input("new_password", "password", help_text="Enter your password here"),
        pin.put_input("new_password_check", "password", help_text="Enter your password here, again"),
        output.put_row([
            pin.put_checkbox("new_force",options=["allow overwrite ?"]),
            pin.put_radio("new_format", ["msgpack", "json"])
        ]),

        output.put_button("Create", onclick=do_new),
    ])

def about():
    return output.put_column([
        output.put_markdown(ABOUT)
    ])

def root():
    output.put_text(HEADER)
    output.put_tabs([
        {'title': 'new', 'content': new()},
        {'title': 'encrypt', 'content': 'Hello world'},
        {'title': 'decrypt', 'content': 'Hello world'},
        {'title': 'verify', 'content': 'Hello world'},
        {'title': 'convert', 'content': 'Hello world'},
        {'title': 'ssh', 'content': output.put_tabs([
            {'title': 'add', 'content': 'Hello world'},
            {'title': 'rm', 'content': 'Hello world'},
            {'title': 'ls', 'content': 'Hello world'}])
         
        },
        {'title': 'convert', 'content': 'Hello world'},
        {'title': 'About', 'content': about()}
    ])

@config(theme="dark", js_code=FOOTER_REMOVER)
def main():
    root()
    

def run_app(port=8888):
    t = multiprocessing.Process(target=start_server, kwargs={"applications":main, "port":8888, "debug":True, "host":"127.0.0.1"}, daemon=True)
    t.start()

    webview.create_window('SF2', f'http://127.0.0.1:{port}', height=1000)
    webview.start()


def run_server(host:str="127.0.0.1", port:int=8888):
    start_server(applications=main, port=port, host=host)

if __name__ == '__main__':
   
    run_app()