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

.PHONY: default all check dist install blib distfiles

default:
	@echo "If you just want to build and install pyxine, you should"
	@echo "probably do so using the supplied setup.py script."
	@echo ""
	@echo "Try something like:"
	@echo ""
	@echo "    python setup.py build"
	@echo "    python setup.py install"
	@echo ""
	@echo "For more in-depth hacking:"
	@echo ""
	@echo "    make all   -- to compile extension modules"
	@echo "    make check -- to run tests"
	@echo ""
	@echo "See README for more."

# Variables to extract from /usr/lib/python2.2/config/Makefile
PYTHON_DEFS  = PYTHON CC CXX OPT INCLUDEPY
PYTHON_DEFS += BLDSHARED CCSHARED SO
PYTHON_DEFS += INSTALL INSTALL_DATA INSTALL_SHARED

$(TOP)/python-defs.mak: $(TOP)/common.mak
	$(TOP)/get-python-defs $(PYTHON_DEFS) > $@

# Don't need python defs (& C/C++ dependencies unless compiling.
_GOALS	  = $(if $(MAKECMDGOALS), $(MAKECMDGOALS), default)

ifneq (,$(filter-out depend _buildmanifest, $(_GOALS)))
-include $(TOP)/python-defs.mak
endif

# Temporary lib dir (for testing)
blibdir	  = $(TOP)/build/lib

XINE_CFLAGS := $(shell xine-config --cflags)
XINE_LIBS   := $(shell xine-config --libs)

DEFS	  =
INCLUDES  = -I$(INCLUDEPY)
CPPFLAGS  = $(INCLUDES) $(DEFS)
CFLAGS    = $(OPT) $(XINE_CFLAGS)
CXXFLAGS  = $(OPT)
LDSHARED  = $(BLDSHARED)
LIBS	  = $(XINE_LIBS)
#LIBS	 += -lstdc++

SWIG	  = swig


%.o : %.cc
	$(CXX) $(CXXFLAGS) $(CCSHARED) $(CPPFLAGS) -c $< -o $@
%.o : %.c
	$(CC) $(CXXFLAGS) $(CCSHARED) $(CPPFLAGS) -c $< -o $@

all	: $(SOFILES) $(GEN_FILES)
distfiles: $(DIST_FILES)

#
# Recursive making
#
ifdef SUBDIRS
all	: all-recursive
check	: check-recursive
blib	: blib-recursive
distfiles: distfiles-recursive


%-recursive:
	for d in $(SUBDIRS); do $(MAKE) -C $$d $*; done

else
%-recursive:
	@true
endif

#
# Build and install local lib (for testing)
#
BLIB_SOFILES	= $(filter %$(SO), $(BLIB_FILES))
BLIB_PYFILES	= $(filter-out $(BLIB_SOFILES), $(BLIB_FILES))
BLIB_PKGDIR	= $(blibdir)$(if $(PACKAGE),/$(PACKAGE))

blib	: $(BLIB_FILES)
	$(INSTALL) -d $(BLIB_PKGDIR)
ifneq (,$(BLIB_PYFILES))
	for f in $(BLIB_PYFILES); do			\
	  $(INSTALL_DATA) $$f $(BLIB_PKGDIR)/$$f;	\
	done
endif
ifneq (,$(BLIB_SOFILES))
	for f in $(BLIB_SOFILES); do			\
	  $(INSTALL_SHARED) $$f $(BLIB_PKGDIR)/$$f;	\
	done
endif

#
# Dist targets
#
.PHONY: _buildmanifest
_buildmanifest:
	@for f in $(DIST_FILES); do					\
	  echo $(_subdir)$$f 1>&3;					\
	done
ifdef SUBDIRS
	@for d in $(SUBDIRS); do					\
	  $(MAKE) _subdir="$(_subdir)$$d/" -C $$d $@;			\
	done
endif

#
# Cleanup targets
#
.PHONY: mostlyclean clean distclean maintainer-clean

MOSTLYCLEAN_FILES	+= *~ *.o
CLEAN_FILES		+= .*.d *.py[co]
DISTCLEAN_FILES		+= $(SOFILES)
MAINTAINER_CLEAN_FILES	+= $(GEN_FILES)

mostlyclean	: mostlyclean-recursive
	rm -f $(MOSTLYCLEAN_FILES)
clean		: clean-recursive
	rm -f $(MOSTLYCLEAN_FILES) $(CLEAN_FILES)
distclean	: distclean-recursive
	rm -f $(MOSTLYCLEAN_FILES) $(CLEAN_FILES) $(DISTCLEAN_FILES)
maintainer-clean: maintainer-clean-recursive
	rm -f $(MOSTLYCLEAN_FILES) $(CLEAN_FILES) $(DISTCLEAN_FILES) \
	      $(MAINTAINER_CLEAN_FILES)


#
# Auto dependency generation
#
DEPFILES  = $(patsubst %.o, .%.d, $(OFILES))
.PHONY: depend

ifneq (,$(strip $(DEPFILES)))
depend:
	rm -f $(DEPFILES)
	$(MAKE) $(DEPFILES)

.%.d : %.c
	$(CC) -M $(CPPFLAGS) $< | \
	   sed 's/^\(.*\)\.o:/\1.o .\1.d:/' > $@
.%.d : %.cc
	$(CXX) -M $(CPPFLAGS) $< | \
	   sed 's/^\(.*\)\.o:/\1.o .\1.d:/' > $@

# (Don't include $(DEPFILES) when targets include *clean or depend)
ifneq (,$(filter-out %clean depend _buildmanifest, $(_GOALS)))
-include $(DEPFILES)
endif

endif

# Local Variables:
# mode: Makefile
# End:
