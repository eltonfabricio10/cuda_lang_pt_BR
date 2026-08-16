import os
from cudatext import *
import cudatext as ct
import cudatext_cmd as cmds
import json

from cudax_lib import get_translation
_ = get_translation(__file__)

class Command:

    def __init__(self):
        global json_fn
        json_fn = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_find_replace_3rd_history.json')
        if not os.path.exists(json_fn):
            with open(json_fn, mode = 'w', encoding = 'utf-8') as f:
                json.dump({'find_replace': [{'find': '[A-Z0-9._%+-]+@[A-Z0-9-]+.+.[A-Z]{2,4}', 'regex': True}], 'find': self.get_fr_prop('find_h')}, f, indent = 2)

    def add_fr(self):
        key = 'find_replace'
        f_ = self.get_fr_prop('find_d')
        rg_ = self.get_fr_prop('op_regex_d')
        if f_:
            data = self.load_json()
            found = False
            for dat in data[key]:
                if f_ == dat['find'] and rg_ == dat['regex']:
                    found = True
                    break
            if not found:
                self.save_json(key, {'find': f_, 'regex': rg_})

    def add_f(self):
        key = 'find'
        f_ = self.get_fr_prop('find_d')
        if f_:
            data = self.load_json()
            if f_ in data[key]:
                data[key].pop(data[key].index(f_))
            data[key].insert(0, f_)
            self.save_json(key, data[key], True)

    def remove(self):
        key = 'find_replace'
        items, items_ = self.get_items()
        if len(items_) > 0:
            w, h = self.get_w_h()
            res = dlg_menu(DMENU_LIST, items, 0, _('Remove find-results for replacement'), w = w, h = h)
            if res is not None:
                res_ = msg_box(_('Do you really want to remove find-result?'), MB_YESNO + MB_ICONQUESTION)
                if res_ == ID_YES:
                    data = self.load_json()
                    data[key].pop(res)
                    self.save_json(key, data[key], True)
        else:
            msg_box(_('No found find-results for replacement'), MB_OK)

    def load_json(self):
        with open(json_fn, encoding = 'utf-8') as f:
            data = json.load(f)

        return data

    def save_json(self, key, json_data, replace = False):
        data = self.load_json()
        if replace:
            data[key] = json_data
        else:
            data[key].append(json_data)
        with open(json_fn, mode = 'w', encoding = 'utf-8') as f:
            json.dump(data, f, indent = 2)
        msg_status(_('Find-results for replacement updated'))

    def get_w_h(self):
        w_ = 600
        h_ = 600
        r = app_proc(PROC_COORD_MONITOR, 0)
        if r:
            w_ = (r[2] - r[0]) // 3
            h_ = (r[3] - r[1]) // 3

        return w_, h_

    def get_items(self):
        key = 'find_replace'
        items = ''
        items_ = []
        data = self.load_json()
        if data[key]:
            for i in data[key]:
                j = json.loads(json.dumps(i))
                items_.append(j)
                if j['regex']:
                    items += '(*) '
                items += '[' + j['find'] + ']' + "\n"
        else:
            msg_status(_('No found find-results for replacement'))

        return items, items_

    def get_fr_prop(self, prop):
        return app_proc(PROC_GET_FINDER_PROP, '').get(prop, [])

    def set_fr_h(self):
        if self.get_fr_prop('is_replace'):
            regex = self.get_fr_prop('op_regex_d')
            items, items_ = self.get_items()
            f_h = []
            for item in items_:
                if regex:
                    if item['regex']:
                        f_h.append(item['find'])
                else:
                    if not item['regex']:
                        f_h.append(item['find'])
        else:
            data = self.load_json()
            f_h = data['find']

        app_proc(PROC_SET_FINDER_PROP, dict(find_h = f_h))

    def clear_fr(self):
        keys = ['find_replace', 'find']
        for key in keys:
            self.save_json(key, [], True)

        msg_status(_('History of find-replace cleaned'))

    def on_state_findbar(self, ed_self, state, value):
        if state == 'cmd':
            if value in ('FindNext', 'FindPrev', 'FindFirst'):
                if self.get_fr_prop('is_replace'):
                    self.add_fr()
                else:
                    self.add_f()
            elif value in ('Rep', 'RepAll', 'RepStop', 'RepGlobal'):
                self.add_fr()
        elif state == 'is_rep' or (state == 'opt' and value == 'RegEx') or (state == 'focus' and value == 'edFind'):
            self.set_fr_h()

    def on_state(self, ed_self, state):
        if state == APPSTATE_CLEAR_HISTORY_FINDER:
            self.clear_fr()
