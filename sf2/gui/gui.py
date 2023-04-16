from pywebio import *
import multiprocessing
import webview

HEADER = """
   _____ _________ 
  / ___// ____/__ \\
  \__ \/ /_   __/ /
 ___/ / __/  / __/ 
/____/_/    /____/ V2
"""

@config(theme="dark")
def main():
    
    output.put_text(HEADER)
    output.put_tabs([
        {'title': 'new', 'content': 'Hello world'},
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
        {'title': 'About', 'content': 'Hello world'}
    ])

def run_app(port=8888):
    t = multiprocessing.Process(target=start_server, kwargs={"applications":main, "port":8888, "debug":True, "host":"127.0.0.1"}, daemon=True)
    t.start()

    webview.create_window('SF2', f'http://127.0.0.1:{port}')
    webview.start()


def run_server(host:str="127.0.0.1", port:int=8888):
    start_server(applications=main, port=port, host=host)

if __name__ == '__main__':
   
    run_app()