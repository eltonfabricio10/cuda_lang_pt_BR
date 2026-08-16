import os
from cudatext import *
import cudatext_cmd as cmds

try:
    from .pyads import ADS
except:
    ADS = None
    msg_box('NTFS Streams plugin requires Windows', MB_OK+MB_ICONERROR)


def ask_new_stream_name(st, filename):
    while True:
        s = dlg_input('Add stream in "%s":' % os.path.basename(filename), '')
        if not s: return
        if s in st.streams:
            msg_box('Stream name "%s" already exists'%s, MB_OK+MB_ICONWARNING)
        else:
            return s


class Command:

    def dialog(self):
        self._dialog(ed.get_filename())

    def dialog_any(self):
        fn = dlg_file(True, '', '', '')
        if not fn: return
        self._dialog(fn)

    def _dialog(self, fn):
        if not ADS: return
        if not fn:
            msg_status('NTFS Streams: need named file')
            return

        #handle filename with stream already
        if ':' in os.path.basename(fn):
            n = fn.rfind(':')
            fn = fn[:n]

        st = ADS(fn)

        ITEMS_TOP = [
            'Open stream (%d items)...'% len(st.streams),
            'Add empty stream...',
            'Add stream from file...',
            'Delete stream...'
            ]

        res = dlg_menu(DMENU_LIST, ITEMS_TOP, caption='Streams: '+os.path.basename(fn))
        if res is None: return

        if res==0: # open stream
            items = st.streams
            if not items:
                msg_status('No streams')
                return
            res = dlg_menu(DMENU_LIST, items, caption='Open stream in '+os.path.basename(fn))
            if res is None: return
            res = items[res]

            file_open(st.full_filename(res))

        if res==1: #add empty
            str_name = ask_new_stream_name(st, fn)
            if not str_name: return

            try:
                st.add_stream_from_file(None, str_name)
                msg_status('Stream added: '+str_name)
            except Exception as e:
                msg_box(str(e), MB_OK+MB_ICONERROR)

        if res==2: #add from file
            filename = dlg_file(True, '', '', '')
            if not filename: return

            tt = ADS(filename)
            if tt.has_streams():
                res = dlg_menu(DMENU_LIST, tt.streams+['(unnamed)'], caption='Select stream from source file')
                if res is None: return
                if res<len(tt.streams):
                    filename = tt.full_filename(tt.streams[res])

            str_name = ask_new_stream_name(st, fn)
            if not str_name: return

            try:
                st.add_stream_from_file(filename, str_name)
                msg_status('Stream added from file: '+os.path.basename(filename))
            except Exception as e:
                msg_box(str(e), MB_OK+MB_ICONERROR)

        if res==3: #delete stream
            if not st.has_streams():
                msg_status('No streams')
                return
            str_name = dlg_menu(DMENU_LIST, st.streams, caption='Delete stream')
            if str_name is None: return
            str_name = st.streams[str_name]

            #confirm
            if msg_box('Do you want to delete stream "%s" in file "%s"? This cannot be undone.' 
              % (str_name, os.path.basename(fn)), MB_OK+MB_ICONQUESTION) != ID_OK: return

            #close tab of deleted stream
            prev_name = st.full_filename(str_name)
            for h in ed_handles():
                e = Editor(h)
                if e.get_filename().lower() == prev_name.lower():
                    e.focus()
                    e.cmd(cmds.cmd_FileClose)

            try:
                st.delete_stream(str_name)
                msg_status('Stream deleted: '+str_name)
            except Exception as e:
                msg_box(str(e), MB_OK+MB_ICONERROR)


