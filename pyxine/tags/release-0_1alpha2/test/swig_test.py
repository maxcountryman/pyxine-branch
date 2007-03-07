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
import unittest

import pyxine
from pyxine.libxine import *

class SwigTests(pxtest.TestCase):
    """Tests of the SWIG typemaps."""

    def setUp(self):
        self.xine = self.getXine().this

    def get_xine_stream_t(self):
        return self.getStream().this
    
    # FIXME: test int64_t INPUT
    
    def test_CONSTANT_MEMBER(self):
        xine = self.xine
        cfg = xine_config_get_first_entry(xine)
        self.failUnlessRaises(AttributeError,
                              xine_cfg_entry_s_key_set, cfg, "foo");

    def test_INT_ARRAY256_t(self):
        s = self.get_xine_stream_t()
        osd = xine_osd_new(s,0,0,50,50)
        color, trans = xine_osd_get_palette(osd)
        self.failUnlessEqual(len(color), 256)
        self.failUnlessEqual(type(color[0]), int)
        self.failUnlessEqual(len(trans), 256)
        self.failUnlessEqual(type(trans[0]), int)

        xine_osd_set_palette(osd, color, trans)
        self.failUnlessRaises(ValueError,
                              xine_osd_set_palette, osd, color, trans[:10])
        self.failUnlessRaises(ValueError,
                              xine_osd_set_palette, osd, ['2'] * 256, trans)
        xine_osd_free(osd)

    # STRING OUT gets tested by CONSTANT_MEMBER

    def test_FREEABLE_STRING_t(self):
        xine = self.xine
        exts = xine_get_file_extensions(xine)
        self.failUnless('mpg' in exts.split(' '))

    def test_STRING_p(self):
        self.failUnless('none' in xine_list_video_output_plugins(self.xine))

    # STRINGDUP INPUT
    # STRINGDUP *INPUT
    #  these get tested by the Xine.config.register_* tests in test/simple.py

    def test_opt_STRING_t(self):
        self.delStream()
        ao = xine_open_audio_driver(self.xine, None, "NULL")
        xine_close_audio_driver(self.xine, ao)
        self.failUnlessRaises(pyxine.Error,
                              xine_open_audio_driver, self.xine, "foo", "NULL")

    def xtest_STRING64_t(self):
        # FIXME: need a stream with a LANG?
        s = self.get_xine_stream_t()
        xine_open(s, self.getTestMRL())
        print "LANG", xine_get_audio_lang(s, -1)

    def test_SWIGPTR_p(self):
        s = self.getStream()
        # this tests SWIGPTR *INPUT
        post = xine_post_init(self.xine, "goom", 1, [s.ao.this], [s.vo.this])
        # this tests SWIGPTR * OUT
        inputs = xine_post_s_audio_input_get(post)
        self.failUnlessEqual(len(inputs), 1)
        self.failUnless(inputs[0].endswith("_xine_audio_port_t_p"))
        xine_post_dispose(self.xine, post)

    # FIXME: test xine_mrl_t **
    # FIXME: test struct timeval *
    # FIXME: test xine_cfg_entry *

    def test_NONNULL_SWIGPTR(self):
        self.delStream()
        self.failUnlessRaises(pyxine.Error,
                              xine_open_audio_driver, self.xine, "foo", "NULL")
        try:
            xine_open_audio_driver(self.xine, "foo", "NULL")
            self.fail()
        except pyxine.Error, e:
            self.failUnlessEqual(str(e), "xine_open_audio_driver failed")

    def test_OKAY(self):
        s = self.get_xine_stream_t()
        self.failUnlessRaises(pyxine.Error,
                              xine_get_pos_length, s)

    def test_ITER_OKAY(self):
        xine = self.xine
        n = 0
        try:
            xine_config_get_first_entry(xine)
            while 1:
                n = n + 1
                xine_config_get_next_entry(xine)
        except StopIteration:
            pass
        self.failUnless(n > 0)

    def test_LOOKUP_OKAY(self):
        xine_config_lookup_entry(self.xine, "misc.memcpy_method")
        self.failUnlessRaises(KeyError,
                              xine_config_lookup_entry, self.xine, "foo.junk")
        
if __name__ == '__main__':
    unittest.main()
    
    
