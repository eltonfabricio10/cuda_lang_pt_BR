Plugin for CudaText.
Allows to convert text (selected block, or entire text if nothing selected) using many codings (transformations).

Codings:

- HTML entitize/deentitize: converts characters to their HTML entity (like "&nbsp;" for non-breakable space)
- XML entitize/deentitize: converts characters to their XML entity
- CSS escape/unescape
- Safe HTML entitize/deentitize: converts characters to their HTML entity, but preserves HTML reserved characters

- JSON escape: escapes a string and surrounds it in quotes, according to the JSON encoding
- JSON unescape: unescapes a string (including the quotes!) according to JSON encoding

- URL encode: uses 'urllib.quote' to escape special URL characters
- URL decode: uses 'urllib.unquote' to convert escaped URL characters

- Base64 encode/decode
- Base32 encode/decode
- Base16 encode/decode

- Quoted-printable: converts Unicode string to something like =D0=9F=D1=80=D0=BE
- Unicode-escape: converts Unicode string to something like \u041f\u0440\u043e

- MD5: creates MD5 hash
- SHA256: creates SHA256 hash
- SHA512: creates SHA512 hash

- Escape regex: escapes regular-expressions meta characters, e.g. $ to \$
- Escape %_: escapes SQL-LIKE meta characters

- Decimal to hexadecimal: converts decimal number to hex form (with 0x prefix)
- Hexadecimal to decimal: converts hex number (0x prefix is optional) to decimal form

- QWERTY layout English to Russian / Russian to English:
  converts wrongly typed text using Russian-keyboard layout, e.g. "ghbdtn" to "привет" 
  
- ROT13
- ROT18
- ROT47

- Unicode normalize (NFC, NFD, NFKC, NFKD): see description at
  https://en.wikipedia.org/wiki/Unicode_equivalence#Normal_forms


About
-----

Code was ported from Sublime Text plugin "StringEncode": https://github.com/colinta/SublimeStringEncode
Later more encodings were added by Alexey T., legacy Sublime-plugin-code was improved/changed.

Author: Alexey Torgashin (CudaText)
License: MIT
