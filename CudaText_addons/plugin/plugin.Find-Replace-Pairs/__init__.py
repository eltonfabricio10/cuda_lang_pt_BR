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
        json_fn = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_find_replace_pairs.json')

    def list(self):
        items, items_ = self.get_items()
        if len(items_) > 0:
            w, h = self.get_w_h()
            res = dlg_menu(DMENU_LIST, items, 0, _('Pairs of Find/Replace'), w = w, h = h)
            if res is not None:
                self.set_fr(items_[res])
        else:
            msg_box(_('No pairs found'), MB_OK)

    def add(self):
        f_, r_, rg_ = self.get_fr()
        data = self.load_json()
        found = False
        for dat in data:
            if f_ == dat['find'] and r_ == dat['replace'] and rg_ == dat['regex']:
                found = True
                break
        if not found:
            self.save_json({
                'find': f_,
                'replace': r_,
                'regex': rg_,
            })

    def remove(self):
        items, items_ = self.get_items()
        if len(items_) > 0:
            w, h = self.get_w_h()
            res = dlg_menu(DMENU_LIST, items, 0, _('Delete of pairs of Find/Replace'), w = w, h = h)
            if res is not None:
                res_ = msg_box(_('Do you really want to remove pair?'), MB_YESNO + MB_ICONQUESTION)
                if res_ == ID_YES:
                    data = self.load_json()
                    data.pop(res)
                    self.save_json(data, True)
        else:
            msg_box(_('No pairs found'), MB_OK)

    def load_json(self):
        data = ''
        if os.path.exists(json_fn):
            with open(json_fn, encoding = 'utf-8') as f:
                data = json.load(f)

        return data

    def save_json(self, json_data, update = False):
        if update:
            data = json_data
        else:
            data = self.load_json()
            if data:
                data.append(json_data)
            else:
                data = [json_data]
        with open(json_fn, mode = 'w', encoding = 'utf-8') as f:
            json.dump(data, f, indent = 2)

        msg_status(_('Pairs of Find/Replace updated'))

    def get_w_h(self):
        w_ = 600
        h_ = 600
        r = app_proc(PROC_COORD_MONITOR, 0)
        if r:
            w_ = (r[2] - r[0]) // 3
            h_ = (r[3] - r[1]) // 3

        return w_, h_

    def get_items(self):
        items = ''
        items_ = []
        data = self.load_json()
        if data:
            for i in data:
                j = json.loads(json.dumps(i))
                items_.append(j)
                if j['regex']:
                    items += '(*) '
                items += '[' + j['find'] + '] => [' + j['replace'] + ']' + "\n"
        else:
            msg_status(_('No pairs found'))

        return items, items_

    def get_fr_prop(self, prop):
        return app_proc(PROC_GET_FINDER_PROP, '').get(prop, [])

    def set_fr_prop(self, prop, val):
        return app_proc(PROC_SET_FINDER_PROP, {prop: val})

    def get_fr(self):
        ed.cmd(cmds.cmd_DialogReplace)
        fr_ = app_proc(PROC_GET_FINDER_PROP, '')
        f_ = fr_.get('find_d', [])
        r_ = fr_.get('rep_d' , [])
        rg_ = fr_.get('op_regex_d' , [])

        return f_, r_, rg_

    def set_fr(self, vals):
        ed.cmd(cmds.cmd_DialogReplace)
        app_proc(PROC_SET_FINDER_PROP, dict(
            find_d = vals['find'],
            rep_d = vals['replace'],
            op_regex_d = vals['regex'],
            focus = 'edFind'
        ))

    def set_fr_r(self):
        if self.get_fr_prop('is_replace'):
            f_ = self.get_fr_prop('find_d')
            rg_ = self.get_fr_prop('op_regex_d')
            items, items_ = self.get_items()
            res = []
            if len(items_) > 0:
                for i in items_:
                    if i['find'] == f_ and i['regex'] == rg_:
                        res.append(i['replace'])

            if len(res) == 1:
                self.set_fr_prop('rep_d', res[0])
            else:
                self.h_menu = menu_proc(0, MENU_CREATE)
                menu_proc(self.h_menu, MENU_CLEAR)
                for j in res:
                    menu_proc(self.h_menu, MENU_ADD, caption = j, command='module=cuda_find_replace_pairs;cmd=set_fr_r_index;info={};'.format(j))
                menu_proc(self.h_menu, MENU_SHOW)

    def set_fr_r_index(self, info = None):
        self.set_fr_prop('rep_d', info)

    def on_state_findbar(self, ed_self, state, value):
        if state == 'cmd' and value in ('Rep', 'RepAll', 'RepStop', 'RepGlobal'):
            self.add()
        elif state == 'is_rep' or (state == 'opt' and value == 'RegEx') or state == 'focus':
            self.set_fr_r()