import os
import time
from cudatext import *
import cudax_lib as apx
import cudatext_cmd as cmds

_ = apx.get_translation(__file__)  # I18N

FONTS = [font for font in app_proc(PROC_ENUM_FONTS, '') if not font.startswith('@')]
OPTION = 'font_name' + app_proc(PROC_GET_OS_SUFFIX, '')

def reload_and_apply():
    ed.cmd(cmds.cmd_OpsReloadAndApply)

def change_font(font):
    ed.set_prop(PROP_FONT, font)
    apx.set_opt(OPTION,font)

class Command:

    def __init__(self):
        pass


    def select_font_(self):
        focus = -1
        while True:
            if focus==-1:
                current_font = apx.get_opt(OPTION)
                focus = FONTS.index(current_font) if current_font in FONTS else 0

            res = focus = dlg_menu(DMENU_LIST, FONTS, focused=focus, caption=_('Select font'))
            if res is None:
                reload_and_apply() # globally apply settings only on menu close
                return

            change_font(FONTS[res])

    def next_font_(self):
        current_font = apx.get_opt(OPTION)
        idx = FONTS.index(current_font) if current_font in FONTS else 0
        if idx+1 >= len(FONTS):
            return
        idx+=1
        font = FONTS[idx]
        change_font(font)
        print('{}. {}'.format(idx+1,font))
        reload_and_apply()
        time.sleep(0.01) # sleep to help saving config! important

    def previous_font_(self):
        current_font = apx.get_opt(OPTION)
        idx = FONTS.index(current_font) if current_font in FONTS else 0
        if idx == 0:
            return
        idx-=1
        font = FONTS[idx]
        change_font(font)
        print('{}. {}'.format(idx+1,font))
        reload_and_apply()
        time.sleep(0.01) # sleep to help saving config! important
