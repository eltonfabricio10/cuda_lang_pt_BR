Plugin for CudaText
It reads current selection (only 1 caret allowed) and converts it to JavaScript array of string,
with "join". Example of result:

['dddd',
'ddddddddd',
'aaaa'].join('\n');

You can a) replace selection with JS code, b) copy JS code to clipboard.
Commands are in Plugins menu.

Converter code (few lines) from https://github.com/metatribal/sublime-jsmultiline
License for this plugin: Apache 2.0 or MIT
Author: Alexey T. (CudaText)
