import os
import re
import json
import cudatext as ct
import cudatext_cmd as ct_cmd
from .autoitparser import ApiParser, Au3Parser


def msg(s, level=0):
    if level == 0:
        print('cuda_autoit_helper:', s)
    elif level == 1:
        print('cuda_autoit_helper WARNING:', s)
    elif level == 2:
        print('cuda_autoit_helper ERROR:', s)


class Command:
    filesettings = os.path.join(ct.app_path(ct.APP_DIR_SETTINGS),
                                'cuda_autoit_helper.json')

    def __init__(self):
        self.settings = {}
        if os.path.isfile(self.filesettings):
            with open(self.filesettings) as fs:
                self.settings = json.load(fs)
            Au3Parser.autoitpath = self.settings.get('autoit_dir')
        else:
            msg('For full functionality - set the AutoIt directory.', 1)

        self.api_file = os.path.join(os.path.dirname(__file__), 'au3.api')
        self.api = ApiParser(self.api_file)
        self.parsers = {}
        self.definitions = {}

    def parser(self, ed_self):
        file = ed_self.get_filename()
        current = self.parsers.setdefault(file, Au3Parser())
        text = re.split('\r|\n', ed_self.get_text_all())
        row = ct.ed.get_carets()[0][1]
        current.parse_au3_file(text, file, row)

        self.keywords = self.api.keywords + current.keywords
        self.functions = self.api.functions + current.functions
        self.definitions = current.definitions

    def on_goto_def(self, ed_self):
        """go to definition call"""
        self.parser(ed_self)
        cursor = self.get_cursor()
        if not cursor:
            return
        word, _ = self.get_word_under_cursor(*cursor)
        if not word:
            return
        df = self.definitions.get(word.lower())  # [file, line_number] and None
        if df:
            self.goto_file(*df)
            return True
        else:
            ct.msg_status('Goto - no definition found for : ' + word)

    def goto_file(self, filename, row, col=0):
        """open definition file and mark line"""
        if not os.path.isfile(filename):
            return
        ct.file_open(filename)
        ct.ed.set_prop(ct.PROP_LINE_TOP, str(max(0, row - 5)))  # 5 = Offset
        ct.ed.set_caret(col, row - 1)
        ct.msg_status('Goto "%s", Line %d' % (filename, row))
        return True

    def on_func_hint(self, ed_self):
        """show hint call"""
        self.parser(ed_self)
        cursor = self.get_cursor()
        if not cursor:
            return
        row, col = cursor

        line = ct.ed.get_text_line(row).lower()
        end = line.rfind('(', 0, col+1)
        start = line.rfind(' ', 0, end)+1
        s = line[start:end].strip('( )')

        for f in self.functions:
            if f[1].lower() == s:
                if f[2]:
                    return ' ( ' + f[2] + ' )'

    def on_complete(self, ed_self):
        """autocomplete call"""
        self.parser(ed_self)
        cursor = self.get_cursor()
        if not cursor:
            return
        word, pos = self.get_word_under_cursor(*cursor)
        if not word:
            return
        source = word[:pos].lower()

        # create autocomplete list
        complete_list = ''
        for f in self.functions:
            if f[1].lower().find(source) == 0:
                pars = ''
                if f[2]:
                    pars = ''.join(['(', f[2].strip(), ')'])
                complete_list += '|'.join([f[0], f[1].strip(), pars]) + '\n'
        for v in self.keywords:
            if v[1].lower().find(source) == 0:
                complete_list += '|'.join([v[0], v[1], ' \n'])
        if not complete_list:
            return True

        ct.ed.complete(complete_list, pos, len(word)-pos)
        return True

    def get_cursor(self):
        """get current cursor position"""
        carets = ct.ed.get_carets()
        if len(carets) != 1:
            return
        x0, y0, x1, y1 = carets[0]
        if not 0 <= y0 < ct.ed.get_line_count():
            return
        line = ct.ed.get_text_line(y0)
        if not 0 <= x0 <= len(line):
            return
        return (y0, x0)

    def get_word_under_cursor(self, row, col, seps='.,:-!<>()[]{}\'"\t\n\r'):
        """get current word under cursor position"""
        line = ct.ed.get_text_line(row)
        if not 0 <= col <= len(line):
            return '', 0
        for sep in seps:
            if sep in line:
                line = line.replace(sep, ' ')
        s = ''.join([' ', line, ' '])
        start = s.rfind(' ', 0, col+1)
        end = s.find(' ', col+1)-1
        word = line[start:end]
        return word, col-start  # word, position cursor in word

    def set_autoit_path(self):
        """set path to AutoIt directory"""
        d = Au3Parser.autoitpath if os.path.isdir(Au3Parser.autoitpath) else ct.app_path(ct.APP_DIR_EXE)
        path = ct.dlg_dir(d)
        if self.check_autoit_path(path):
            Au3Parser.autoitpath = path
            self.settings['autoit_dir'] = path
            with open(self.filesettings, mode='w', encoding='utf-8') as fs:
                json.dump(self.settings, fs, indent=4)
            msg('AutoIt path set: {}'.format(path))

    def check_autoit_path(self, path):
        """check if AutoIt dir is exists"""
        if os.path.isdir(os.path.join(path, 'Include')):
            return True
        else:
            msg('Please set correct the AutoIt directory.', 1)
            return False

    def on_key(self, ed_self, code, state):
        """insert args for function under cursor"""
        if 'AutoIt' not in ct.ed.get_prop(ct.PROP_LEXER_FILE):
            return
        if code != 9:  # tab-key=9
            return
        if state != '':
            return
        if ed_self.get_prop(ct.PROP_TAB_COLLECT_MARKERS):
            return
        cursor = self.get_cursor()
        if not cursor:
            return
        row, col = cursor

        word, _ = self.get_word_under_cursor(*cursor, seps=')\n\r\t')
        if not word:
            return
        brackets = False
        if word[-1:] == '(':
            brackets = True
            word = word.strip(' (')

        for f in self.functions:
            if f[1].lower() == word.lower():
                params = f[2].split(',')
                i = min(f[2].count(',', 0, f[2].find('[')),
                        f[2].count(',', 0, f[2].find('='))-1)

                args = []
                for p in params:
                    args.append(p.strip('[ ]'))
                s = ', '.join(args)
                ls = len(s)

                # insert args
                if brackets:
                    ct.ed.insert(col, row, s)
                else:
                    ct.ed.insert(col, row, ''.join(['(', s, ')']))

                # generate tab stops
                marks = []
                k = int(not brackets)
                x0 = col + k
                # x0 = col if brackets else col + 1
                for n, arg in enumerate(args):
                    larg = len(arg)
                    x1 = x0+larg
                    marks.append([x0, row, 0, larg])
                    z = col + ls - x1 + k
                    if n >= i and z != 0:
                        marks.append([x1, row, 0, col+ls-x1+k, 0])
                    x0 = x1 + 2
                marks.reverse()
                for m in marks:
                    ct.ed.markers(ct.MARKERS_ADD, *m)
                ct.ed.set_prop(ct.PROP_TAB_COLLECT_MARKERS, '1')
                ct.ed.cmd(ct_cmd.cmd_Markers_GotoLastAndDelete)
                return False

    def show_docstring(self):
        cursor = self.get_cursor()
        if not cursor:
            return
        word, _ = self.get_word_under_cursor(*cursor)
        if not word:
            return
        with open(self.api_file, encoding='utf-8') as f:
            for line in f:
                if line.lower().find(word.lower()) == 0:
                    if '/a>' in line:
                        start = line.find('<a')
                        end = line.find('/a>') + 3
                        line = line[:start] + line[end:]
                    ct.app_log(ct.LOG_CLEAR, '', panel=ct.LOG_PANEL_OUTPUT)
                    ct.app_log(ct.LOG_ADD, line, panel=ct.LOG_PANEL_OUTPUT)
                    ct.ed.cmd(ct_cmd.cmd_ShowPanelOutput)
                    ct.ed.focus()
                    return True
        ct.msg_status('Cannot find doc-string')
