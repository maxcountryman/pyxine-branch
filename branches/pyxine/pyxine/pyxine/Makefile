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

PACKAGE	  = pyxine

PYSOURCE  = config.py constants.py constwrap.py cstruct.py
PYSOURCE += event.py __init__.py osd.py post.py
PYSOURCE += weakmethod.py x11.py xine.py

GEN_FILES = libxine_wrap.c pxlib.py
DIST_FILES= Makefile libxine.i fixed_xine.h xine.h.orig
DIST_FILES+= $(GEN_FILES) $(PYSOURCE)

OFILES	  = libxine_wrap.o
SOFILES	  = libxine$(SO)
PYFILES	  = $(PYSOURCE) pxlib.py
BLIB_FILES= $(SOFILES) $(PYFILES)

include $(TOP)/common.mak

libxine$(SO): $(OFILES)
	$(LDSHARED) $^ $(LIBS) -o $@

libxine_wrap.c: libxine.i fixed_xine.h
	$(SWIG) -python -dnone libxine.i

pxlib.py: $(TOP)/pxlib/pxlib.py
	cp -p $< $@
.PHONY: force
$(TOP)/pxlib/pxlib.py: force
	make -C $(TOP)/pxlib pxlib.py



