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

TOP	  = .

# FIXME
PYXINE_VERSION = 0.1alpha1

SUBDIRS	  = pxlib pyxine test examples
GEN_FILES = setup.py MANIFEST

DIST_FILES= $(GEN_FILES)
DIST_FILES+= Makefile common.mak LICENSE README TODO HINTS
DIST_FILES+= setup.py.in setup.cfg get-python-defs

CLEAN_FILES = python-defs.mak

DISTNAME  = pyxine-$(PYXINE_VERSION)
DISTDIR	  = $(DISTNAME)
TAR_DIST  = $(DISTNAME).tar.gz

PYSETUP	  = $(PYTHON) setup.py

-include $(TOP)/common.mak

default	: setup.py
dist	: sdist

install	build sdist bdist bdist_rpm : setup.py
	$(PYSETUP) $@

sdist bdist bdist_rpm : distfiles

MANIFEST: $(addsuffix /Makefile, $(SUBDIRS))
	@echo "Generating MANIFEST"
	@$(MAKE) _subdir="" _buildmanifest 3>$@

PXLIB_SRC	= $(shell grep 'pxlib/.*\.cc$$' MANIFEST)
LIBXINE_SRC	= $(shell grep 'pyxine/.*\.c$$' MANIFEST)
XINE_LIBS	= $(shell xine-config --libs | tr ' ' '\n' | sed -n 's/^-l//p')
XINE_LIBPATH	= $(shell xine-config --libs | tr ' ' '\n' | sed -n 's/^-L//p')

setup.py: setup.py.in MANIFEST
	@echo "Generating setup.py"
	@sed 's:%PXLIB_SRC%:$(PXLIB_SRC):; \
	      s:%LIBXINE_SRC%:$(LIBXINE_SRC):; \
	      s:%XINE_LIBPATH%:$(XINE_LIBPATH):; \
	      s:%XINE_LIBS%:$(XINE_LIBS):; \
	      s:%PYXINE_VERSION%:$(PYXINE_VERSION):;' \
	  $< > $@



.PHONY: pyclean pyclean-all
pyclean:
	-$(PYSETUP) clean
pyclean-all:
	-$(PYSETUP) clean --all
clean	: pyclean
distclean : pyclean-all
maintainer-clean : pyclean-all
