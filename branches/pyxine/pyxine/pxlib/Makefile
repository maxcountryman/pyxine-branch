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

CCFILES   = Mutex.cc Thread.cc XDisplay.cc Traits.cc
CCFILES  += Callback.cc Geometry.cc WindowList.cc
CCFILES	 += PxWindow.cc
HFILES    = pxlib.h $(CCFILES:.cc=.h)
GEN_FILES = pxlib.py pxlib_wrap.cc

DIST_FILES= Makefile pxlib.i $(CCFILES) $(HFILES) $(GEN_FILES)

OFILES	  = pxlib_wrap.o $(CCFILES:.cc=.o)
SOFILES	  = pxlibc$(SO)
BLIB_FILES= $(SOFILES)

include $(TOP)/common.mak

LIBS	 += -lstdc++

pxlibc$(SO): $(OFILES)
	$(LDSHARED) $^ $(LIBS) -o $@

pxlib.py pxlib_wrap.cc: pxlib.i PxWindow.h
	$(SWIG) -python -c++ -shadow -dnone -o pxlib_wrap.cc pxlib.i
