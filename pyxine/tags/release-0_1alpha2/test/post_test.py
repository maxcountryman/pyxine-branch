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

import pxtest
import unittest, weakref
from pyxine import post

class PostTests(pxtest.TestCase):
    def setUp(self):
        stream = self.getStream()
        self.stream = stream
        self.goom = post.Post(stream, "goom",
                              audio_target=stream.ao, video_target=stream.vo)

    def tearDown(self):
        del self.goom
        del self.stream
                              
    def test_construct_goom(self):
        self.failUnless(self.goom)

    def check_in_out(self, dict, name, length=1):
        self.failUnlessEqual(len(dict), length)
        self.failUnless(name in dict)
        self.failUnlessEqual(dict[name].name, name)
        self.failUnlessEqual(dict.get(name).name, name)
        self.failUnlessRaises(KeyError, dict.__getitem__, "foo")
        self.failUnlessEqual(dict.get("foo", "baz"), "baz")

    def test_inputs(self):
        self.check_in_out(self.goom.inputs, "audio in", 1)

    def test_outputs(self):
        self.check_in_out(self.goom.outputs, "audio out", 2)

    def test_destruction(self):
        stream = self.stream
        goomref = weakref.ref(self.goom)
        stream.audio_source.wire(self.goom.inputs["audio in"])
        self.goom = None
        self.failUnless(goomref(), "Post(goom) deleted itself too early")
        stream.audio_source.wire(stream.ao)
        self.failIf(goomref(), "Post(goom) didn't delete itself")

    def test_PostOutput_destruction(self):
        stream = self.stream
        ref = weakref.ref(stream.audio_source)
        self.failIf(ref(), "PostOutput from Stream didn't delete itself")
        ref = weakref.ref(self.goom.outputs["generated video"])
        self.failIf(ref(), "PostOutput from Post(goom) didn't delete itself")
    

if __name__ == '__main__':
    unittest.main()
