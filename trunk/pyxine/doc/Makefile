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

TOP	  = ..

GEN_FILES = README.html

DIST_FILES= $(GEN_FILES)
DIST_FILES+= Makefile default.css

# Program to convertion from prStucturedDocumentation to HTML.
# See http://docutils.sf.net/
DOCUTILS_HTML = html.py
STYLESHEET = pyxine.css

VPATH = $(TOP)

%.html : %
	$(DOCUTILS_HTML) --stylesheet="$(STYLESHEET)" $< > $@

-include $(TOP)/common.mak
