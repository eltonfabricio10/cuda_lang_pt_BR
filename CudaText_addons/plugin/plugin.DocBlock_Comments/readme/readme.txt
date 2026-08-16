Plugin for CudaText.
It helps to enter DocBlock comments for lexers: PHP, JavaScript, CoffeeScript.
DocBlock comments in these lexers are:

  /**
   * Some text
   * @tag text
   * @tag text
   * @tag text
   */

Plugin should not slow down editing, it is activated only a) on pressing Enter,
b) or calling "auto-completion" command. And only in few supported lexers.


1) It handles Enter key press.
It looks, if end of the current line is "/**", if so then empty docblock is entered
and caret placed in it. 
If you press Enter in the middle of docblock, ie beginning of the current line
is indent + "* ", plugin adds "* " on new line too.

2) It supports auto-completion for standard 'tags' in docblocks.
Inside docblock type "@" and press call "auto-completion" (Ctrl+Space),
plugin will suggest menu with JSDoc/PHPDoc tags. 


Author: Alexey Torgashin (CudaText)
License: MIT
