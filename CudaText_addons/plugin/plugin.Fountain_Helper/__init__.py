import os
from cudatext import *
import cudatext_cmd as cmds
from .fo_proc import *
from .preview import do_preview


SIDE_TITLE = 'Dialogs'

def msg(s):
    msg_status('[Fountain] '+s)


class Command:
    last_name = ''
    id_dlg = None
    id_list = None
    filename = ''

    def on_key(self, ed_self, key, state):
        #work on Shift+Enter
        if state=='s' and key==13:
            msg('Shift+Enter')
            carets = ed.get_carets()
            if len(carets)>1: return
            y = carets[0][1]
            s = ed.get_text_line(y)
            s = s.upper()
            ed.set_text_line(y, s)
            ed.cmd(cmds.cCommand_KeyEnter)
            return False #block


    def _find_name(self, name_init):
        lines = ed.get_text_all().splitlines()
        items = find_names(lines)

        while True:
            name = dlg_input('Character name (case ignored):', name_init)
            if not name: return
            items = [i for i in items if i['name'].upper()==name.upper()]
            if items:
                self.last_name = name
                break
            else:
                msg_box('Name "%s" not found, try another name'%name, MB_OK+MB_ICONWARNING)

        items_m = ['['+str(i['i']+1)+'] '+i['text'] for i in items]
        res = dlg_menu(DMENU_LIST, items_m, caption='Occurrences')
        if res is None: return
        #print(items[res])
        y = items[res]['i']
        ed.set_caret(0, y, -1, -1)


    def find_name(self):
        names = self._find_all_names()
        if not names:
            msg('No characters found')
            return

        res = dlg_menu(DMENU_LIST, names, caption='Characters')
        if res is None: return
        self._find_name(names[res])


    def find_name_caret(self):
        carets = ed.get_carets()
        if len(carets)>1: return
        y = carets[0][1]
        ok, name = get_name_from(ed.get_text_line(y))
        if ok:
            self._find_name(name)
        else:
            msg('Not ok name: '+name)


    def _find_all_names(self):

        lines = ed.get_text_all().splitlines()
        items = find_names(lines)

        names = [i['name'] for i in items]
        return sorted(list(set(names)))


    def init_dlg(self):

        h = dlg_proc(0, DLG_CREATE)
        self.id_dlg = h

        n = dlg_proc(h, DLG_CTL_ADD, 'listbox_ex')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'list',
            'align': ALIGN_CLIENT,
            'act': True,
            'on_change': self.callback_list_click,
        })

        self.id_list = dlg_proc(h, DLG_CTL_HANDLE, index=n)


    def fill_side_panel(self, extract_items, name):

        if not self.id_dlg:
            self.init_dlg()

        app_proc(PROC_SIDEPANEL_ADD_DIALOG, (SIDE_TITLE, self.id_dlg, 'output.png'))
        app_proc(PROC_SIDEPANEL_ACTIVATE, SIDE_TITLE)

        listbox_proc(self.id_list, LISTBOX_DELETE_ALL)
        listbox_proc(self.id_list, LISTBOX_ADD, index=-1, text='(from %s)'%name, tag=-1)

        for i in extract_items:
            text = '%d: ' % (i['i']+1) + i['text']
            listbox_proc(self.id_list, LISTBOX_ADD, index=-1, text=text, tag=i['i'])


    def _extract_talks(self, name):

        lines = ed.get_text_all().splitlines()
        items = find_names(lines)
        items = [i for i in items if i['name'].upper()==name.upper()]

        self.filename = ed.get_filename()
        self.fill_side_panel(items, name)

        return [i['text'] for i in items]


    def extract_talks(self):

        names = self._find_all_names()
        if not names:
            msg('No characters found')
            return

        res = dlg_menu(DMENU_LIST, names, caption='Names')
        if res is None: return

        name = names[res]
        items = self._extract_talks(name)

        text_filename = os.path.basename(ed.get_filename())
        text_caption = 'This file contains all dialogue spoken by "%s" extracted from "%s".'\
            % (name, text_filename)

        file_open('')
        ed.set_prop(PROP_TAB_TITLE, 'from '+name)

        text = '\n\n'.join([text_caption]+items)+'\n'
        ed.set_text_all(text)


    def find_scene(self):

        lines = ed.get_text_all().splitlines()
        items = find_scenes(lines)
        if not items:
            msg('No scenes found')
            return

        items_m = [i['s'] for i in items]
        res = dlg_menu(DMENU_LIST, items_m, caption='Scenes')
        if res is None: return

        y = items[res]['i']
        ed.set_caret(0, y, -1, -1)


    def on_complete(self, ed_self):

        carets = ed.get_carets()
        if len(carets)>1: return

        x, y, x1, y1 = carets[0]
        s = ed.get_text_line(y)
        len_rt = len(s)-x
        s = s[:x]

        ok, s = get_name_from(s)
        if not ok:
            print('Not a character: '+s)
            return

        names = self._find_all_names()
        #print('names', names)

        res = []
        for name in names:
            if name.startswith(s) and name!=s:
                res.append(name)
        #print('res', res)

        text = '\n'.join(['name|%s|'%name for name in res])
        ed.complete(text, len(s), len_rt, 0, False)
        return True


    def callback_list_click(self, id_dlg, id_ctl, data='', info=''):

        sel = listbox_proc(self.id_list, LISTBOX_GET_SEL)
        if sel is None: return
        item = listbox_proc(self.id_list, LISTBOX_GET_ITEM_PROP, index=sel)
        if item is None: return
        nline = item['tag']
        if nline<0: return

        file_open(self.filename)
        ed.set_caret(0, nline, -1, -1)


    def web_preview(self):

        do_preview()
