# $Id$
#
# Copyright (C) 2003  Geoffrey T. Dairiki <dairiki@dairiki.org>
#
# This file is part of Pyxine, Python bindings for xine.
#
# Pyxine is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# Pyxine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from pyxine import libxine, constants, constwrap

class OsdColor:
    def __init__(self, color, trans):
        self.color, self.trans = color, trans
    def __repr__(self):
        return "<%s: (0x%06x, 0x%02x)>" % (self.__class__.__name__,
                                           self.color, self.trans)
    def __str__(self):
        return repr(self)

class Osd:
    def __init__(self, stream, width, height, x=0, y=0):
        self.this = libxine.xine_osd_new(stream.this, x, y, width, height)
        self.clear()
        self.set_font()
        self.set_text_palette(constants.XINE_TEXTPALETTE_WHITE_BLACK_TRANSPARENT)
        
    def __del__(self):
        self.hide()
        libxine.xine_osd_free(self.this)

    def set_position(self, x, y):
        libxine.xine_osd_set_position(self.this, x, y)
    def show(self, vpts=0):
        libxine.xine_osd_show(self.this, vpts)
    def hide(self, vpts=0):
        libxine.xine_osd_hide(self.this, vpts)

    def clear(self):
        libxine.xine_osd_clear(self.this)
        
    def draw_point(self, x, y, color):
        libxine.xine_osd_draw_point(self.this, x, y, color)
    def draw_line(self, x1, y1, x2, y2, color):
        libxine.xine_osd_draw_line(self.this, x1, y1, x2, y2, color)
    def draw_rect(self, x1, y1, x2, y2, color, filled=0):
        libxine.xine_osd_draw_rect(self.this, x1, y1, x2, y2, color, filled)

    def draw_text(self, x, y, text, color_base=constants.XINE_OSD_TEXT1):
        color_base = constwrap.XINE_OSD(color_base)
        libxine.xine_osd_draw_text(self.this, x, y, text, color_base)
    def set_font(self, fontname="sans", size=16):
        libxine.xine_osd_set_font(self.this, fontname, size)
    def get_text_size(self, text):
        return libxine.xine_osd_get_text_size(self.this, text)
    def set_text_palette(self,
                         palette_number=constants.XINE_TEXTPALETTE_WHITE_BLACK_TRANSPARENT,
                         color_base=constants.XINE_OSD_TEXT1):
        palette_number = constwrap.XINE_TEXTPALETTE(palette_number)
        color_base = constwrap.XINE_OSD(color_base)
        libxine.xine_osd_set_text_palette(self.this, palette_number, color_base)
        
    def get_palette(self):
        color, trans = libxine.xine_osd_get_palette(self.this)
        return map(OsdColor, color, trans)
    
    def set_palette(self, palette):
        assert palette.count() == 256
        color = map(lambda c: c.color, palette)
        trans = map(lambda c: c.trans, palette)
        libxine.xine_osd_set_palette(self.this, color, trans)

    def get_color(self, i):
        color, trans = libxine.xine_osd_get_palette(self.this)
        return OsdColor(color[i], trans[i])

    def set_color(self, i, val):
        color, trans = libxine.xine_osd_get_palette(self.this)
        color[i] = val.color
        trans[i] = val.trans
        libxine.xine_osd_set_palette(self.this, color, trans)
