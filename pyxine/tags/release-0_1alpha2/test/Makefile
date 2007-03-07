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

TOP	= ..

PYSOURCE  = pxtest.py
PYSOURCE += constants_test.py constwrap_test.py cstruct_test.py event_test.py
PYSOURCE += post_test.py swig_test.py weakmethod_test.py xine_test.py

TESTSOURCE = wonderful_strange.wav
TESTINPUTS = $(TESTSOURCE:.wav=.mp3)

GEN_FILES  = $(TESTINPUTS)
DIST_FILES = Makefile CREDITS
DIST_FILES += $(PYSOURCE) $(TESTSOURCE) $(TESTINPUTS)

include $(TOP)/common.mak

all:

check: all blib-top 
	PYTHONPATH=$(blibdir) $(PYTHON) pxtest.py 2>&1 >/dev/null

.PHONY: blib-top
blib-top:
	$(MAKE) -C $(TOP) blib

# Test sound file from
# http://www.wavsource.com/tv/tv06.htm#twin
wonderful_strange.mp3: wonderful_strange.wav
	lame --mp1input -h --resample 44.1 --lowpass 5.0 -b 32 -S \
	        --tt "Wonderful and Strange" \
	 	--tl "Twin Peaks"  --tg "Sound Clip" \
	    $< $@
