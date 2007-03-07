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

import weakref

class weakmethod(object):
    """A weakly bound method.

    This is a class method which binds to its instance using a weakref.

    This is useful, among other things, for callback methods in pyxine,
    so that the existence of the bound method (in the C guts of libxine)
    won't keep the instance from being garbage collected.

    Example:

        from pyxine.weakmethod import weakmethod
        
        class MyClass:

            def callback(self, arg):
                self.arg_val = arg
            callback = weakmethod(callback)

        o = MyClass()

        cb = o.callback

        cb(1)

        del o                           # o will be garbage collected here

        # This will rais weakref.ReferenceError (when/if the bound method
        # tries to use self.)
        cb(2)                          
    """

    im_func = None
    im_class = None
    im_self = None
    
    def __init__(self, func):
        self.im_func = func
    def __getattr__(self, attr):
        return getattr(self.im_func, attr)
    def __get__(self, obj, cls=None):
        if obj is not None:
            return _bound(self, obj, cls)
        else:
            return _unbound(self, cls)

class _bound(weakmethod):
    def __init__(self, method, obj, cls):
        self.im_func = method.im_func
        self.im_self = weakref.proxy(obj)
        self.im_class = cls

    def __call__(self, *args, **kwargs):
        self.im_self
        return self.im_func(self.im_self, *args, **kwargs)

class _unbound(weakmethod):
    def __init__(self, method, cls):
        self.im_func = method.im_func
        self.im_class = cls

