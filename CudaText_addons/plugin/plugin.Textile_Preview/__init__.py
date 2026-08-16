import sys
import os
import webbrowser
import tempfile
from cudatext import *

sys.path.append(os.path.dirname(__file__))
import textile

fn_temp = os.path.join(tempfile.gettempdir(), 'textile_preview.html')


class Command:
    def run(self):
        text = ed.get_text_all()
        if not text: return

        text = textile.textile(text)

        with open(fn_temp, 'w') as f:
            f.write(text)

        if os.path.isfile(fn_temp):
            msg_status('Opening HTML preview...')
            webbrowser.open_new_tab(fn_temp)
        else:
            msg_status('Cannot convert Textile to HTML')
