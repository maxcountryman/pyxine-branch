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

"""Wrappers for the SWIG-generated struct accessors.

"""

from pyxine import libxine
import inspect, weakref

class _member(property):
    def __init__(self, struct_name, name):
        accessor_base = "%s_%s" % (struct_name, name)
        doc = "%s::%s" % (struct_name, name)

        getter = getattr(libxine, accessor_base + "_get")
        setter = getattr(libxine, accessor_base + "_set", None)

        def fget(self): return getter(self.this)

        if setter:
            def fset(self, val): setter(self.this, val)
        else:
            fset = None

        property.__init__(self, fget, fset)
        self.__doc__ = doc
        
class _cstruct(object):
    class __metaclass__(type):
        def __new__(cls_type, cls_name, cls_bases, cls_dict):
            if cls_name == '_cstruct' or cls_bases[0] != _cstruct:
                return type.__new__(cls_type, cls_name, cls_bases, cls_dict)
                
            struct_name = cls_name

            def isgetter(func):
                return func.endswith('_get') and func.startswith(struct_name)

            members = map(lambda s: s[len(struct_name)+1:-4],
                          filter(isgetter, dir(libxine)))
            members.sort()

            for name in members:
                cls_dict[name] = _member(struct_name, name)

            def __repr__(self):
                data =  dict(map(lambda m: (m, getattr(self, m)),
                                 members))
                return "<%s: %s>" % (cls_name, data)
            
            cls_dict['__repr__'] = __repr__
            cls_dict['__str__'] = __repr__
            cls_dict['_struct_name'] = struct_name
            
            return type.__new__(cls_type, cls_name, cls_bases, cls_dict)


    def __init__(self, datap):
        if type(datap) is str:
            if datap.endswith("_void_p"):
                datap = datap[:-6] + self.__class__.__name__ + "_p"
            elif not datap.endswith("_p"):
                raise ValueError, "bad SWIG pointer (%s)" % datap
        elif not datap:
            # FIXME: better checking for PyBuffer object
            raise ValueError
        
        self.this = datap


class super(object):
    """This is like the __builtin__.super, but it works for properties.

    (The builtin super only seems to work for methods.)
    """
    def __init__(self, cls, object=None):
        self.__dict__['_super__cls'] = cls
        if object is not None:
            object = weakref.proxy(object)
        self.__dict__['_super__object'] = object

    def __get__(self, object, cls=None):
        if not self.__object:
            if object is not None:
                object = weakref.proxy(object)
            self.__dict__['_super__object'] = object
        return self
    
    def __getprop(self, name):
        base_seen = 0
        for sup in inspect.getmro(self.__object.__class__):
            if not base_seen:
                base_seen = sup is self.__cls
            else:
                a = getattr(sup, name, None)
                if hasattr(a, '__get__'):
                    return a
        raise AttributeError

    def __getattr__(self, name):
        return self.__getprop(name).__get__(self.__object, self.__object.__class__)

    def __setattr__(self, name, val):
        self.__getprop(name).__set__(self.__object, val)

class xine_event_t(_cstruct): pass
class xine_ui_data_t(_cstruct): pass
class xine_format_change_data_t(_cstruct): pass
class xine_audio_level_data_t(_cstruct): pass
class xine_progress_data_t(_cstruct): pass
class xine_input_data_t(_cstruct): pass

class xine_cfg_entry_s(_cstruct): pass
xine_cfg_entry_t = xine_cfg_entry_s

class xine_post_s(_cstruct): pass
xine_post_t = xine_post_s
class xine_post_in_s(_cstruct): pass
xine_post_in_t = xine_post_in_s
class xine_post_out_s(_cstruct): pass
xine_post_out_t = xine_post_out_s
