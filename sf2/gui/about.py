from pywebio import *

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

class About:
    def __init__(self) -> None:
        pass

    def create(self):
        return output.put_column([
            output.put_markdown(ABOUT)
        ])