import multiprocessing
from functools import partial


from pywebio import *
import webview

from sf2.gui.new import New
from sf2.gui.about import About
from sf2.gui.encrypt import Encrypt
from sf2.gui.decrypt import Decrypt
from sf2.gui.ssh import SSH

HEADER = """
   _____ _________ 
  / ___// ____/__ \\
  \__ \/ /_   __/ /
 ___/ / __/  / __/ 
/____/_/    /____/ V2
"""


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

def root(config_file:str):
    new = New(config_file)
    about = About(config_file)
    encrypt = Encrypt(config_file)
    decrypt = Decrypt(config_file)
    ssh = SSH(config_file)
    output.put_text(HEADER)
    output.put_tabs([
        {'title': 'new', 'content': new.create()},
        {'title': 'encrypt', 'content': encrypt.create()},
        {'title': 'decrypt', 'content': decrypt.create()},
        {'title': 'verify', 'content': 'Hello world'},
        {'title': 'convert', 'content': 'Hello world'},
        {'title': 'ssh', 'content': ssh.create()},
        {'title': 'About', 'content': about.create()}
    ])

@config(theme="dark", js_code=FOOTER_REMOVER)
def main(config_file:str):
    root(config_file)
    

def run_app(port=8888, config_file:str=None):
    main_thread = partial(main, config_file)
    t = multiprocessing.Process(target=start_server, kwargs={"applications":main_thread, "port":port, "debug":True, "host":"127.0.0.1"}, daemon=True)
    t.start()

    webview.create_window('SF2', f'http://127.0.0.1:{port}', height=1000)
    webview.start()


def run_server(host:str="127.0.0.1", port:int=8888):
    start_server(applications=main, port=port, host=host)

if __name__ == '__main__':
   
    run_app()