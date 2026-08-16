import os
import tempfile
from cudatext import *

from cudax_lib import get_translation, safe_open_url
_ = get_translation(__file__)

import re
import string
import locale

plug_path = os.path.dirname(os.path.abspath(__file__))
plug_name = os.path.basename(plug_path)
dir_temp = os.path.join(tempfile.gettempdir(), plug_name)
fn_config = os.path.join(app_path(APP_DIR_SETTINGS), 'plugins.ini')
ini_section = plug_name.replace('cuda_', '')
locales = ['en']

class TplReplace(string.Template):
    delimiter = '{{'
    pattern = r'''
    \{\{(?:
    (?P<escaped>\{\{) |
    (?P<named>[_a-z][_a-z0-9]*)\}\} |
    (?P<invalid>)
    )
    '''

class Command:
    opts_def = dict(
        file_exts = 'ttf,woff,eot,otf,ttc',
        tpl_fn = 'template.html',
        ft = 'abcdefghijklmnopqrstuvwxyz|ABCDEFGHIJKLMNOPQRSTUVWXYZ|The quick brown fox jumps over the lazy dog.',
        ft_loc = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя|АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ|Съешь же ещё этих мягких французских булок, да выпей чаю.',
    )

    def __init__(self):
        self.opts = self.load_opts()
        if not os.path.isdir(dir_temp):
            os.mkdir(dir_temp)

    def on_open_pre(self, ed_self, fn):
        file_ext = self.get_fn_fe(fn)[1]
        if file_ext in self.opts['file_exts'].split(','):
            self.run(fn)
            return False

    def on_exit(self, ed_self):
        if os.path.isdir(dir_temp):
            for f in os.listdir(dir_temp):
                os.remove(os.path.join(dir_temp, f))
        os.rmdir(dir_temp)

    def get_locales(self):
        loc = locale.getlocale()[0].split('_')[0]
        if loc not in locales:
            locales.append(loc)

        return locales

    def get_fts(self):
        locales_ = self.get_locales()
        fts = dict()
        for loc in locales_:
            fts[loc] = self.opts['ft'] if loc == locales[0] else self.opts['ft_loc']

        return fts

    def load_opts(self):
        data = dict()
        for key in self.opts_def:
            data[key] = ini_read(fn_config, ini_section, key, self.opts_def[key])

        return data

    def save_opts(self):
        for key in self.opts:
            if len(self.get_locales()) == 1 and key == 'ft_loc':
                continue
            ini_write(fn_config, ini_section, key, self.opts[key])

    def config(self):
        self.save_opts()
        file_open(fn_config)
        lines = [ed.get_text_line(i) for i in range(ed.get_line_count())]
        try:
            index = lines.index('[' + ini_section + ']')
            ed.set_caret(0, index)
        except:
            pass

    def get_fn_fe(self, fn):
        fn = os.path.basename(fn)
        fe = os.path.splitext(fn)[1][1:].lower()
        fn_only = os.path.splitext(os.path.basename(fn))[0]
        return fn, fe, fn_only

    def gen_html(self, fn, loc, ft):
        tpl = plug_path + os.sep + self.opts['tpl_fn']
        if os.path.isfile(tpl):
            with open(tpl, 'r', encoding='utf-8') as f:
                text = f.read()
            ft_parts = ft.split('|')
            text = TplReplace(text).safe_substitute(
                font_title = self.get_fn_fe(fn)[0],
                font_name = self.get_fn_fe(fn)[2],
                font_file = fn,
                fish_text_1 = ft_parts[0],
                fish_text_2 = ft_parts[1],
                fish_text_3 = ft_parts[2]
            )

            fn_temp = os.path.join(dir_temp, os.path.basename(fn) + '_' + loc + '.html')
            with open(fn_temp, 'w', encoding='utf-8') as f:
                f.write(text)

            if os.path.isfile(fn_temp):
                msg_status(_('FontPreview: open file') + ' ' + fn_temp)
                safe_open_url('file://' + fn_temp)
            else:
                msg_status(_('FontPreview: cannot open file') + ' ' + fn_temp)
        else:
            msg_status(_('FontPreview: cannot open file') + ' ' + tpl)

    def run(self, fn):
        fts = self.get_fts()
        for loc, ft in fts.items():
            self.gen_html(fn, loc, ft)
