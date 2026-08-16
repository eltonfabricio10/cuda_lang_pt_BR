import os
from cudatext import *

class Command:
    
    def on_open_pre(self, ed_self, filename):
        ext = os.path.basename(filename).split('.')[-1].lower()
        if ext in ('jpg', 'jpeg', 'png', 'bmp', 'ico'):
            print('Ignoring picture:', filename)
            file_open(filename, options='/view-hex')
            return False
            
