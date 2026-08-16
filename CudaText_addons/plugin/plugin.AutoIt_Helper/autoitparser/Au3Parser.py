import os
import re


regcons = re.compile(r'(Global\s+|)Const\s+(\$\w+)\s*(=.*)', re.I)
regvars = re.compile(r'(Global\s+|Const\s+|)(\$\w+)\s*(=|)', re.I)
regfuns = re.compile(r'Func\s+([\w_]+)\s*\((.*?)\)', re.I)
regincs = re.compile(r'#include\s*(<|")(.*?)[>|"]', re.I)


class Au3Parser:
    """Parser for opened au3 file"""
    __slots__ = ['_file', '_keywords', '_functions', '_ikeywords', '_ifunctions', '_times', '_defs']
    autoitpath = ''

    def __init__(self):
        self._keywords = []
        self._functions = []
        self._ikeywords = []
        self._ifunctions = []
        self._times = {}
        self._defs = {}

    def parse_au3_file(self, text, file, row=0):
        "parse text and update cache"
        self._keywords = []
        self._functions = []
        if not os.path.isfile(file):
            return
        filepath = os.path.dirname(file)

        infunc = False
        varcache = []
        iscomment = False
        for line_number, line in enumerate(text, 1):
            # passed commented line
            ls = line.strip().lower()
            if ls.find(';') == 0:
                continue
            if ls.find('#cs') == 0 or ls.find('#comments-start') == 0:
                iscomment = True
            if ls.find('#ce') >= 0 or ls.find('#comments-end') >= 0:
                iscomment = False
            if iscomment is True:
                continue

            if line_number <= row:
                if 'func ' in line.lower():
                    infunc = True
                if 'endfunc' in line.lower():
                    infunc = False
                    varcache = []
                if line_number == row:
                    infunc = False
                    self._keywords.extend(varcache)
                    varcache = []

                # find constants
                foundcons = regcons.findall(line)
                for f in foundcons:
                    fx = ''.join([f[1].strip(), '|', f[2].strip()])
                    c = ['const', fx]
                    if infunc and ('global' not in f[0].lower()):
                        if c not in varcache:
                            varcache.append(c)
                    else:
                        if c not in self._keywords:
                            self._keywords.append(c)
                    self._defs.update({f[1].lower(): [file, line_number]})

                # find variables
                foundvars = regvars.findall(line)
                for f in foundvars:
                    if 'const' in f[0].lower():
                        continue
                    v = ['var', f[1]]
                    if infunc and ('global' not in f[0].lower()):
                        if v not in varcache:
                            varcache.append(v)
                    else:
                        if v not in self._keywords:
                            self._keywords.append(v)
                    if f[2] == '=' and (v not in self._keywords or v not in varcache):
                        self._defs.update({f[1].lower(): [file, line_number]})

            # find functions
            foundfuns = regfuns.findall(line)
            for f in foundfuns:
                fn = ['udf', f[0], f[1]]
                if fn not in self._functions:
                    self._functions.append(fn)
                self._defs.update({f[0].lower(): [file, line_number]})

            # scan included files
            self._scan_includes(line, line_number, filepath)

    def parse_inlude_file(self, text, file):
        "parse text and update cache"
        filepath = os.path.dirname(file)

        iscomment = False
        for line_number, line in enumerate(text, 1):
            # passed commented line
            ls = line.strip().lower()
            if ls.find(';') == 0:
                continue
            if ls.find('#cs') == 0 or ls.find('#comments-start') == 0:
                iscomment = True
            if ls.find('#ce') >= 0 or ls.find('#comments-end') >= 0:
                iscomment = False
            if iscomment is True:
                continue

            # find constants
            foundcons = regcons.findall(line)
            for f in foundcons:
                fx = ''.join([f[1].strip(), '|', f[2].strip()])
                c = ['const', fx]
                if c not in self._ikeywords:
                    self._ikeywords.append(c)
                self._defs.update({f[1].lower(): [file, line_number]})

            # find functions
            foundfuns = regfuns.findall(line)
            for f in foundfuns:
                if f[0].find('__') == 0:
                    continue
                fn = ['udf', f[0], f[1]]
                if fn not in self._ifunctions:
                    self._ifunctions.append(fn)
                self._defs.update({f[0].lower(): [file, line_number]})

            # scan included files
            self._scan_includes(line, line_number, filepath)

    @property
    def keywords(self):
        return self._keywords + self._ikeywords

    @property
    def functions(self):
        return self._functions + self._ifunctions

    @property
    def definitions(self):
        return self._defs

    def _scan_includes(self, line, line_number, filepath):
        # scan included files
        foundincs = regincs.findall(line)
        for f in foundincs:
            if f[0] == '<':
                # AutoIt UDFs <filename>
                incfile = os.path.join(self.autoitpath, 'Include', f[1])
            else:
                # locale files "filename"
                incfile = os.path.join(filepath, f[1])

            if os.path.isfile(incfile):
                fileitime = os.path.getmtime(incfile)
                if self._times.get(incfile) != fileitime:
                    self._times[incfile] = fileitime
                    self._defs.update({f[1].lower(): [incfile, line_number]})
                    with open(incfile, encoding='utf-8', errors='ignore') as t:
                        self.parse_inlude_file(t, incfile)