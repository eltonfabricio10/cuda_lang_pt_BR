import os
import shutil
import json
from cudatext import *

CFG_DEFAULT = os.path.join(os.path.dirname(__file__), 'def_config.json')
CFG_FILE = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_switch_header.json')
MAP = {}

if not os.path.exists(CFG_FILE):
    shutil.copyfile(CFG_DEFAULT, CFG_FILE)

def make_fn(fn0, fn1, ext):
    return os.path.join(os.path.dirname(fn0), fn1+'.'+ext)

class Command:

    def run(self):

        global MAP
        fn0 = ed.get_filename()
        if not fn0: 
            return msg_status('Need named file')
        fn1 = os.path.basename(fn0)
        n = fn1.rfind('.')
        if n<=0: 
            return msg_status('Need file with extension')
        ext1 = fn1[n+1:]
        fn1 = fn1[:n]
        
        fn2 = ''
        if ext1 in MAP.keys():
            ext2 = MAP[ext1]
            if type(ext2) is str:
                fn2 = make_fn(fn0, fn1, ext2)
            elif type(ext2) is list:
                for e in ext2:
                    fn2a = make_fn(fn0, fn1, e)
                    if os.path.isfile(fn2a):
                        fn2 = fn2a
                        break
        
        if os.path.isfile(fn2):
            file_open(fn2)
        else:
            msg_status('Cannot switch file: no pair file')


    def config(self):
        
        if os.path.exists(CFG_FILE):
            file_open(CFG_FILE)
        else:
            msg_status('Config file not found: '+CFG_FILE)


    def __init__(self):
    
        global MAP
        if os.path.exists(CFG_FILE):
            MAP = json.loads(open(CFG_FILE).read())
