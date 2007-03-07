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
from pyxine.constwrap import *
from pyxine.constants import *

class ConstwrapTests(unittest.TestCase):
    def test_str(self):
        self.failUnlessEqual(str(XINE_ERROR(XINE_ERROR_NONE)), "XINE_ERROR_NONE")

    def test_repr(self):
        self.failUnlessEqual(repr(XINE_ERROR(XINE_ERROR_NONE)), "XINE_ERROR_NONE")

    def test_iter(self):
        self.failUnless('NONE' in XINE_ERROR)

    def test_init_with_str(self):
        self.failUnlessEqual(XINE_STATUS("STOP"), XINE_STATUS_STOP)

    def test_init_with_prefixed_str(self):
        self.failUnlessEqual(XINE_STATUS("XINE_STATUS_PLAY"), XINE_STATUS_PLAY)

    def test_bad_init(self):
        self.failUnlessRaises(ValueError, XINE_STATUS, "FOO")

    def test_XINE_EVENT_INPUT(self):
        self.failUnlessEqual(XINE_EVENT_INPUT("MOUSE_BUTTON"), XINE_EVENT_INPUT_MOUSE_BUTTON)
        self.failUnlessEqual(XINE_EVENT_INPUT("INPUT_MOUSE_MOVE"), XINE_EVENT_INPUT_MOUSE_MOVE)
        self.failUnlessEqual(XINE_EVENT_INPUT("XINE_EVENT_INPUT_MENU1"), XINE_EVENT_INPUT_MENU1)
        self.failUnlessRaises(ValueError, XINE_EVENT_INPUT, "BAR")

    def test_contains(self):
        self.failUnless(XINE_EVENT_INPUT.contains(XINE_EVENT_INPUT_MOUSE_BUTTON))
        self.failUnless(XINE_EVENT_INPUT.contains("MOUSE_MOVE"))
        self.failUnless(XINE_EVENT_INPUT.contains("INPUT_MOUSE_MOVE"))
        self.failUnless(XINE_EVENT_INPUT.contains("XINE_EVENT_INPUT_MOUSE_MOVE"))
        self.failIf(XINE_EVENT_INPUT.contains(XINE_EVENT_QUIT))

    def test_compare_with_int(self):
        play = XINE_STATUS("PLAY")
        self.failUnlessEqual(play, XINE_STATUS_PLAY)
        self.failUnless(play > XINE_STATUS_STOP)
        self.failUnlessEqual(XINE_STATUS_PLAY, play)
        self.failUnless(XINE_STATUS_STOP < play)
    
    def test_compare_with_constwrap(self):
        idle = XINE_STATUS("IDLE")
        enone = XINE_ERROR("NONE")
        self.failUnlessEqual(int(idle), int(enone))
        self.failUnlessEqual(idle, XINE_STATUS("IDLE"))
        self.failIfEqual(idle, enone)

    def test_compare_with_string(self):
        play = XINE_STATUS("PLAY")
        enone = XINE_ERROR("NONE")
        self.failUnlessEqual(play, "PLAY")
        self.failUnless(play in ("STOP", "PLAY"))
        self.failUnless(play in XINE_STATUS)
        self.failUnlessEqual("PLAY", play)
        self.failUnlessEqual(play, "XINE_STATUS_PLAY")
        self.failUnlessEqual(str(XINE_STATUS_PLAY), play)
        self.failUnless(play > "STOP")
        self.failUnless("QUIT" > play)

        
        
if __name__ == '__main__':
    unittest.main()
    
    
