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

from pyxine.weakmethod import *

import weakref, unittest

argval = None

class TestClass:
    def weak_m(self, val):
        global argval
        argval = val
        self.val = val
    weak_m = weakmethod(weak_m)

    def m(self, val):
        global argval
        argval = val
        self.val = val

        
class Tests(unittest.TestCase):
    def setUp(self):
        self.o = TestClass()

    def test_a(self):
        m = self.o.m
        m(1)
        self.failUnlessEqual(argval, 1)
        del self.o
        m(2)
        self.failUnlessEqual(argval, 2)
        
    def test_b(self):
        m = self.o.weak_m
        m(1)
        self.failUnlessEqual(argval, 1)
        del self.o
        self.failUnlessRaises(weakref.ReferenceError, m, 2)
        self.failUnlessEqual(argval, 2)

if __name__ == '__main__':
    unittest.main()
    
    
