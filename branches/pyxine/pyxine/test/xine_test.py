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
import unittest, time

import pyxine
from pyxine import libxine
from pyxine.constants import *

class SimpleXineTests(unittest.TestCase):
    """Tests which can be run without instantiating a Xine object."""
    
    def test_get_version_string(self):
        self.failUnlessEqual(pyxine.get_version_string(),
                             pyxine.XINE_VERSION)

    def test_get_version(self):
        self.failUnlessEqual(pyxine.get_version(),
                             (pyxine.XINE_MAJOR_VERSION,
                              pyxine.XINE_MINOR_VERSION,
                              pyxine.XINE_SUB_VERSION))

    def test_check_version(self):
        pyxine.check_version() # shouldn't fail
        self.failUnlessRaises(pyxine.Error,
                              pyxine.check_version, 42,0,1)

class XineTests(pxtest.TestCase):

    def setUp(self):
        self.xine = self.getXine()
        
    def testBasic(self):
        repr(self.xine.config['misc.memcpy_method'])

    def test_open_audio_driver(self):
        self.delStream()
        self.xine.open_audio_driver()
        self.failUnlessRaises(pyxine.Error,
                              self.xine.open_audio_driver, "foo-driver")
    
    def test_open_video_driver(self):
        self.delStream()
        self.xine.open_video_driver()
        self.failUnlessRaises(pyxine.Error,
                              self.xine.open_video_driver, "foo-driver")

    def test_stream_new(self):
        self.delStream()
        ao = self.xine.open_audio_driver()
        vo = self.xine.open_video_driver()
        self.xine.stream_new(ao, vo)

    def test_get_browsable_plugin_ids(self):
        browsable_ids = self.xine.get_browsable_input_plugin_ids()
        self.failUnless('file' in browsable_ids)

    def test_get_autoplay_plugin_ids(self):
        autoplay_ids = self.xine.get_autoplay_input_plugin_ids()
        self.failUnless('DVD' in autoplay_ids)

    def test_get_file_extension(self):
        file_extensions = self.xine.get_file_extensions()
        self.failUnless('avi' in file_extensions)

    def test_get_mime_types(self):
        mime_types = self.xine.get_mime_types()
        self.failUnless('video/mpeg' in mime_types)
        self.failUnless('mpg' in mime_types['video/mpeg'].extensions)

    def test_get_demux_for_mime_type(self):
        xine = self.xine
        self.failUnlessEqual(xine.get_demux_for_mime_type('video/mpeg'), 'mpeg')
        self.failUnlessEqual(xine.get_demux_for_mime_type('foo/bar'), None)

    def test_get_input_plugin_descriptions(self):
        xine = self.xine
        desc = xine.get_input_plugin_description('file')
        self.failUnlessEqual(type(desc), type(""))
        self.failUnless(len(desc) > 0)

    def test_list_audio_output_plugins(self):
        ao_ids = self.xine.list_audio_output_plugins()
        self.failUnless(len(ao_ids) > 0)
        self.failUnlessEqual(type(ao_ids[0]), type(""))

    def test_list_video_output_plugins(self):
        vo_ids = self.xine.list_video_output_plugins()
        self.failUnless('none' in vo_ids)
        
    def test_list_post_plugins(self):
        xine = self.xine
        self.failUnless('goom' in xine.list_post_plugins())
        self.failUnless('goom' in xine.list_post_plugins("AUDIO_VISUALIZATION"))
        self.failUnless('goom' not in xine.list_post_plugins("VIDEO_FILTER"))

    def test_get_log_names(self):
        xine = self.xine
        log_names = xine.get_log_names()
        self.failUnless('plugin' in log_names)
        log_section_count = libxine.xine_get_log_section_count(xine.this)
        self.failUnlessEqual(len(log_names), log_section_count)
                             
    def test_get_log(self):
        xine = self.xine
        log_lines = xine.get_log('plugin')
        self.failUnless(log_lines[0])
        self.failUnless(type(log_lines[0]) == type(""))
        log_lines = xine.get_log(1)
        self.failUnless(log_lines[0])
        self.failUnless(type(log_lines[0]) == type(""))

    def test_log(self):
        xine = self.xine
        xine.log(0, "foo")
        self.failUnlessEqual(xine.get_log(0)[0], "foo\n")

    def xtest_register_log_cb(self):
        self.fail("FIXME: fill this out when xine_register_log_cb works.")
        
class XineConfigTests(pxtest.TestCase):
    class ConfigTracker:
        def __init__(self, val=None):
            self.val = val
        def callback(self, cfg):
            self.val = cfg.value
    

    def setUp(self):
        self.xine = self.getXine()
        self.config = self.xine.config

    def test_config_num(self):
        val = self.config['decoder.mpeg2_priority'].default
        self.failUnlessEqual(val, 6)

    def test_config_bool(self):
        val = self.config['input.file_hidden_files'].default
        self.failUnlessEqual(val, 1)
        
    def test_config_range(self):
        val = self.config['codec.a52_level'].default
        self.failUnlessEqual(val, 100)

    def test_config_enum(self):
        val = self.config['misc.demux_strategy'].default
        self.failUnlessEqual(val, "default")

    def test_config_string(self):
        val = self.config['input.vcd_device'].default
        self.failUnlessEqual(val, '/dev/cdrom')

    def test_register_num(self):
        xine, config = self.xine, self.config
        name = 'junk.test_num'

        tracker = self.ConfigTracker()
        tracker.val = config.register_num(name, def_value=3, changed_cb=tracker.callback)
        cfg = config[name]
        self.failUnlessEqual(tracker.val, cfg.default)
        config[name] = 6
        self.failUnlessEqual(tracker.val, 6)
        self.failUnlessEqual(config[name].value, 6)

    def test_register_bool(self):
        xine, config = self.xine, self.config
        name = 'junk.test_bool'

        tracker = self.ConfigTracker()
        tracker.val = config.register_bool(name, changed_cb=tracker.callback)
        cfg = config[name]
        self.failUnlessEqual(tracker.val, cfg.default)
        config[name] = 1
        self.failUnlessEqual(tracker.val, 1)
        config[name] = 0
        self.failUnlessEqual(tracker.val, 0)
        self.failUnlessEqual(config[name].value, 0)
        
    def test_register_range(self):
        xine, config = self.xine, self.config
        name = 'junk.test_range'

        tracker = self.ConfigTracker()
        tracker.val = config.register_range(name, changed_cb=tracker.callback)
        cfg = config[name]
        self.failUnlessEqual(tracker.val, cfg.default)
        config[name] = 6
        self.failUnlessEqual(tracker.val, 6)
        self.failUnlessEqual(config[name].value, 6)

    def test_register_enum(self):
        xine, config = self.xine, self.config
        tracker = self.ConfigTracker()
        tracker.val = config.register_enum('junk.test_enum',
                                           values=('val-a', 'val-b', 'val-c'),
                                           changed_cb=tracker.callback)
        cfg = config['junk.test_enum']
        self.failUnlessEqual(tracker.val, cfg.default)
        config['junk.test_enum'] = 'val-c'
        self.failUnlessEqual(tracker.val, 'val-c')
        config['junk.test_enum'] = 1
        self.failUnlessEqual(tracker.val, 'val-b')
        self.failUnlessEqual(config['junk.test_enum'].value, 'val-b')

    def test_register_string(self):
        xine, config = self.xine, self.config
        name = 'junk.test_string'

        tracker = self.ConfigTracker()
        tracker.val = config.register_string(name,
                                           def_value='foo',
                                           changed_cb=tracker.callback)
        cfg = config[name]
        self.failUnlessEqual(tracker.val, cfg.default)
        config[name] = 'val-c'
        self.failUnlessEqual(tracker.val, 'val-c')
        self.failUnlessEqual(config[name].value, 'val-c')
        
                             
class SimpleStreamTests(pxtest.TestCase):
    # Get and set params
    def test_get_audio_volume(self):
        stream = self.getStream()
        volume = stream.audio_volume
        self.failUnless(0 <= volume <= 100)

    def test_set_audio_volume(self):
        stream = self.getStream()
        stream.audio_volume = 25
        self.failUnlessEqual(stream.audio_volume, 25)
        stream.audio_volume = 75
        self.failUnlessEqual(stream.audio_volume, 75)

    def test_get_speed(self):
        stream = self.getStream()
        self.failUnless(str(stream.speed).startswith('XINE_SPEED_'))

    # Non-existent params
    def test_get_foo(self):
        stream = self.getStream()
        self.failUnlessRaises(AttributeError, getattr, stream, 'foo')

    def test_set_foo(self):
        stream = self.getStream()
        self.failUnlessRaises(AttributeError, setattr, stream, 'foo', 1)

    # Stream info
    def test_get_has_video(self):
        stream = self.getStream()
        self.failUnlessEqual(stream.has_video, 0)

    def test_set_has_video(self):
        stream = self.getStream()
        self.failUnlessRaises(AttributeError, setattr, stream, 'has_video', 1)

    # Stream meta-info
    def test_get_title(self):
        stream = self.getStream()
        self.failUnless(stream.title is None)

    def test_set_title(self):
        stream = self.getStream()
        self.failUnlessRaises(AttributeError, setattr, stream, 'title', 'Foo')

    def test_get_audio_lang(self):
        stream = self.getStream()
        self.failUnlessRaises(pyxine.Error, stream.get_audio_lang)

    def test_get_spu_lang(self):
        stream = self.getStream()
        self.failUnlessRaises(pyxine.Error, stream.get_spu_lang)

    def test_get_pos_length(self):
        stream = self.getStream()
        self.failUnlessRaises(pyxine.Error, stream.get_pos_length)

    def test_eject(self):
        stream = self.getStream()
        self.failUnlessRaises(pyxine.Error, stream.eject)

    def test_get_audio_source(self):
        stream = self.getStream()
        self.failUnlessEqual(stream.audio_source.type, XINE_POST_DATA_AUDIO)

    def test_get_video_source(self):
        stream = self.getStream()
        #self.failUnlessEqual(stream.video_source.type, XINE_POST_DATA_VIDEO)
        print "TYPE", stream.video_source.type

    def test_send_event(self):
        stream = self.getStream()
        q = stream.new_event_queue()
        stream.send_input_event(XINE_EVENT_INPUT_MOUSE_BUTTON, button=1, x=2, y=3)
        e = q.get()
        self.failUnless(e)
        self.failUnlessEqual(e.type, XINE_EVENT_INPUT_MOUSE_BUTTON)
        self.failUnlessEqual(e.data.button, 1)
        self.failUnlessEqual(e.data.x, 2)
        self.failUnlessEqual(e.data.y, 3)

class PlayingStreamTests(pxtest.TestCase):
    """Tests which require an actual input stream.

    Most of these involve playing a stream."""

    def setUp(self):
        self.stream = self.getStream()
        self.stream.open(self.getTestMRL())
        self.stream.audio_volume=50

    def tearDown(self):
        self.stream.close()
        #self.delStream()
        
    # Stream meta-info
    def test_get_title(self):
        stream = self.stream
        self.failUnlessEqual(stream.title, "Wonderful and Strange")

    def test_play(self):
        stream = self.stream
        stream.play()
        time.sleep(0.1)
        
    def test_play2(self):
        stream = self.stream
        stream.play(start_time=20)
        time.sleep(0.1)

    def test_stop(self):
        stream = self.stream
        stream.play()
        time.sleep(0.1)
        stream.stop()
        stream.play()

    def test_close(self):
        stream = self.stream
        stream.play()
        time.sleep(0.1)
        stream.close()
        self.failUnlessRaises(pyxine.Error, stream.play)


    def test_get_status(self):
        stream = self.stream
        self.failUnlessEqual(stream.status, XINE_STATUS_STOP)
        stream.open(self.getTestMRL())
        self.failUnlessEqual(stream.status, XINE_STATUS_STOP)
        stream.play(start_pos=50)
        self.failUnlessEqual(stream.status, XINE_STATUS_PLAY)
        stream.stop()
        self.failUnlessEqual(stream.status, XINE_STATUS_STOP)
        stream.play(start_pos=95)
        self.failUnlessEqual(stream.status, XINE_STATUS_PLAY)
        time.sleep(2)
        self.failUnlessEqual(stream.status, XINE_STATUS_STOP)
        stream.close()
        self.failUnlessEqual(stream.status, XINE_STATUS_STOP)

    def test_get_audio_lang(self):
        stream = self.stream
        self.failUnlessRaises(pyxine.Error, stream.get_audio_lang)

    def test_get_spu_lang(self):
        stream = self.stream
        self.failUnlessRaises(pyxine.Error, stream.get_spu_lang)

    def test_get_pos_length(self):
        stream = self.stream
        pos, time, length = stream.get_pos_length()
        self.failUnlessEqual(pos, 0)
        self.failUnlessEqual(time, 0)
        self.failUnless(length > 1)

    def checkEvents(self, events):
        self.failUnlessEqual(len(events), 1)
        self.failUnlessEqual(events[0].type, XINE_EVENT_UI_PLAYBACK_FINISHED)
        
    def test_new_event_listener(self):
        stream = self.stream
        events = []
        l = stream.new_event_listener(events.append)
        stream.play(99)
        time.sleep(2)
        del l
        self.checkEvents(events)

    def test_new_event_queue(self):
        stream = self.stream
        events = []
        q = stream.new_event_queue()
        stream.play(99)
        done = 0
        while not done:
            e = q.wait()
            events.append(e)
            if e.type == XINE_EVENT_UI_PLAYBACK_FINISHED:
                done = 1
        self.checkEvents(events)

    def test_new_event_queue_polling(self):
        stream = self.stream
        events = []
        q = stream.new_event_queue()
        stream.play(99)
        done = 0
        while not done:
            e = None
            while not e:
                e = q.get()
            events.append(e)
            if e.type == XINE_EVENT_UI_PLAYBACK_FINISHED:
                done = 1
        self.checkEvents(events)

    def test_destruction(self):
        print "call delStream"
        self.delStream()
        self.stream = self.getStream()
        
    def test_send_vo_data(self):
        #FIXME:
        pass

if __name__ == '__main__':
    unittest.main()
    
    
