
def is_scene(s):
    if not s:
        return False
    if s.startswith('.') and len(s)>1 and s[1].isalnum():
        return True
    s_ = s.upper()
    for prefix in ['EXT ', 'EXT.', 'INT ', 'INT.', 'INT/', 'EST ', 'EST.', 'ESTABLISHING', 'I/E', 'I./E.']:
        if s_.startswith(prefix):
            return True
    return False


def get_name_from(s):
    """
    Extraxt name from line, strip () and @ and ^
    """
    if is_scene(s):
        return (False, '')

    n = s.find('(')
    if n>=0:
        s = s[:n]

    if s.endswith('^'):
        s = s[:-1]

    ok = False
    if s.startswith('@'):
        s = s[1:]
        ok = True
    elif s.isupper():
        ok = True

    return (ok, s.strip())


def find_scenes(lines):
    res = []
    for (i, s) in enumerate(lines):
        if is_scene(s):
            res.append({'i': i, 's': s})
    return res


def find_names(lines):
    res = []
    for (i, s) in enumerate(lines):
        if not s: continue
        if i==0 or i==len(lines)-1: continue

        #name is after empty line, next line is not empty
        ok = lines[i-1]=='' and lines[i+1]!=''
        if not ok: continue

        ok, s = get_name_from(s)
        if ok:
            text = lines[i+1]
            if text.startswith('(') and i+2<len(lines):
                text = lines[i+2]
            res.append({'name': s, 'i': i, 'text': text})
    return res
