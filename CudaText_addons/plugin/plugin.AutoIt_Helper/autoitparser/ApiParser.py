import os


class ApiParser:
    """Parser for api files"""

    __slots__ = ['_keywords', '_functions']

    def __init__(self, api_file):
        # if not os.path.isfile(api_file):
        self._keywords = []
        self._functions = []
        with open(api_file, encoding='utf-8') as f:
            for line in f:
                arg_pos_start = line.find('(')
                if arg_pos_start > 0:
                    arg_pos_end = line.find(')', arg_pos_start)
                    if arg_pos_end > 0:
                        fname = line[:arg_pos_start].strip()
                        fargs = line[arg_pos_start+1:arg_pos_end].strip()
                        if line[:1] in '_':
                            break  # don't add UDF functions
                            # self._functions.append(['udf', fname, fargs])
                        else:
                            self._functions.append(['function', fname, fargs])
                else:
                    line = line.rstrip('\n\r')
                    i = line[-2:]
                    if i in '?1':
                        self._keywords.append(['special', line[:-2]])
                    elif i in '?2':
                        self._keywords.append(['preprocessor', line[:-2]])
                    elif i in '?3':
                        self._keywords.append(['macros', line[:-2]])
                    elif i in '?4':
                        self._keywords.append(['keyword', line[:-2]])

    @property
    def keywords(self):
        return self._keywords

    @property
    def functions(self):
        return self._functions