import os
from cudatext import *
import cudatext_keys as kk
import cudatext_cmd as cmds

MSG_OFF = 'Turned off'
MSG_ONE = 'Shift+arrows: ─┼─┼─, F9: double lines'
MSG_TWO = 'Shift+arrows: ═╬═╬═, F9: single lines'

PROPS = {
  '─': (1, 0, 1, 0),
  '│': (0, 1, 0, 1),
  '┌': (0, 0, 1, 1),
  '┐': (1, 0, 0, 1),
  '└': (0, 1, 1, 0),
  '┘': (1, 1, 0, 0),
  '├': (0, 1, 1, 1),
  '┤': (1, 1, 0, 1),
  '┬': (1, 0, 1, 1),
  '┴': (1, 1, 1, 0),
  '┼': (1, 1, 1, 1),
  '═': (2, 0, 2, 0),
  '║': (0, 2, 0, 2),
  '╒': (0, 0, 2, 1),
  '╓': (0, 0, 1, 2),
  '╔': (0, 0, 2, 2),
  '╕': (2, 0, 0, 1),
  '╖': (1, 0, 0, 2),
  '╗': (2, 0, 0, 2),
  '╘': (0, 1, 2, 0),
  '╙': (0, 2, 1, 0),
  '╚': (0, 2, 2, 0),
  '╛': (2, 1, 0, 0),
  '╜': (1, 2, 0, 0),
  '╝': (2, 2, 0, 0),
  '╞': (0, 1, 2, 1),
  '╟': (0, 2, 1, 2),
  '╠': (0, 2, 2, 2),
  '╡': (2, 1, 0, 1),
  '╢': (1, 2, 0, 2),
  '╣': (2, 2, 0, 2),
  '╤': (2, 0, 2, 1),
  '╥': (1, 0, 1, 2),
  '╦': (2, 0, 2, 2),
  '╧': (2, 1, 2, 0),
  '╨': (1, 2, 1, 0),
  '╩': (2, 2, 2, 0),
  '╪': (2, 1, 2, 1),
  '╫': (1, 2, 1, 2),
  '╬': (2, 2, 2, 2),
}

class Command:
    act = False
    mode = False

    def toggle(self):

        self.act = not self.act
        act = PROC_EVENTS_SUB if self.act else PROC_EVENTS_UNSUB

        # react only to 4 arrow key codes: 37..40, 120=VK_F9
        app_proc(act, 'cuda_draw_lines;on_key;;37,38,39,40,120')
        self.status()


    def status(self):

        msg_status('[Draw Lines] '+(MSG_OFF if not self.act else MSG_TWO if self.mode else MSG_ONE))


    def repl(self, x, y, ch):

        s = ed.get_text_line(y)
        if x<len(s):
            ed.replace(x, y, x+1, y, ch)
        else:
            ed.set_text_line(y, s+' '*(x-len(s))+ch)


    def near_props(self, x, y):
        """
        gets (px1, py1, px2, py2): where each int is
        0: no line, 1: single line, 2: double line
        """

        s = ed.get_text_line(y)

        if 0<=x-1<len(s):
            p = PROPS.get(s[x-1])
            px1 = p[2] if p else 0
        else:
            px1 = 0

        if 0<=x+1<len(s):
            p = PROPS.get(s[x+1])
            px2 = p[0] if p else 0
        else:
            px2 = 0

        if y==0:
            py1 = 0
        else:
            s = ed.get_text_line(y-1)
            if 0<=x<len(s):
                p = PROPS.get(s[x])
                py1 = p[3] if p else 0
            else:
                py1 = 0

        if y+1>=ed.get_line_count():
            py2 = 0
        else:
            s = ed.get_text_line(y+1)
            if 0<=x<len(s):
                p = PROPS.get(s[x])
                py2 = p[1] if p else 0
            else:
                py2 = 0

        return (px1, py1, px2, py2)


    def calc_char(self, x, y, dir):

        px1, py1, px2, py2 = self.near_props(x, y)

        if dir=='r':
            px2 = 2 if self.mode else 1
            if px1>0 and px1!=px2:
                px1 = px2
            if py1==0 and py2==0:
                px1 = px2
            if py1>0 and py2>0 and py1!=py2:
                py2 = py1

        elif dir=='l':
            px1 = 2 if self.mode else 1
            if px2>0 and px1!=px2:
                px2 = px1
            if py1==0 and py2==0:
                px2 = px1
            if py1>0 and py2>0 and py1!=py2:
                py2 = py1

        elif dir=='u':
            py1 = 2 if self.mode else 1
            if py2>0 and py1!=py2:
                py2 = py1
            if px1==0 and px2==0:
                py2 = py1
            if px1>0 and px2>0 and px1!=px2:
                px2 = px1

        elif dir=='d':
            py2 = 2 if self.mode else 1
            if py1>0 and py1!=py2:
                py1 = py2
            if px1==0 and px2==0:
                py1 = py2
            if px1>0 and px2>0 and px1!=px2:
                px2 = px1

        for (ch, p) in PROPS.items():
            if p==(px1, py1, px2, py2):
                return ch

        return '?'


    def on_key(self, ed_self, key, state):

        # handle case when 'reset python plugins' was called
        if not self.act:
            app_proc(PROC_EVENTS_UNSUB, 'cuda_draw_lines;*;;')
            return

        if state=='' and key==kk.VK_F9:
            self.mode = not self.mode
            self.status()
            return False

        # require Shift key
        if 's' not in state: return

        carets = ed.get_carets()
        if len(carets)>1: return
        x, y, x1, y1 = carets[0]

        if key==kk.VK_LEFT:
            if x==0: return
            ch = self.calc_char(x, y, 'l')
            self.repl(x, y, ch)
            ed.cmd(cmds.cCommand_KeyLeft)

        elif key==kk.VK_UP:
            if y==0: return
            ch = self.calc_char(x, y, 'u')
            self.repl(x, y, ch)
            ed.cmd(cmds.cCommand_KeyUp)

        elif key==kk.VK_RIGHT:
            ch = self.calc_char(x, y, 'r')
            self.repl(x, y, ch)
            ed.cmd(cmds.cCommand_KeyRight)

        elif key==kk.VK_DOWN:
            if y==ed.get_line_count()-1: return
            ch = self.calc_char(x, y, 'd')
            self.repl(x, y, ch)
            ed.cmd(cmds.cCommand_KeyDown)

        return False
