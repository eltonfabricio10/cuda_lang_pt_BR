import codecs

def rot13(s):
    return codecs.encode(s, 'rot_13')

def rot47(s):
    r = ''
    for ch in s:
        n = ord(ch)
        if 33 <= n <= 126:
            r += chr(33 + ((n + 14) % 94))
        else:
            r += ch
    return r

def rot18(s):
    chars = "5678901234"
    r = list(s)
    for i, ch in enumerate(r):
        if ch.isdigit():
            r[i] = chars[ord(ch)-48]
    return rot13(''.join(r))
