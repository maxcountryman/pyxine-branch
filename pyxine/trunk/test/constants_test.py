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
from pyxine.constants import *

class ConstantsTests(unittest.TestCase):
    def test_0(self):
        self.failUnlessEqual(XINE_VISUAL_TYPE_NONE, 0)

    def test_1(self):
        self.failUnlessEqual(type(XINE_IMGFMT_YV12), int)
    
                             
if __name__ == '__main__':
    unittest.main()
    
    
