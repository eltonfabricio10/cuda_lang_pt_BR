CSS Inspector plugin for CudaText.
In HTML documents (with lexer "HTML") it shows CSS properties of current tag under caret.
To call plugin, use menu item "Plugins / CSS Inspector", it will show side panel with "CSS" icon.
When you move caret in editor, this panel updates its info.

It calculates tag properties given by: 
- class
- id
- "style" tag
Properties can be set:
- straight in HTML by using "style" tag
- in the CSS file, and connected by the "link" tag


Installation on Linux and Unix'es
---------------------------------

Plugin needs additional Python libraries, install them like this:

$ pip3 install lxml
$ pip3 install cssselect


Installation on Windows
-----------------------

Plugin needs additional libraries.
a) "cssselect" from https://pypi.org/project/cssselect/#files
Get the .whl file, it is the ZIP archive. Unzip the folder "cssselect" to [CudaText]/py folder.
You must have [CudaText]/py/cssselect/__init__.py file.

b) "lxml" from https://pypi.org/project/lxml/#files
Get the .whl file, it is the ZIP archive. Unzip the folder "lxml" to [CudaText]/py folder.
You must have [CudaText]/py/lxml/__init__.py file.
Get the package according to your CudaText bitness (32- or 64-bit) and to Python version
(3.8 is the default for CudaText). For example, for 64-bit and Python 3.8 you need
"lxml-x.x.x-cp38-cp38-win_amd64.whl".


About
-----

Authors:
- @Medvosa at GitHub
- Alexey Torgashin (CudaText)
License: MIT
