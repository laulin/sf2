import multiprocessing
from functools import partial


from pywebio import *
import webview

from sf2.gui.new import New
from sf2.gui.about import About
from sf2.gui.encrypt import Encrypt
from sf2.gui.decrypt import Decrypt
from sf2.gui.ssh import SSH
from sf2.gui.verify import Verify
from sf2.gui.convert import Convert
from sf2.gui.open import Open

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

MANUAL = """
# SF2 User Manual

Simple Fernet File (SF2) is a cryptographic software designed to protect and manage sensitive data in a secure and efficient manner. SF2 offers two main methods for encryption and decryption: using a password or using asymmetric key pairs (RSA).

This cryptographic software designed to protect your sensitive data while allowing seamless collaboration between team members or different entities without sharing a secret. This user manual will provide an overview of the software's functionalities and guide you through its various features.

SF2 utilizes a "Password" for administrative access to encrypted files. This password can be used alone to access the files, but it is not recommended. Instead, SF2 supports the addition of RSA public keys in the SSH format, allowing secure access to files associated with machines/accounts/users. This cryptographic approach enables secure exchange and interaction with files, ensuring data confidentiality and integrity.

The software is available in both graphical and command-line versions, accommodating different user preferences and environments (non-graphical and scripting purposes).

## Password vs. Asymmetric Key Pairs

### Password

Using a password for encryption is a simpler approach, as it only requires a single secret key that is shared between the sender and the recipient. However, this approach has its downsides. If multiple parties need access to the encrypted data, the password must be shared among all of them, which can increase the risk of unauthorized access.

### Asymmetric Key Pairs (RSA)

Asymmetric key pairs consist of a private key and a public key. The private key is kept secret by its owner, while the public key can be freely shared with others. Data encrypted with a public key can only be decrypted by the corresponding private key. This approach eliminates the need to share a secret password among multiple parties, as each user can have their own unique key pair.

SF2 leverages the advantages of using asymmetric key pairs by allowing users to manage public keys and their associated "Auth ID" in encrypted files. This enables secure collaboration and data sharing without the need to share a secret password.

## Features

SF2 offers several features that help users manage and protect their sensitive data:

1. **Open**: Open and edit encrypted files without storing the plaintext content on the hard drive.
2. **New**: Create a new encrypted file with a password.
3. **Encrypt**: Encrypt a plaintext file using a password.
4. **Decrypt**: Decrypt an encrypted file using a password or an RSA private key.
5. **Verify**: Verify the decryptability of an encrypted file using a password or an RSA private key.
6. **Convert**: Convert encrypted files from SF2 v1.xx to SF2 v2.xx format.
7. **SSH**: Manage public keys and their associated "Auth ID" in encrypted files.


SF2 is a powerful cryptographic software that emphasizes secure collaboration and data protection. By utilizing both password-based and asymmetric key-based encryption methods, SF2 provides users with a flexible and secure solution for managing sensitive information.
"""

def root(config_file:str):
    new = New(config_file)
    about = About(config_file)
    encrypt = Encrypt(config_file)
    decrypt = Decrypt(config_file)
    ssh = SSH(config_file)
    verify = Verify(config_file)
    convert = Convert(config_file)
    open = Open(config_file)

    output.put_text(HEADER)
    output.put_tabs([
        {'title': 'Open', 'content': open.create()},
        {'title': 'New', 'content': new.create()},
        {'title': 'Encrypt', 'content': encrypt.create()},
        {'title': 'Decrypt', 'content': decrypt.create()},
        {'title': 'Verify', 'content': verify.create()},
        {'title': 'Convert', 'content': convert.create()},
        {'title': 'SSH', 'content': ssh.create()},
        {'title': 'About', 'content': about.create()},
        {'title': 'Manual', 'content': output.put_markdown(MANUAL)}
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