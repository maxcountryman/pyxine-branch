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

import unittest
from pyxine import cstruct, libxine

class CstructTests(unittest.TestCase):
    def setUp(self):
        raw = libxine.px_make_input_event(1,2,3,4)
        self.e = cstruct.xine_event_t(raw)

    def test_simple(self):
        e = self.e
        self.failUnlessEqual(e.type, 1)

    def test_set_type(self):
        e = self.e
        e.type = 42
        self.failUnlessEqual(e.type, 42)
    
    def test_input_event(self):
        e = self.e
        ie = cstruct.xine_input_data_t(e.data)
        self.failUnlessEqual(ie.button, 2)
        self.failUnlessEqual(ie.x, 3)
        self.failUnlessEqual(ie.y, 4)

    # FIXME: test more complicated (**) accessors.

_n_TestSubclasses = 0

class SuperTests(unittest.TestCase):
    class TestClass(object):
        __p = 2
    
        def m(self):
            return 1

        def _get_p(self):
            return self.__p
        def _set_p(self, val):
            self.__p = val
        p = property(_get_p, _set_p)

    class TestSubclass(TestClass):

        def __init__(self):
            self.__super = cstruct.super(SuperTests.TestSubclass, self)
            global _n_TestSubclasses
            _n_TestSubclasses = _n_TestSubclasses + 1

        def __del__(self):
            global _n_TestSubclasses
            _n_TestSubclasses = _n_TestSubclasses - 1

        def m(self):
            return "SUPER: %d" % self.__super.m()

        def _set_p_sub(self, val):
            self.__super.p = 2 * val
        
        p = property(lambda self: "SUPER: %s" % self.__super.p, _set_p_sub)

    def test_method(self):
        ts = self.TestSubclass()
        self.failUnlessEqual(ts.m(), "SUPER: 1")

    def test_get_prop(self):
        ts = self.TestSubclass()
        self.failUnlessEqual(ts.p, "SUPER: 2")

    def test_set_prop(self):
        ts = self.TestSubclass()
        ts.p = 2
        self.failUnlessEqual(ts.p, "SUPER: 4")

    def test_destruction(self):
        ts = self.TestSubclass()
        del ts
        self.failUnlessEqual(_n_TestSubclasses, 0)
        
if __name__ == '__main__':
    unittest.main()
