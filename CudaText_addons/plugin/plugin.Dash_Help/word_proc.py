from cudatext import *
import string

CHARS = string.ascii_letters + string.digits + '$_#'

def get_word_info():
    x0, y0, x2, y2 = ed.get_carets()[0]
    text = ed.get_text_line(y0)
    if not text:
        return (x0, y0, 0, '')
    if x0>len(text):
        x0 = len(text)
    
    x1 = x0
    while x1>0 and text[x1-1] in CHARS: x1-=1
    x2 = x0
    while x2<len(text) and text[x2] in CHARS: x2+=1

    return (x1, y0, x2-x1, text[x1:x2])


def get_word():
    inf = get_word_info()
    if not inf: return ''
    return inf[3]
 
