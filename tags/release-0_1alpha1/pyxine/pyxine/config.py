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

from pyxine import libxine, cstruct, constants, constwrap
import inspect

class _ConfigEntry(object):
    def __init__(self, rep):
        self.rep = rep

    key = property(lambda s: s.rep.key)
    type = property(lambda s: constwrap.XINE_CONFIG_TYPE(s.rep.type))
    description = property(lambda s: s.rep.description)
    help = property(lambda s: s.rep.help)
    exp_level = property(lambda s: s.rep.exp_level)

    def __repr__(self):
        def is_property(p): return type(p) == property
        d = {}
        for k,v in inspect.getmembers(self.__class__, is_property):
            d[k] = getattr(self, k)
        return "<%s: %s>" % (self.__class__.__name__, d)

    __str__ = __repr__
    
class _Num_ConfigEntry(_ConfigEntry):
    def _set_value(self, val):
        self.rep.num_value = val
    value = property(lambda s: s.rep.num_value, _set_value)
    default = property(lambda s: s.rep.num_default)

    def __str__(self):
        return str(self.value)
    def __int__(self):
        return self.value
    
class _Bool_ConfigEntry(_Num_ConfigEntry):
    pass

class _Range_ConfigEntry(_Num_ConfigEntry):
    min = property(lambda s: s.rep.range_min)
    max = property(lambda s: s.rep.range_max)

class _String_ConfigEntry(_ConfigEntry):
    def _set_value(self, val):
        self.rep.str_value = val
    value = property(lambda s: s.rep.str_value, _set_value)
    default = property(lambda s: s.rep.str_default)
    sticky = property(lambda s: s.rep.str_sticky) # FIXME: what is this ??

    def __str__(self):
        return self.value

class _Enum_ConfigEntry(_ConfigEntry):
    values = property(lambda s: s.rep.enum_values)
    enum_values = values

    def _set_num_value(self, val):
        try:
            self.values[val]
        except IndexError:
            raise ValueError
        self.rep.num_value = val
    num_value = property(lambda s: s.rep.num_value, _set_num_value)
    num_default = property(lambda s: s.rep.num_default)
    
    def _set_value(self, val):
        if type(val) is int:
            self.rep.num_value = val
        else:
            self.rep.num_value = list(self.values).index(val)
    value = property(lambda s: s.values[s.rep.num_value], _set_value)
    default = property(lambda s: s.values[s.rep.num_default])

    def __str__(self):
        return self.value

_config_entry_types = {
    constants.XINE_CONFIG_TYPE_RANGE: _Range_ConfigEntry,
    constants.XINE_CONFIG_TYPE_STRING: _String_ConfigEntry,
    constants.XINE_CONFIG_TYPE_ENUM: _Enum_ConfigEntry,
    constants.XINE_CONFIG_TYPE_NUM: _Num_ConfigEntry,
    constants.XINE_CONFIG_TYPE_BOOL: _Bool_ConfigEntry,
    }

def xine_cfg_entry_t(packed):
    rep = cstruct.xine_cfg_entry_t(packed)
    proxy = _config_entry_types.get(rep.type, _ConfigEntry)
    return proxy(rep)


def _wrap_cb(cb):
    if cb is None:
        return None
    def wrapper(entry):
        cb(xine_cfg_entry_t(entry))
    return wrapper

class XineConfig:
    def __init__(self, xine):
        self.this = xine.this
        self.xine = xine

    def load(self, cfg_filename):
        if self.xine.cfg_filename is not None:
            self.reset()
        libxine.xine_config_load(self.this, cfg_filename)
        self.xine.cfg_filename = cfg_filename

    def save(self, cfg_filename=None):
        cfg_filename = cfg_filename or self.xine.cfg_filename
        libxine.xine_config_save(self.this, cfg_filename)
        self.xine.cfg_filename = cfg_filename

    def reset(self):
        libxine.xine_config_reset(self.this)
        self.xine.cfg_filename = None
        
    def values(self):
        v = []
        try:
            entry = libxine.xine_config_get_first_entry(self.this)
            while 1:
                v.append(xine_cfg_entry_t(entry))
                entry = libxine.xine_config_get_next_entry(self.this)
        except StopIteration:
            pass
        return v
    def keys(self):
        return map(lambda entry: entry.key, self.values())
    def items(self):
        return map(lambda entry: (entry.key, entry), self.values())
    def itervalues(self):
        return iter(self.values())
    def iterkeys(self):
        return iter(self.keys())
    def iteritems(self):
        return iter(self.items())
    def __iter__(self):
        return self.iterkeys()
    
    def __getitem__(self, key):
        entry = libxine.xine_config_lookup_entry(self.this, key)
        return xine_cfg_entry_t(entry)

    def __setitem__(self, key, value):
        entry = self[key]
        entry.value = value
        libxine.xine_config_update_entry(self.this, entry.rep.this)

            
    def register_string(self, key, def_value="",
                        description="", help="", exp_level=0,
                        changed_cb=None):
        return libxine.xine_config_register_string(
            self.this, key, def_value,
            description, help, exp_level,
            _wrap_cb(changed_cb))

    def register_range(self, key, def_value=0, min=0, max=100,
                       description="", help="", exp_level=0,
                       changed_cb=None):
        return libxine.xine_config_register_range(
            self.this, key, def_value, min, max,
            description, help, exp_level,
            _wrap_cb(changed_cb))

    def register_enum(self, key, def_value=0, values=(),
                      description="", help="", exp_level=0,
                      changed_cb=None):

        num_val = libxine.xine_config_register_enum(
            self.this, key, def_value, values,
            description, help, exp_level,
            _wrap_cb(changed_cb))
        return values[num_val]

    def register_num(self, key, def_value=0,
                     description="", help="", exp_level=0,
                     changed_cb=None):
        return libxine.xine_config_register_num(
            self.this, key, def_value,
            description, help, exp_level,
            _wrap_cb(changed_cb))

    def register_bool(self, key, def_value=0,
                      description="", help="", exp_level=0,
                      changed_cb=None):
        return libxine.xine_config_register_bool(
            self.this, key, def_value,
            description, help, exp_level,
            _wrap_cb(changed_cb))
