import sys
import datetime
import os
import re
from time import sleep
from subprocess import Popen, PIPE, STDOUT
from threading import Thread, Lock
import signal
import time

import cudatext_keys as keys
import cudatext_cmd as cmds
from cudatext import *

# Para ollama
import requests
import json

from cudax_lib import get_translation
_ = get_translation(__file__)  # i18n

fn_icon = os.path.join(os.path.dirname(__file__), 'ailocal.png')
fn_config = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_ailocal.ini')
MAX_BUFFER = 100*1000
IS_WIN = os.name=='nt'
IS_MAC = sys.platform=='darwin'
READSIZE = 4*1024
HOMEDIR = os.path.expanduser('~')
INPUT_H = 26

def bool_to_str(v):
    return '1' if v else '0'

def str_to_bool(s):
    return s=='1'

class Command:
    title_console = 'AI Local Console'
    h_console = None
    threadText = ""

    def __init__(self):
        try:
            self.font_size = int(ini_read(fn_config, 'op', 'font_size', '9'))
        except:
            ini_write(fn_config, 'op', 'font_size', '9')

        try:
            self.max_history = int(ini_read(fn_config, 'op', 'max_history', '10'))
        except:
            ini_write(fn_config, 'op', 'max_history', '10')

        try:
            self.url = str(ini_read(fn_config, 'op', 'url', 'http://localhost:11434/api/generate'))
        except:
            # Ollama URL
            ini_write(fn_config, 'op', 'url', 'http://localhost:11434/api/generate')

        try:
            self.key = str(ini_read(fn_config, 'op', 'key', ''))
        except:
            ini_write(fn_config, 'op', 'key', '')

        try:
            self.model = str(ini_read(fn_config, 'op', 'model', 'qwen2.5-coder:3b'))
        except:
            # Example model
            ini_write(fn_config, 'op', 'model', 'qwen2.5-coder:3b')

        try:
            self.temperature = float(ini_read(fn_config, 'op', 'temperature', '1.0'))
        except:
            # Temperature by default
            ini_write(fn_config, 'op', 'temperature', '1.0')

        try:
            self.del_simbols = int(ini_read(fn_config, 'op', 'del_simbols', '1'))
        except:
            # Temperature by default
            ini_write(fn_config, 'op', 'del_simbols', '1')

        try:
            self.tool = str(ini_read(fn_config, 'op', 'tool', 'ollama'))
        except:
            # Tools ollama or lmstudio
            ini_write(fn_config, 'op', 'tool', str(self.tool))

        #self.dark_colors = str_to_bool(ini_read(fn_config, 'op', 'dark_colors', '1'))

        self.h_menu = menu_proc(0, MENU_CREATE)

        self.load_history()

        #for-loop doesn't work here
        self.menu_calls = []
        self.menu_calls += [ lambda: self.run_cmd_n(0) ]
        self.menu_calls += [ lambda: self.run_cmd_n(1) ]
        self.menu_calls += [ lambda: self.run_cmd_n(2) ]
        self.menu_calls += [ lambda: self.run_cmd_n(3) ]
        self.menu_calls += [ lambda: self.run_cmd_n(4) ]
        self.menu_calls += [ lambda: self.run_cmd_n(5) ]
        self.menu_calls += [ lambda: self.run_cmd_n(6) ]
        self.menu_calls += [ lambda: self.run_cmd_n(7) ]
        self.menu_calls += [ lambda: self.run_cmd_n(8) ]
        self.menu_calls += [ lambda: self.run_cmd_n(9) ]
        self.menu_calls += [ lambda: self.run_cmd_n(10) ]
        self.menu_calls += [ lambda: self.run_cmd_n(11) ]
        self.menu_calls += [ lambda: self.run_cmd_n(12) ]
        self.menu_calls += [ lambda: self.run_cmd_n(13) ]
        self.menu_calls += [ lambda: self.run_cmd_n(14) ]
        self.menu_calls += [ lambda: self.run_cmd_n(15) ]
        self.menu_calls += [ lambda: self.run_cmd_n(16) ]
        self.menu_calls += [ lambda: self.run_cmd_n(17) ]
        self.menu_calls += [ lambda: self.run_cmd_n(18) ]
        self.menu_calls += [ lambda: self.run_cmd_n(19) ]
        self.menu_calls += [ lambda: self.run_cmd_n(20) ]
        self.menu_calls += [ lambda: self.run_cmd_n(21) ]


    def upd_history_combo(self):

        self.input.set_prop(PROP_COMBO_ITEMS, '\n'.join(self.history))


    def load_history(self):

        self.history = []
        for i in range(self.max_history):
            s = ini_read(fn_config, 'prompts', str(i), '')
            if s:
                self.history += [s]


    def save_history(self):

        ini_proc(INI_DELETE_SECTION, fn_config, 'prompts')
        for (i, s) in enumerate(self.history):
            ini_write(fn_config, 'prompts', str(i), s)


    def init_forms(self):
        self.h_console = self.init_console_form()
        app_proc(PROC_BOTTOMPANEL_ADD_DIALOG, (self.title_console, self.h_console, fn_icon))

    def over_selected_text(self):
        self.open_console()
        self.run_cmd("")

    def open_side_panel(self):

        # don't init form twice!
        if not self.h_side:
            self.init_forms()

        dlg_proc(self.h_side, DLG_CTL_FOCUS, name='list')

        app_proc(PROC_SIDEPANEL_ACTIVATE, (self.title_side, True)) #True - set focus

    def open_console(self):

        #don't init form twice!
        if not self.h_console:
            self.init_forms()

        dlg_proc(self.h_console, DLG_CTL_FOCUS, name='input')

        app_proc(PROC_BOTTOMPANEL_ACTIVATE, (self.title_console, True)) #True - set focus

    def init_console_form(self):

        colors = app_proc(PROC_THEME_UI_DICT_GET,'')
        color_btn_back = colors['ButtonBgPassive']['color']
        color_btn_font = colors['ButtonFont']['color']

        #color_memo_back = 0x0 if self.dark_colors else color_btn_back
        #color_memo_font = 0xC0C0C0 if self.dark_colors else color_btn_font
        color_memo_back = color_btn_back
        color_memo_font = color_btn_font

        cur_font_size = self.font_size

        h = dlg_proc(0, DLG_CREATE)
        dlg_proc(h, DLG_PROP_SET, prop={
            'border': False,
            'keypreview': True,
            'on_key_down': self.form_key_down,
            #'on_show': self.form_show,
            #'on_hide': self.form_hide,
            'color': color_btn_back,
            })

        n = dlg_proc(h, DLG_CTL_ADD, 'button_ex')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'enter',
            'a_l': None,
            'a_t': None,
            'a_r': ('', ']'),
            'a_b': ('', ']'),
            'w': 90,
            'h': INPUT_H,
            'cap': 'Enter',
            'hint': _('Hotkey: Enter'),
            'on_change': self.button_enter_click,
            })

        n = dlg_proc(h, DLG_CTL_ADD, 'editor_combo')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'input',
            'border': True,
            'h': INPUT_H,
            'a_l': ('', '['),
            'a_r': ('enter', '['),
            'a_t': ('enter', '-'),
            'font_size': cur_font_size,
            'texthint': _('Enter the prompt text for the selected text (or /help):'),
            })
        self.input = Editor(dlg_proc(h, DLG_CTL_HANDLE, index=n))

        n = dlg_proc(h, DLG_CTL_ADD, 'editor')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'memo',
            'a_t': ('', '['),
            'a_l': ('', '['),
            'a_r': ('', ']'),
            'a_b': ('enter', '['),
            'font_size': cur_font_size,
            })
        self.memo = Editor(dlg_proc(h, DLG_CTL_HANDLE, index=n))

        self.memo.set_prop(PROP_RO, True)
        self.memo.set_prop(PROP_CARET_VIRTUAL, False)
        self.memo.set_prop(PROP_GUTTER_ALL, False)
        self.memo.set_prop(PROP_UNPRINTED_SHOW, False)
        self.memo.set_prop(PROP_MARGIN, 2000)
        self.memo.set_prop(PROP_MARGIN_STRING, '')
        self.memo.set_prop(PROP_LAST_LINE_ON_TOP, False)
        self.memo.set_prop(PROP_HILITE_CUR_LINE, False)
        self.memo.set_prop(PROP_HILITE_CUR_COL, False)
        self.memo.set_prop(PROP_MODERN_SCROLLBAR, True)
        self.memo.set_prop(PROP_MINIMAP, False)
        self.memo.set_prop(PROP_MICROMAP, False)
        self.memo.set_prop(PROP_COLOR, (COLOR_ID_TextBg, color_memo_back))
        self.memo.set_prop(PROP_COLOR, (COLOR_ID_TextFont, color_memo_font))

        self.input.set_prop(PROP_ONE_LINE, True)
        self.input.set_prop(PROP_GUTTER_ALL, True)
        self.input.set_prop(PROP_GUTTER_NUM, False)
        self.input.set_prop(PROP_GUTTER_FOLD, False)
        self.input.set_prop(PROP_GUTTER_BM, False)
        self.input.set_prop(PROP_GUTTER_STATES, False)
        self.input.set_prop(PROP_UNPRINTED_SHOW, False)
        self.input.set_prop(PROP_MARGIN, 2000)
        self.input.set_prop(PROP_MARGIN_STRING, '')
        self.input.set_prop(PROP_HILITE_CUR_LINE, False)
        self.input.set_prop(PROP_HILITE_CUR_COL, False)

        self.upd_history_combo()

        dlg_proc(h, DLG_SCALE)
        return h


    def config(self):

        ini_write(fn_config, 'op', 'max_history', str(self.max_history))
        ini_write(fn_config, 'op', 'font_size', str(self.font_size))
        ini_write(fn_config, 'op', 'url', str(self.url))
        ini_write(fn_config, 'op', 'model', str(self.model))
        ini_write(fn_config, 'op', 'temperature', str(self.temperature))
        ini_write(fn_config, 'op', 'del_simbols', str(self.del_simbols))
        ini_write(fn_config, 'op', 'tool', str(self.tool))
        ini_write(fn_config, 'op', 'key', str(self.key))
        #ini_write(fn_config, 'op', 'dark_colors', bool_to_str(self.dark_colors))

        file_open(fn_config)


    def form_key_down(self, id_dlg, id_ctl, data='', info=''):

        #Enter
        if (id_ctl==keys.VK_ENTER) and (data==''):
            text = self.input.get_text_line(0)
            self.input.set_text_all('')
            self.input.set_caret(0, 0)
            self.run_cmd(text)
            return False

        #Up/Down: scroll memo
        if (id_ctl==keys.VK_UP) and (data==''):
            self.memo.cmd(cmds.cCommand_ScrollLineUp)
            return False

        if (id_ctl==keys.VK_DOWN) and (data==''):
            self.memo.cmd(cmds.cCommand_ScrollLineDown)
            return False

        #PageUp/PageDown: scroll memo
        if (id_ctl==keys.VK_PAGEUP) and (data==''):
            self.memo.cmd(cmds.cCommand_ScrollPageUp)
            return False

        if (id_ctl==keys.VK_PAGEDOWN) and (data==''):
            self.memo.cmd(cmds.cCommand_ScrollPageDown)
            return False

        #Ctrl+Down: history menu
        if (id_ctl==keys.VK_DOWN) and (data=='c'):
            self.show_history()
            return False

        #Escape: go to editor
        if (id_ctl==keys.VK_ESCAPE) and (data==''):
            # Stops the timer
            timer_proc(TIMER_STOP, self.timer_update, 0)
            ed.focus()
            ed.cmd(cmds.cmd_ToggleBottomPanel)
            return False

        #Enter (cannot react to Ctrl+Enter)
        if (id_ctl==keys.VK_PAUSE):
            self.button_break_click(0, 0)
            return False


    def show_history(self):

        menu_proc(self.h_menu, MENU_CLEAR)
        for (index, item) in enumerate(self.history):
            menu_proc(self.h_menu, MENU_ADD,
                index=0,
                caption=item,
                command=self.menu_calls[index],
                )

        prop = dlg_proc(self.h_console, DLG_CTL_PROP_GET, name='input')
        x, y = prop['x'], prop['y']
        x, y = dlg_proc(self.h_console, DLG_COORD_LOCAL_TO_SCREEN, index=x, index2=y)
        menu_proc(self.h_menu, MENU_SHOW, command=(x, y))


    def run_cmd(self, text):

        while len(self.history) >= self.max_history:
            del self.history[0]

        try:
            n = self.history.index(text)
            del self.history[n]
        except:
            pass

        self.history += [text]
        self.upd_history_combo()

        if text=='/insert':
            ed.cmd(cmds.cCommand_TextInsert, self.memo.get_text_all())
            if self.del_simbols:
                ed.cmd(cmds.cmd_FinderAction,'repall\x01>>> \x01\x01oA')
            return

        if text=='/clear':
            self.memo.set_prop(PROP_RO, False)
            self.memo.set_text_all('')
            self.memo.set_prop(PROP_RO, True)
            return

        if text=='/help':
            self.memo.set_prop(PROP_RO, False)
            self.memo.set_text_line(-1,_("Option 1: select the text and type the prompt"))
            self.memo.set_text_line(-1,_("Option 2: just type the prompt"))
            self.memo.set_text_line(-1,_("/clear: clear the console text"))
            self.memo.set_text_line(-1,_("/insert: insert console selected text to the current document"))
            self.memo.set_prop(PROP_RO, True)
            return

        text += "\n" + ed.get_text_sel()

        self.input.set_text_all('')

        self.print_in_memo(_("\nUser prompt\n"))
        self.print_in_memo(text)

        if self.tool == "ollama":
            thread_llm_obj = Thread(target=self.thread_ollama, args=(text,))
            if thread_llm_obj.is_alive():
                return
            thread_llm_obj.start()
        if self.tool == "lmstudio":
            thread_llm_obj = Thread(target=self.thread_lmstudio, args=(text,))
            if thread_llm_obj.is_alive():
                return
            thread_llm_obj.start()

        self.exec(text)

    def thread_lmstudio(self, text):
        url = self.url

        # Your request payload
        headers = {"Authorization": f"Bearer {self.key}"}
        payload = {
            "model": self.model,
            "messages": [
                { "role": "system", "content": _("Answer") },
                { "role": "user", "content": text }
            ],
            "temperature": self.temperature,
            "max_tokens": -1,
            "stream": False
        }

        headers = {
            "Content-Type": "application/json"
        }

        # Send POST request
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
        except Exception as e:
            self.print_in_memo("Error LM Studio: ")
            self.print_in_memo(str(e))
            return


        # Check for successful response
        if response.status_code == 200:
            self.response_json = response.json()
            print(self.response_json)
            self.bot_response = self.response_json.get("choices")[0].get("message").get("content") if self.response_json.get("choices") else _("Sorry, I couldn't get a response.")
            self.print_in_memo("\nBot AI\n")
            self.print_in_memo(self.bot_response)
        else:
            self.print_in_memo(_("Error: Request failed with status code ") + str(response.status_code))

    def thread_ollama(self, text):
        # LLM Connect
        headers = {"Authorization": f"Bearer {self.key}"}
        # headers = {"Authorization: Bearer {}".format(self.key)}
        data = {
            "model": self.model,
            "temperature": self.temperature,
            "prompt": text
        }

        self.print_in_memo("\nBot AI\n")

        try:
            response = requests.post(self.url, headers=headers, json=data, stream=True)
        except Exception as e:
            self.print_in_memo("Error Ollama: ")
            self.print_in_memo(str(e))
            return

        line_resp = ""

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                line_resp = line_resp + str(json.loads(decoded_line)["response"])

        self.print_in_memo(line_resp)

    def print_in_memo(self, text):
        text_line = text.split("\n")
        self.memo.set_prop(PROP_RO, False)
        for linex in text_line:
            self.memo.set_text_line(-1, ">>> " + linex)
        self.memo.set_prop(PROP_RO, True)

    def exec(self, s):

        pass


    def run_cmd_n(self, n):

        if n<len(self.history):
            s = self.history[n]
            self.input.set_text_all(s)
            self.input.set_caret(len(s), 0)


    def update_output(self, s):

        self.memo.set_prop(PROP_RO, False)
        self.memo.set_text_all(s)
        self.memo.set_prop(PROP_RO, True)

        self.memo.cmd(cmds.cCommand_GotoTextEnd)
        self.memo.set_prop(PROP_LINE_TOP, self.memo.get_line_count()-3)


    def on_exit(self, ed_self):
        self.save_history()


    def button_enter_click(self, id_dlg, id_ctl, data='', info=''):
        text = self.input.get_text_line(0)
        self.input.set_text_all('')
        self.input.set_caret(0, 0)
        self.run_cmd(text)
        return False


    def callback_list_dblclick(self, id_dlg, id_ctl, data='', info=''):
        if ed.get_prop(PROP_RO):
            return

        index = listbox_proc(self.h_list, LISTBOX_GET_SEL)
        if index<0:
            return

        ed.cmd(cmds.cCommand_TextInsert, _('Inserted item %d...') % index)


    def set_imagelist_size(self, theme_name, imglist):

        # res = re.match('^\S+x(\d+)$', theme_name)
        res = re.match(r'^\S+x(\d+)$', theme_name)
        if not res:
            return msg_box(_('AI Local: bad icons folder name: "%s"') % theme_name, MB_OK+MB_ICONERROR)
        n = int(res.group(1))
        if not 8<=n<=64:
            return msg_box(_('AI Local: bad icons size: "%s"') % theme_name, MB_OK+MB_ICONERROR)

        imagelist_proc(imglist, IMAGELIST_SET_SIZE, (n, n))


    def toolbar_add_btn(self, h_bar, hint, icon=-1, command=''):

        toolbar_proc(h_bar, TOOLBAR_ADD_ITEM)
        cnt = toolbar_proc(h_bar, TOOLBAR_GET_COUNT)
        h_btn = toolbar_proc(h_bar, TOOLBAR_GET_BUTTON_HANDLE, index=cnt-1)
        if hint=='-':
            button_proc(h_btn, BTN_SET_KIND, BTNKIND_SEP_HORZ)
        else:
            button_proc(h_btn, BTN_SET_KIND, BTNKIND_ICON_ONLY)
            button_proc(h_btn, BTN_SET_HINT, hint)
            button_proc(h_btn, BTN_SET_IMAGEINDEX, icon)
            button_proc(h_btn, BTN_SET_DATA1, command)


    def action_open_project(self, info=None):

        msg_box(_('Open Project action'), MB_OK)


    def action_save_project_as(self, info=None):

        msg_box(_('Save Project As action'), MB_OK)
