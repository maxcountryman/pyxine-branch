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

"""Wrappers for the various constant sets.

This probably is just way too much syntactic sugar.
"""

from pyxine import constants
import warnings

class _constants(int):
    class __metaclass__(type):
        def __new__(cls_type, cls_name, cls_bases, cls_dict):
            prefix = cls_name + "_"

            names = {}
            values = {}
            for name in dir(constants):
                if name.startswith(prefix):
                    val = getattr(constants, name)
                    names[val] = name
                    values[name[len(prefix):]] = val

            if not names and cls_name != '_constants':
                import warnings
                warnings.warn("%s: empty constant set" % cls_name, stacklevel=2)
                
            cls_dict["_prefix"] = prefix
            cls_dict["_names"] = names
            cls_dict["_values"] = values
            cls_dict["__slots__"] = []

            return type.__new__(cls_type, cls_name, cls_bases, cls_dict)

        def __iter__(self):
            """Allow use of class as sequence of constant names.

            Example:
            
                >>> list(XINE_STATUS)
                ['IDLE', 'STOP', 'PLAY', 'QUIT']
            """
            return iter(self._values)

    def _str2int(cls, name):
        if name.startswith(cls._prefix):
            return getattr(constants, name, None)
        try:
            return getattr(constants, cls._prefix + name)
        except AttributeError:
            pass
        try:
            return cls.__bases__[0]._str2int(name)
        except AttributeError:
            return None
    _str2int = classmethod(_str2int)
    
    def __new__(cls, val):
        try:
            intval = int(val)
        except ValueError:
            intval = cls._str2int(str(val))
            if intval is None:
                raise ValueError, "%s: unknown constant" % val
        else:
            if not cls._names.has_key(intval):
                # FIXME: Use a specific warning class for this.
                warnings.warn("bad value for %s* (%d)" % (cls._prefix, intval),
                              stacklevel=2)

        return int.__new__(cls, intval)

    def __str__(self):
        try:
            return self._names[int(self)]
        except KeyError:
            return "%s(%d)" % (self.__class__.__name__, self)

    __repr__ = __str__

    def __cmp__(self, other):
        if isinstance(other, _constants):
            return cmp((self._prefix, int(self)), (other._prefix, int(other)))
        try:
            return cmp(int(self), int(other))
        except ValueError:
            return cmp(int(self), int(self.__class__(str(other))))
    
    def contains(cls, val):
        """Check to see if value is in the set of known constants.

        >>> XINE_EVENT_INPUT.contains(101) # 101 = XINE_EVENT_INPUT_MOUSE_BUTTON
        1
        >>> XINE_EVENT_INPUT.contains(0)
        0
        >>> XINE_EVENT_INPUT.contains('MOUSE_BUTTON')
        1
        """
        try:
            return cls._names.has_key(int(val))
        except ValueError:
            return cls._str2int(str(val)) is not None
    contains = classmethod(contains)
    
class XINE_VISUAL_TYPE(_constants): pass
class XINE_MASTER_SLAVE(_constants): pass
class XINE_TRICK_MODE(_constants): pass
class XINE_PARAM(_constants): pass
class XINE_SPEED(_constants): pass
class XINE_PARAM_VO(_constants): pass
#class XINE_VO_ZOOM(_constants): pass
class XINE_VO_ASPECT(_constants): pass
class XINE_DEMUX(_constants): pass
class XINE_IMGFMT(_constants): pass
class XINE_POST_TYPE(_constants): pass
class XINE_POST_DATA(_constants): pass
class XINE_STATUS(_constants): pass
class XINE_ERROR(_constants): pass
class XINE_STREAM_INFO(_constants): pass
class XINE_META_INFO(_constants): pass

# FIXME: this is a bitmask
class XINE_MRL_TYPE(_constants): pass

class XINE_GUI_SEND(_constants): pass
#class XINE_HEALTH_CHECK(_constants): pass
#class CHECK(_constants): pass
class XINE_CONFIG_TYPE(_constants): pass

class XINE_EVENT(_constants): pass
class XINE_EVENT_INPUT(XINE_EVENT): pass

class XINE_OSD(_constants): pass
class XINE_TEXTPALETTE(_constants): pass
