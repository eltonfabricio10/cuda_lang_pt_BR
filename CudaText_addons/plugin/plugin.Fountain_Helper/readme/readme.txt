plugin for CudaText.
it gives features for Fountain lexer:

- event on pressing Shift+Enter: it converts cur line to upper-case and makes a new-line.
- auto-completion list of names, when calling completions (Ctrl+Space) after partial character name.

and commands in "Plugins - Fountain Helper":

- "Character list" 
it finds all character names in cur file, then asks for a name. for entered name, it find all its places and gives menu with these places, to go there. brackets at the end, e.g. "Edward (V.O.)", are stripped. @name and name^ are handled.

- "Character under caret"
it takes name, on separate line, under caret, and shows the dialog like before for this name.

- "Scene list"
it shows list of all scenes, to jump to selected scene. it is the same as using CudaText tree panel on the left, but note: code to find scenes is different, than lexer has for the tree panel.

- "Extract talks of character"
it asks for a name, then finds all talks of that name. talks are collected in a new editor tab, separated by empty lines. 

- "Preview in browser"
it converts current document to HTML (in a temporary folder) and opens HTML file in browser.
this command requires Node.js installed!
it uses parser from: https://github.com/nathanhoad/fountain-js


author: Alexey Torgashin (CudaText)
license: MIT
