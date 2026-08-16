from cudatext import *

#bookmarks kinds: 1..9
INDEX_ADD=1
LINES_DEC=10 # how many lines to show from top edge to GoTo position

def doset(id):
    line = ed.get_carets()[0][1]
    items = ed.bookmark(BOOKMARK_GET_ALL, 0)
    for item in items:
        if item['kind']==id+INDEX_ADD:
            ed.bookmark(BOOKMARK_CLEAR, item['line'])
    ed.bookmark(BOOKMARK_SET, line, id+INDEX_ADD)
    msg_status('Set bookmark %d' % id)

def dogoto(id):
    items = ed.bookmark(BOOKMARK_GET_ALL, 0)
    for item in items:
        if item['kind']==id+INDEX_ADD:
            y = item['line']
            ed.set_caret(0, y, -1, -1)
            ed.set_prop(PROP_LINE_TOP, y-LINES_DEC)
            msg_status('Jumped to bookmark %d' % id)
            return
    msg_status('Bookmark %d is not set' % id)


class Command:
    def set1(self):
        doset(1)
    def set2(self):
        doset(2)
    def set3(self):
        doset(3)
    def set4(self):
        doset(4)
    def set5(self):
        doset(5)
    def set6(self):
        doset(6)
    def set7(self):
        doset(7)
    def set8(self):
        doset(8)

    def goto1(self):
        dogoto(1)
    def goto2(self):
        dogoto(2)
    def goto3(self):
        dogoto(3)
    def goto4(self):
        dogoto(4)
    def goto5(self):
        dogoto(5)
    def goto6(self):
        dogoto(6)
    def goto7(self):
        dogoto(7)
    def goto8(self):
        dogoto(8)
