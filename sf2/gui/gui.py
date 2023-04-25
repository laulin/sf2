import multiprocessing
import os.path
from pathlib import Path

from pywebio import *
import webview

from sf2.gui.new import New

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

ABOUT = """# SF2
Version 2.0.0
Licence : MIT
By Laulin

__Special thanks to:__
* [Spartan Conseil](https://spartan-conseil.fr) for giving me time and money, which allows me to give you a free software

__Thanks to:__
* [Cryptography](https://cryptography.io/en/latest/)
* [PyWebIO](https://www.pyweb.io/) (Thank you for making GUI so easy !!!)
* [Webview](https://pywebview.flowrl.com/)
* [Msgpack](https://msgpack.org/) (what a greatful format)
* [Inotify](https://pypi.org/project/inotify/)"""



def about():
    return output.put_column([
        output.put_markdown(ABOUT)
    ])

def root():
    new = New()
    output.put_text(HEADER)
    output.put_tabs([
        {'title': 'new', 'content': new.create()},
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