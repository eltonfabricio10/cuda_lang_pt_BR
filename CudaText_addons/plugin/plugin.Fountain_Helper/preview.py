import os
import tempfile
import webbrowser
from cudatext import *
from cudax_nodejs import run_node

fn_script = os.path.join(os.path.dirname(__file__), 'preview.js')

def do_preview():

    fn_ed = ed.get_filename()
    if not fn_ed or ed.get_prop(PROP_MODIFIED):
        msg_status('First, save the current document')
        return

    text = run_node('', [fn_script, fn_ed])
    if not text:
        msg_status('Could not convert document to HTML')
        return

    fn = tempfile.gettempdir()+os.sep+'Preview '+os.path.basename(fn_ed)+'.html'
    if os.path.isfile(fn):
        os.remove(fn)

    with open(fn, 'w') as f:
        f.write(text)

    webbrowser.open_new_tab('file://'+fn)
    msg_status('Opened browser')
