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

import pyxine
from pyxine import event
from pyxine.constants import *

class EventTests(unittest.TestCase):

    def test_InputEvent(self):
        e = event.InputEvent(XINE_EVENT_INPUT_MOUSE_BUTTON, button=1, x=2, y=3)
        self.failUnlessEqual(e.type, XINE_EVENT_INPUT_MOUSE_BUTTON)
        self.failUnlessEqual(e.data.button, 1)
        self.failUnlessEqual(e.data.x, 2)
        self.failUnlessEqual(e.data.y, 3)

    def test_InputEvent_mutable(self):
        e = event.InputEvent(XINE_EVENT_INPUT_MOUSE_BUTTON, button=1, x=2, y=3)
        e.type = "INPUT_MOUSE_MOVE"
        e.data.button = 2
        e.data.x = 4
        e.data.y = 6
        self.failUnlessEqual(e.type, XINE_EVENT_INPUT_MOUSE_MOVE)
        self.failUnlessEqual(e.data.button, 2)
        self.failUnlessEqual(e.data.x, 4)
        self.failUnlessEqual(e.data.y, 6)

    def test_wrap_event(self):
        e = event.InputEvent(XINE_EVENT_INPUT_MOUSE_BUTTON, button=1, x=2, y=3)
        w = event._wrap_event(e.this)
        e.data.y = 6
        self.failUnlessEqual(w.type, XINE_EVENT_INPUT_MOUSE_BUTTON)
        self.failUnlessEqual(w.data.button, 1)
        self.failUnlessEqual(w.data.x, 2)
        self.failUnlessEqual(w.data.y, 6)

if __name__ == '__main__':
    unittest.main()
    
