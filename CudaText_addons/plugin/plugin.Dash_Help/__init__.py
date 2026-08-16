import os
import subprocess
import platform
from urllib.parse import quote
from cudatext import *
from .word_proc import *
from .dash_data import *

class Command:

    def run_syntax_foreground(self):
   
        self._run(True, False)

    def run_nosyntax_foreground(self):
    
        self._run(False, False)

    def run_syntax_background(self):
    
        self._run(True, True)

    def run_nosyntax_background(self):
    
        self._run(False, True)

    def _run(self, syntax_sensitive, run_in_background):

        if ed.get_sel_mode() != SEL_NORMAL:
            msg_status('[Dash Help] Can use only normal selection')
            return

        query = ed.get_text_sel()
        if not query:
            query = get_word()
    
        lexer = ed.get_prop(PROP_LEXER_CARET)
        if not lexer:
            msg_status('[Dash Help] Need lexer in file')
            return

        keys = []            
        if syntax_sensitive:
            keys = DASH_KEYS.get(lexer, None)
            if not keys:
                msg_status('[Dash Help] Lexer "%s" is unknown to Dash'%lexer)
                return

        background_string = '&prevent_activation=true' if run_in_background else ''

        if platform.system() == 'Windows':
            # sending keys=<nothing> confuses some Windows doc viewers
            if keys:
                # ampersand must be escaped and ^ is the Windows shell escape char
                url = 'dash-plugin://keys=%s^&query=%s%s' % (','.join(keys), quote(query), background_string)
            else:
                url = 'dash-plugin://query=%s%s' % (quote(query), background_string)
            subprocess.call(['start', url], shell=True)
        elif platform.system() == 'Linux':
            subprocess.call(['/usr/bin/xdg-open',
                         'dash-plugin:keys=%s&query=%s%s' % (','.join(keys), quote(query), background_string)])
        else:
            subprocess.call(['/usr/bin/open', '-g',
                         'dash-plugin://keys=%s&query=%s%s' % (','.join(keys), quote(query), background_string)])
        
        msg_status('[Dash Help] Called search')
        print('Dash: query "%s", keys %s'% (query, str(keys)))
        