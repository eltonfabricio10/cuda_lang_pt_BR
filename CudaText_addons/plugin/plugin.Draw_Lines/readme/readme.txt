plugin for CudaText.
allows to draw preudo-graphic frames in text, using Unicode "box" chars,
which were available in DOS codepage ages ago.

example of frames:
       ╒════╦═╗
       │   ╔╬═╬╤═╤═════╗
   ╒═╕ │   ╠╩╤╩╧═╧─┬─┐ ║
   └─┴─┤ ┌┬╨─┤    ┌┼─┼─╜
  ╙────┴─┴┴──┴────┴┴─┘

activate/deactivate plugin using menu item: Plugins - Draw Lines.
when active, plugin allows single/double line modes, toggle this by F9 
(no command in plugin, just a hotkey).
use Shift+arrows to draw line, single or double, in any of 4 directions:
up/down/left/right. line intersections are handled, so some chars will
be "crosses" or "angles" when you intersect other lines.

plugin subscribes to editor event only after call, so doesn't slow down
usual work.

author: Alexey (CudaText)
license: MIT
