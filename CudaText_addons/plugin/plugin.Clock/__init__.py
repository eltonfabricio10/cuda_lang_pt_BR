import os
from datetime import datetime
from cudatext import *

MYCELL = app_proc(PROC_GET_UNIQUE_TAG, '')
CFG_FILE = 'plugins.ini'
CFG_SECTION = 'clock'
CFG_KEY_SEC = 'show_seconds'

def bool_to_str(v): return '1' if v else '0'
def str_to_bool(s): return s=='1'

class Command:
    id_st = 0
    inited = False
    seconds = True
    fmt = ''

    def tick(self, tag='', info=''):

        # add statusbar cell later, so it appears in the right edge
        if not self.inited:
            self.inited = True
            statusbar_proc(self.id_st, STATUSBAR_ADD_CELL, tag=MYCELL)
            statusbar_proc(self.id_st, STATUSBAR_SET_CELL_AUTOSIZE, tag=MYCELL, value=1)
            pause = 1000
            if not self.seconds:
                pause *= 10
            timer_proc(TIMER_START, 'cuda_clock.tick', pause, '')

        now = datetime.now()
        s = now.strftime(self.fmt)
        statusbar_proc(self.id_st, STATUSBAR_SET_CELL_TEXT, tag=MYCELL, value=s)

    def on_start(self, ed_self):

        self.id_st = app_proc(PROC_GET_MAIN_STATUSBAR, '')
        self.seconds = str_to_bool(ini_read(CFG_FILE, CFG_SECTION, CFG_KEY_SEC, '1'))
        self.fmt = "%H:%M:%S" if self.seconds else "%H:%M"
        timer_proc(TIMER_START_ONE, 'cuda_clock.tick', 1000, '')

    def config(self):
        ini_write(CFG_FILE, CFG_SECTION, CFG_KEY_SEC, bool_to_str(self.seconds))
        fn = os.path.join(app_path(APP_DIR_SETTINGS), CFG_FILE)
        if os.path.isfile(fn):
            file_open(fn)
