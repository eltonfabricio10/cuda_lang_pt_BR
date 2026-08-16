from cudatext import *
from . import format_proc

format_proc.MSG = '[Remove Greek accents] '

def do_format(s):

    s = s.replace('Ά' , 'Α')
    s = s.replace('Έ' , 'Ε')
    s = s.replace('Ή' , 'Η')
    s = s.replace('Ί' , 'Ι')
    s = s.replace('Ϊ' , 'Ι')
    s = s.replace('Ϊ́' , 'Ι')
    s = s.replace('Ό' , 'Ο')
    s = s.replace('Ύ' , 'Υ')
    s = s.replace('Ώ' , 'Ω')
    s = s.replace('ά' , 'α')
    s = s.replace('έ' , 'ε')
    s = s.replace('ή' , 'η')
    s = s.replace('ί' , 'ι')
    s = s.replace('ϊ' , 'ι')
    s = s.replace('ΐ' , 'ι')
    s = s.replace('ό' , 'ο')
    s = s.replace('ύ' , 'υ')
    s = s.replace('ώ' , 'ω')
    return s

class Command:

    def run(self):
        format_proc.run(do_format)
