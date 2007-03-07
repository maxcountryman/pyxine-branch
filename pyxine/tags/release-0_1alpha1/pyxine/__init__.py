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

__all__ = [ 'constants', 'xine', 'x11', 'stream' ]

class Error(Exception):
    """Base exception class for exceptions raised by pyxine.
    """
    pass

class StreamError(Error):
    """Exceptions associated with stream error codes from xine_get_error().
    """
    def __init__(self, errcode):
        Error.__init__(self, errcode)
        self.errcode = constwrap.XINE_ERROR(errcode)
    def __str__(self):
        return str(self.errcode)


from pyxine import libxine, constwrap

from pyxine.constants import XINE_VERSION, \
     XINE_MAJOR_VERSION, XINE_MINOR_VERSION, XINE_SUB_VERSION


def get_version_string():
    """Get the version string for the installed libxine.

    Note that the version string of the libxine this pyxine was compiled
    against is available in 'XINE_VERSION'.
    """
    return libxine.xine_get_version_string()

def get_version():
    """Get the version of the installed libxine.

    Returns a triple of integers: ('major', 'minor', 'sub')

    Note that the version of the libxine this pyxine was compiled against
    is available in ('XINE_MAJOR_VERSION', 'XINE_MINOR_VERSION', 'XINE_SUB_VERSION').
    """
    return libxine.xine_get_version()

def check_version(major=XINE_MAJOR_VERSION,
                  minor=XINE_MINOR_VERSION,
                  sub=XINE_SUB_VERSION):
    """Check to see if the installed libxine is of an appropriate version.

    Raises 'Error' if the installed version of libxine is incompatible.
    """
    if not libxine.xine_check_version(major, minor, sub):
        raise Error, "Installed libxine is incompatible"


check_version()

# Import a few specific classes 
from pyxine.xine import Xine
from pyxine.x11 import X11Visual, TkWidget, XlibDrawable

