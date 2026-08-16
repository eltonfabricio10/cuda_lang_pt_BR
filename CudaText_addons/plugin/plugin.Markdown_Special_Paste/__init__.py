import os
from cudatext import *
import cudatext_cmd as cmds
import requests
import html
from datetime import datetime

from cudax_lib import get_translation
_   = get_translation(__file__)  # i18n

fn_config = os.path.join(app_path(APP_DIR_SETTINGS), 'plugins.ini')
option_section = 'markdown_special_paste'
option_timeout = 5
option_pic_path = '{projdir}'
option_pic_name = '{now}'
option_pic_ext = 'png'
option_now = '%Y-%m-%d-%H-%M-%S'


FORMAT_URL = {
    'Markdown': '[{title}]({url})',
    'reStructuredText': '`{title} <{url}>`__',
    'MediaWiki': '[{url} {title}]',
    'AsciiDoc': '{url}[{title}]',
    'LaTeX': r'\href{{url}}{{title}}',
}

FORMAT_PIC = {
    'Markdown': '![alt text]({filename} "Title")',
    'reStructuredText': '\n.. image:: {filename}',
    'MediaWiki': '\n[[File:{filename}]]',
    'AsciiDoc': 'image:{filename}[title="Title"]',
    'LaTeX': r'\includegraphics[width=\linewidth]{{filename}}',
}

def resolve_pic_path(s):

    if os.sep!='/':
        s = s.replace('/', os.sep)

    def_val = os.path.dirname(ed.get_filename())

    if '{projdir}' in s:
        try:
            import cuda_project_man
            info = cuda_project_man.global_project_info
            #print(info)
            proj_dir = os.path.dirname(info.get('filename', ''))
            if proj_dir:
                s = s.replace('{projdir}', proj_dir)
            else:
                s = def_val
        except:
            print('ERROR: '+_('Cannot import Project Manager in Markdown Special Paste plugin'))
            return ''
    else:
        s = s.replace('{filedir}', def_val)

    if os.sep in s:
        os.makedirs(s, exist_ok=True)

    return s


def dbg(s):
    #print(s)
    pass

def get_title(s, tag):
    n = s.find('<'+tag+'>')
    if n<0:
        dbg('no <title>: '+s)
        return
    s = s[n+len(tag)+2:]
    n = s.find('</'+tag+'>')
    if n<0:
        dbg('no </title>: '+s)
        return
    s = s[:n]
    return html.unescape(s)


class Command:

    def __init__(self):

        global option_timeout
        global option_pic_path
        global option_pic_name
        global option_pic_ext
        global option_now

        try:
            option_timeout = int(ini_read(fn_config, option_section, 'url_timeout', str(option_timeout)))
        except:
            print('ERROR: '+_('Bad value in plugins.ini [%s] %s')%(option_section, 'url_timeout'))

        option_pic_path = ini_read(fn_config, option_section, 'pic_path', option_pic_path)
        option_pic_name = ini_read(fn_config, option_section, 'pic_name', option_pic_name)
        option_pic_ext = ini_read(fn_config, option_section, 'pic_ext', option_pic_ext)
        option_now = ini_read(fn_config, option_section, 'now', option_now)


    def on_paste(self, ed_self, keep_caret, select_then):

        # Shift pressed? don't work
        state = app_proc(PROC_GET_KEYSTATE, '')
        if 's' in state:
            return

        fmt = app_proc(PROC_CLIP_ENUM, '')
        if 'p' in fmt:
            self.paste_pic()
            return False # block usual Paste

        if 't' in fmt:
            return self.paste_text()

    def paste_pic(self):

        fn_ed = ed.get_filename()
        if not fn_ed:
            msg_status(_('Cannot paste picture in the untitled tab'))
            return

        save_dir = resolve_pic_path(option_pic_path)
        s_input = option_pic_name\
                    .replace('{now}', datetime.now().strftime(option_now) )\
                    .replace('{dirname}', os.path.basename(os.path.dirname(fn_ed)))

        while True:
            s_input = dlg_input(
                _('Clipboard contains some picture.\nSave it to file in: "{}"\n(without ".{}"):').format(save_dir, option_pic_ext), s_input)
            s = s_input
            if not s:
                return
            if not s.endswith('.' + option_pic_ext) and not s.endswith('.png') and not s.endswith('.jpg') and not s.endswith('.jpeg'):
                s += '.' + option_pic_ext

            fn = os.path.join(save_dir, s)
            if os.path.exists(fn):
                msg_status(_('File already exists: ')+fn)
            else:
                break

        if not app_proc(PROC_CLIP_SAVE_PIC, fn):
            msg_status(_('Cannot save clipboard to file: ')+fn)
            return

        lex = ed.get_prop(PROP_LEXER_FILE)
        text = FORMAT_PIC.get(lex)
        if not text:
            return

        fn_rel = os.path.relpath(fn, os.path.dirname(fn_ed))
        fn_rel = fn_rel.replace('\\', '/')
        fn_rel = fn_rel.replace(' ', '%20')

        text = text.replace('{filename}', fn_rel)
        ed.cmd(cmds.cCommand_TextInsert, text)


    def paste_text(self):

        s = app_proc(PROC_GET_CLIP, '')
        if '\n' in s:
            return
        if not s.startswith('http://') and not s.startswith('https://'):
            return

        try:
            r = requests.get(s, verify=False, timeout=option_timeout)
        except:
            return

        if not r:
            return
        text = r.content.decode('utf-8', errors='replace')
        if not text:
            return

        title = get_title(text, 'title') or get_title(text, 'TITLE') or 'Title'

        lex = ed.get_prop(PROP_LEXER_CARET)
        fmt = FORMAT_URL.get(lex)
        if not fmt:
            return
        fmt = fmt.replace('{url}', s)
        fmt = fmt.replace('{title}', title)

        ed.cmd(cmds.cCommand_TextInsert, fmt)
        return False #block usual Paste


    def config(self):

        ini_write(fn_config, option_section, 'url_timeout', str(option_timeout))
        ini_write(fn_config, option_section, 'pic_path', option_pic_path)
        ini_write(fn_config, option_section, 'pic_name', option_pic_name)
        ini_write(fn_config, option_section, 'pic_ext', option_pic_ext)
        ini_write(fn_config, option_section, 'now', option_now)
        file_open(fn_config)

        lines = [ed.get_text_line(i) for i in range(ed.get_line_count())]
        try:
            index = lines.index('['+option_section+']')
            ed.set_caret(0, index)
        except:
            pass
