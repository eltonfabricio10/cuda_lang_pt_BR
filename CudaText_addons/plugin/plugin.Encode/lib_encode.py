# coding: utf-8
import sys
import base64
import quopri
import re
import json
import hashlib
import urllib.parse
from .escape_table import *

ENC = 'utf8' 


def decode_num_entities(text, dec, hexa):
    if dec:
        # Decode decimal entities: &#39;
        text = re.sub(
            r'&#([0-9]+);',
            lambda m: chr(int(m.group(1))),
            text
        )

    if hexa:
        # Decode hexadecimal entities: &#x27; or &#X27;
        text = re.sub(
            r'&#[xX]([0-9A-Fa-f]+);',
            lambda m: chr(int(m.group(1), 16)),
            text
        )

    return text


class StringEncode():
    pass

class HtmlEntitizeCommand(StringEncode):

    def encode(self, text):
        text = text.replace('&', '&amp;')
        for k in html_escape_table:
            v = html_escape_table[k]
            text = text.replace(k, v)
        ret = ''
        for i, c in enumerate(text):
            if ord(c) > 127:
                ret += hex(ord(c)).replace('0x', '&#x') + ';'
            else:
                ret += c
        return ret


class HtmlDeentitizeCommand(StringEncode):

    def encode(self, text):
        # Reverse lookup for named entities
        for k, v in html_escape_table.items():
            text = text.replace(v, k)

        text = decode_num_entities(text, True, True)

        # Decode &amp; last, to avoid double decoding
        text = text.replace('&amp;', '&')

        return text


class CssEscapeCommand(StringEncode):

    def encode(self, text):
        ret = ''
        for i, c in enumerate(text):
            if ord(c) > 127:
                ret += hex(ord(c)).replace('0x', '\\')
            else:
                ret += c
        return ret


class CssUnescapeCommand(StringEncode):

    def encode(self, text):
        while re.search(r'\\[a-fA-F0-9]+', text):
            match = re.search(r'\\([a-fA-F0-9]+)', text)
            text = text.replace(
                match.group(0), chr(int('0x' + match.group(1), 16)))
        return text


class SafeHtmlEntitizeCommand(StringEncode):

    def encode(self, text):
        for k in html_escape_table:
            # skip HTML reserved characters
            if k in html_reserved_list:
                continue
            v = html_escape_table[k]
            text = text.replace(k, v)
        ret = ''
        for i, c in enumerate(text):
            if ord(c) > 127:
                ret += hex(ord(c)).replace('0x', '&#x') + ';'
            else:
                ret += c
        return ret


class SafeHtmlDeentitizeCommand(StringEncode):

    def encode(self, text):
        for k in html_escape_table:
            # skip HTML reserved characters
            if k in html_reserved_list:
                continue
            v = html_escape_table[k]
            text = text.replace(v, k)

        text = decode_num_entities(text, False, True) # dec=False since original Sublime plugin had not dec-decoding, only hex

        text = text.replace('&amp;', '&')
        return text


class XmlEntitizeCommand(StringEncode):

    def encode(self, text):
        text = text.replace('&', '&amp;')
        for k in xml_escape_table:
            v = xml_escape_table[k]
            text = text.replace(k, v)
        ret = ''
        for i, c in enumerate(text):
            if ord(c) > 127:
                ret += hex(ord(c)).replace('0x', '&#x') + ';'
            else:
                ret += c
        return ret


class XmlDeentitizeCommand(StringEncode):

    def encode(self, text):
        for k in xml_escape_table:
            v = xml_escape_table[k]
            text = text.replace(v, k)

        text = decode_num_entities(text, True, True)

        text = text.replace('&amp;', '&')
        return text


class JsonEscapeCommand(StringEncode):

    def encode(self, text):
        return json.dumps(text)


class JsonUnescapeCommand(StringEncode):

    def encode(self, text):
        return json.loads(text)


class UrlEncodeCommand(StringEncode):
    '''
    URL Encode: as in Notepad++, basically encodes all non-reserved chars (think of this regex: [a-zA-Z0-9._-] ie. alphanumerics, dot, underscore and dash) with a few exceptions $+!*'(),
    '''
    def encode(self, text):
        quoted = urllib.parse.quote(text, safe='$+!*\'(),')
        return quoted

class UrlEncode2Command(StringEncode):
    '''
    URL Encode Unrestricted: encodes even the exceptions above (like +), while still preserving alphanumerics, dot, underscore and dash.
    '''
    def encode(self, text):
        quoted = urllib.parse.quote(text, safe='')
        return quoted

class UrlEncode3Command(StringEncode):
    '''
    URL Encode Everything: as in Notepad++, encodes absolutely everything including letters
    '''
    def encode(self, text):
        quoted = "".join(f"%{byte:02X}" for byte in text.encode("utf-8"))
        return quoted


class UrlDecodeCommand(StringEncode):

    def encode(self, text):
        # unquote_plus is not ok, user requested to always keep '+' char
        return urllib.parse.unquote(text)


class Base64EncodeCommand(StringEncode):

    def encode(self, text):
        return base64.b64encode(bytes(text, ENC)).decode(ENC)


class Base64DecodeCommand(StringEncode):

    def encode(self, text):
        return base64.b64decode(bytes(text, ENC)).decode(ENC)
        

class Base32EncodeCommand(StringEncode):

    def encode(self, text):
        return base64.b32encode(bytes(text, ENC)).decode(ENC)

class Base32DecodeCommand(StringEncode):

    def encode(self, text):
        return base64.b32decode(bytes(text, ENC)).decode(ENC)


class Base16EncodeCommand(StringEncode):

    def encode(self, text):
        return base64.b16encode(bytes(text, ENC)).decode(ENC)
        
class Base16DecodeCommand(StringEncode):

    def encode(self, text):
        return base64.b16decode(bytes(text, ENC)).decode(ENC)


class QuoPriEncodeCommand(StringEncode):

    def encode(self, text):
        return quopri.encodestring(bytes(text, ENC)).decode(ENC)

class QuoPriDecodeCommand(StringEncode):

    def encode(self, text):
        return quopri.decodestring(bytes(text, ENC)).decode(ENC)


class UnicodeEscapeEncodeCommand(StringEncode):

    def encode(self, text):
        return bytes(text, 'unicode-escape').decode(ENC)

class UnicodeEscapeDecodeCommand(StringEncode):

    def encode(self, text):
        return bytes(text, ENC).decode('unicode-escape')
        


class Md5EncodeCommand(StringEncode):

    def encode(self, text):
        hasher = hashlib.md5()
        hasher.update(bytes(text, 'utf-8'))
        return hasher.hexdigest()


class Sha256EncodeCommand(StringEncode):

    def encode(self, text):
        hasher = hashlib.sha256()
        hasher.update(bytes(text, 'utf-8'))
        return hasher.hexdigest()


class Sha512EncodeCommand(StringEncode):

    def encode(self, text):
        hasher = hashlib.sha512()
        hasher.update(bytes(text, 'utf-8'))
        return hasher.hexdigest()


class Escaper(StringEncode):

    def encode(self, text):
        return re.sub(r'(?<!\\)(%s)' % self.meta, r'\\\1', text)


class EscapeRegexCommand(Escaper):
    meta = r'[\\*.+^$()\[\]\{\}]'


class EscapeLikeCommand(Escaper):
    meta = r'[%_]'


class HexDecCommand(StringEncode):

    def encode(self, text):
        return str(int(text, 16))


class DecHexCommand(StringEncode):

    def encode(self, text):
        return hex(int(text))


class UnicodeHexCommand(StringEncode):

    def encode(self, text):
        hex_text = u''
        text_bytes = bytes(text, 'utf-16')

        if text_bytes[0:2] == b'\xff\xfe':
            endian = 'little'
            text_bytes = text_bytes[2:]
        elif text_bytes[0:2] == b'\xfe\xff':
            endian = 'big'
            text_bytes = text_bytes[2:]

        char_index = 0
        for c in text_bytes:
            if char_index == 0:
                c1 = c
                char_index += 1
            elif char_index == 1:
                c2 = c
                if endian == 'little':
                    c1, c2 = c2, c1
                tmp = (c1 << 8) + c2
                if tmp < 0x80:
                    hex_text += chr(tmp)
                    char_index = 0
                elif tmp >= 0xd800 and tmp <= 0xdbff:
                    char_index += 1
                else:
                    hex_text += '\\u' + '{0:04x}'.format(tmp)
                    char_index = 0
            elif char_index == 2:
                c3 = c
                char_index += 1
            elif char_index == 3:
                c4 = c
                if endian == 'little':
                    c3, c4 = c4, c3
                tmp1 = ((c1 << 8) + c2) - 0xd800
                tmp2 = ((c3 << 8) + c4) - 0xdc00
                tmp = (tmp1 * 0x400) + tmp2 + 0x10000
                hex_text += '\\U' + '{0:08x}'.format(tmp)
                char_index = 0
        return hex_text


class HexUnicodeCommand(StringEncode):

    def encode(self, text):
        uni_text = text

        endian = sys.byteorder

        r = re.compile(r'\\u([0-9a-fA-F]{2})([0-9a-fA-F]{2})')
        rr = r.search(uni_text)
        while rr:
            first_byte = int(rr.group(1), 16)

            if first_byte >= 0xd8 and first_byte <= 0xdf:
                # Surrogate pair
                pass
            else:
                if endian == 'little':
                    b1 = int(rr.group(2), 16)
                    b2 = int(rr.group(1), 16)
                else:
                    b1 = int(rr.group(1), 16)
                    b2 = int(rr.group(2), 16)

                ch = bytes([b1, b2]).decode('utf-16')

                uni_text = uni_text.replace(rr.group(0), ch)
            rr = r.search(uni_text, rr.start(0) + 1)

        # Surrogate pair (2 bytes + 2 bytes)
        r = re.compile(
            r'\\u([0-9a-fA-F]{2})([0-9a-fA-F]{2})\\u([0-9a-fA-F]{2})([0-9a-fA-F]{2})')
        rr = r.search(uni_text)
        while rr:
            if endian == 'little':
                b1 = int(rr.group(2), 16)
                b2 = int(rr.group(1), 16)
                b3 = int(rr.group(4), 16)
                b4 = int(rr.group(3), 16)
            else:
                b1 = int(rr.group(1), 16)
                b2 = int(rr.group(2), 16)
                b3 = int(rr.group(3), 16)
                b4 = int(rr.group(4), 16)

            ch = bytes([b1, b2, b3, b4]).decode('utf-16')

            uni_text = uni_text.replace(rr.group(0), ch)
            rr = r.search(uni_text)

        # Surrogate pair (4 bytes)
        r = re.compile(
            r'\\U([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})')
        rr = r.search(uni_text)
        while rr:
            tmp = (int(rr.group(1), 16) << 24) \
                + (int(rr.group(2), 16) << 16) \
                + (int(rr.group(3), 16) <<  8) \
                + (int(rr.group(4), 16))

            if (tmp <= 0xffff):
                ch = chr(tmp)
            else:
                tmp -= 0x10000
                c1 = 0xd800 + int(tmp / 0x400)
                c2 = 0xdc00 + int(tmp % 0x400)
                if endian == 'little':
                    b1 = c1 & 0xff
                    b2 = c1 >> 8
                    b3 = c2 & 0xff
                    b4 = c2 >> 8
                else:
                    b1 = c1 >> 8
                    b2 = c1 & 0xff
                    b3 = c2 >> 8
                    b4 = c2 & 0xff

                ch = bytes([b1, b2, b3, b4]).decode('utf-16')

            uni_text = uni_text.replace(rr.group(0), ch)
            rr = r.search(uni_text)

        return uni_text
