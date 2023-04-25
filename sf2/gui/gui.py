import multiprocessing


from pywebio import *
import webview

from sf2.gui.new import New
from sf2.gui.about import About
from sf2.gui.encrypt import Encrypt
from sf2.gui.decrypt import Decrypt

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

def root():
    new = New()
    about = About()
    encrypt = Encrypt()
    decrypt = Decrypt()
    output.put_text(HEADER)
    output.put_tabs([
        {'title': 'new', 'content': new.create()},
        {'title': 'encrypt', 'content': encrypt.create()},
        {'title': 'decrypt', 'content': decrypt.create()},
        {'title': 'verify', 'content': 'Hello world'},
        {'title': 'convert', 'content': 'Hello world'},
        {'title': 'ssh', 'content': output.put_tabs([
            {'title': 'add', 'content': 'Hello world'},
            {'title': 'rm', 'content': 'Hello world'},
            {'title': 'ls', 'content': 'Hello world'}])
         
        },
        {'title': 'convert', 'content': 'Hello world'},
        {'title': 'About', 'content': about.create()}
    ])

#@config(theme="dark", js_code=FOOTER_REMOVER)
@config(theme="dark")
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