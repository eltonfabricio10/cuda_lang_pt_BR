Plugin for CudaText.
Gives IntelliSense commands for AutoIt lexer.

1) Auto-completion (Ctrl+Space)
   Place caret after incomplete function/class/variable name, and press this hotkey.
2) Go to definition
   Place caret on name of func/class/variable/const, and call "Go to definition" menu item from editor context menu.
3) Show function call-tip (Ctrl+Shift+Space)
   Place caret after function name between () brackets, and press this hotkey.
4) Auto-insert args for function (Tab)
   Place caret after function name and press this hotkey. Or press this hotkey after Auto-completion.
5) Show function doc-string
   Shows doc-string for function/class under caret, in the Output panel. Call it from Commands dialog or from Plugins menu.

Plugin uses local copy of 'au3.api' file. You can download latest version this file from:
    https://www.autoitscript.com/autoit3/scite/download/au3.api
    
Plugin needs to know path to AutoIt installation, so you must call menu item in "Option / Settings-plugins / AutoIt Helper" to specify this path. Otherwise, IntelliSense doesn't work and gives error in Console panel.

Authors: OlehL, Tom Braider.
License: MIT
