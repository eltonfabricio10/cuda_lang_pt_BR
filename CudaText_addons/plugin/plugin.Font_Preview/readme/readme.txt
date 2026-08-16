Plugin for CudaText.
Shows html-preview of font-file (default-ext: ttf, woff, eot, otf, ttc) in WebBrowser.

How to use
----------
1) Open font-file in CudaText
2) Switch to default-WebBrowser where opened new tab with html-preview of font.

Configuration
-------------
Menu item "Options / Settings-plugins / Font Preview / Config".

Options in the settings/plugins.ini file, in [font_preview], are:
- "file_exts": file-extensions that the plugin will open
- "tpl_fn": file-template for html-preview (base file-name in plugin dir, ex. template.html): lowercase, uppercase and fish-text with delimiters "|".
- "ft": fish-text
- "ft_loc": local fish-text

Author:
  ildar r. khasanshin (@ildarkhasanshin at GitHub)
License: MIT