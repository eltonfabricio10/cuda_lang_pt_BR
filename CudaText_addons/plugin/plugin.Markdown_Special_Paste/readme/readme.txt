plugin for CudaText.
it handles "on_paste" event for lexers:
- Markdown
- reStructuredText
- MediaWiki
- AsciiDoc
- LaTeX

1) if clipboard contains text URL: 'http://' or 'https://'.
plugin changes text according to templates:

- for Markdown: [Text](url)
- for reStructuredText: `Text <url>`__
- for MediaWiki: [url Text]
- for AsciiDoc: url[title]
- for LaTeX: \href{url}{title}

2) if clipboard contains a picture.
plugin suggests to save the picture in the folder of the current file
(or the folder of the current Project Manager project, by option).
after that it inserts the link to this new file.

- for Markdown: '![alt text](filename.png "Title")
- for reStructuredText: .. image:: filename.png
- for MediaWiki: [[File:filename.png]]
- for AsciiDoc: image:filename.png[title="Title"]
- for LaTeX: \includegraphics[width=\linewidth]{filename.png}


how to temporary skip plugin work
---------------------------------

to skip plugin handling, call the Paste command with any hotkey
containing Shift, or call menu item Paste while holding Shift.
e.g. use Shift+Insert (standard second hotkey for Paste).
or use Ctrl+Shift+V, but first you need to assign Ctrl+Shift+V to "Paste"
(in the Command Palette dialog).


options
-------

config file "plugins.ini" can be opened via menu item:
  "Options / Settings-plugins / Markdown Special Paste / Config".

options in section [markdown_special_paste] are:

- "url_timeout" - Timeout in seconds, which it used on downloading webpage by its URL.

- "pic_name" - Initial suggested name for picture file.
    Can have macros:
    {now} - Current date/time formatted as yyyy-mm-dd-hh-mm-ss.
    {dirname} - Name of parent folder, without path.

- "pic_path" - Initial folder for picture file, when pasting picture.
    Can contain subfolders with separator "/", they will be auto-created.
    Option value must begin with one of macros:
    {filedir} - Folder of current editor file.
    {projdir} - Folder of currently opened CudaText project.
                If no project is opened, it's folder of current editor file.

- "pic_ext" - Image file extension without dot. Can be "png", "jpg", "jpeg".
              For other values (e.g. "gif") you will get the plugin error.

- "now" - Date/time format for {now} macro. See Python docs for strftime().


author: Alexey Torgashin
license: MIT
