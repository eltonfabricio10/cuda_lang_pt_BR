import re
import webbrowser
from cudatext import *
from .word_proc import *

regex = re.compile(r'([a-z-]+)', re.I)
URL = 'http://caniuse.com/#search='

def do_info(text):
    m = regex.search(text)
    if m:
        text = m.group()
        webbrowser.open_new_tab(URL + text)
        return True

class Command:
    def run(self):
        text = ed.get_text_sel()
        if not text:
            x, y, nlen, text = get_word_info()
        if text and do_info(text):
            msg_status('Webbrowser opened with info about "%s"' % text)
        else:
            msg_status('No text selected')
