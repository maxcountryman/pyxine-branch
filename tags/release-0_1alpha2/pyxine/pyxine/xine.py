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

from pyxine import Error, StreamError, libxine, constants, constwrap
import warnings

class Xine(object):
    """The 'Xine' video player engine.
    """
    def __init__(self, config={}, cfg_filename=None):
        """Create and initialize the xine engine.

        You can specify (initial) xine configuration values.

        Examples:

            import pyxine
            import os, os.path

            # To read config from ~/.xine/config2
            xine = pyxine.Xine(
                cfg_filename=os.path.join(os.environ['HOME'],
                                          '.xine/config2'))

            # To explicitly specify some config values:
            xine = pyxine.Xine({'misc.memcpy_method': 'mmx',
                                'input.dvd_region': 2})
        """
        self.this = libxine.xine_new()

        for k,v in config.items():
            libxine.xine_config_register_string(self.this, k, str(v),
                                                "", "", 0, None)

        self.cfg_filename = cfg_filename
        if cfg_filename is not None:
            libxine.xine_config_load(self.this, cfg_filename)

        libxine.xine_init(self.this)

    def __get_config(self):
        """Xine configuration accessor.

        See pyxine.config.XineConfig for details.
        """
        from pyxine import config
        return config.XineConfig(self)
    config = property(__get_config)

    def __del__(self):
        libxine.xine_exit(self.this)
        print "Xine deleted"

        
    def open_audio_driver(self, id=None, data="NULL"):
        """Initialize an audio output driver.
        
        FIXME: more
        """
        return AudioPort(self, 
                         libxine.xine_open_audio_driver(self.this, id, data),
                         data=data)

    def open_video_driver(self, id=None, visual=None, data="NULL"):
        """Initialize a video output driver.
        
        FIXME: more
        """
        try:
            datap = data.get_xine_x11_visual()
            default_visual = "X11"
        except AttributeError:
            datap = data
            default_visual = "NONE"

        if visual is None:
            visual = default_visual

        visual = constwrap.XINE_VISUAL_TYPE(visual)

        return VideoPort(self,
                         libxine.xine_open_video_driver(self.this, id, visual, datap),
                         data=data)

    def stream_new(self, ao=None, vo=None):
        """Create a new 'Stream'.

        The stream will be initialized to play through the specified
        audio and video output drivers.
        """
        if ao is None:
            ao = self.open_audio_driver()
        if vo is None:
            vo = self.open_video_driver()
        return Stream(self, ao, vo,
                      libxine.xine_stream_new(self.this, ao.this, vo.this))

    def get_browsable_input_plugin_ids(self):
        """Get a list of browsable input plugins.
        
        Returns a sequence of plugin ids (strings).
        """
        return libxine.xine_get_browsable_input_plugin_ids(self.this)

    def get_autoplay_input_plugin_ids(self):
        """Get a list of input plugins which support the autoplay feature

        (whatever that is...)

        Returns a sequence of plugin ids (strings).
        """
        return libxine.xine_get_autoplay_input_plugin_ids(self.this)

    def get_file_extensions(self):
        """Get list of recognized file extensions.
        """
        return libxine.xine_get_file_extensions(self.this).split(' ')
    
    def get_mime_types(self):
        """Get list of recognized MIME types.

        Returns a dict whose keys are the recognized MIME types.
        The values of the returned dict are themselves dicts, each
        with two items:

          'extensions' -- which contains a list of filename extensions
            associated with the given type.
            
          'description' -- A textual description of the type.
        """
        d = {}
        for str in filter(None, libxine.xine_get_mime_types(self.this).split(';')):
            try:
                mimetype = MimeTypeInfo(str)
                d[mimetype.type] = mimetype
            except ValueError:
                warnings.warn("Bad MIME type: '%s'" % str)
        return d

    def get_demux_for_mime_type(self, mime_type):
        """Get the demuxer id which handles a given MIME type.

        Returns 'None' if there is no demuxer for the specified type.
        """
        return libxine.xine_get_demux_for_mime_type(self.this, mime_type)
        
    def get_input_plugin_description(self, plugin_id):
        """Get description of input plugin.
        """
        return libxine.xine_get_input_plugin_description(self.this, plugin_id)

    def list_audio_output_plugins(self):
        """List available audio output plugins.

        Returns a tuple of plugin ids (strings).
        """
        return libxine.xine_list_audio_output_plugins(self.this)
    
    def list_video_output_plugins(self):
        """List available video output plugins.

        Returns a tuple of plugin ids (strings).
        """
        return libxine.xine_list_video_output_plugins(self.this)

    def list_post_plugins(self, type=None):
        """List available post(-processing) plugins.

        Returns a tuple of plugin ids (strings).
        
        The optional argument 'type' can be give as one of:
        'VIDEO_FILTER', 'VIDEO_VISUALIZATION', 'AUDIO_FILTER',
        or 'AUDIO_VISUALIZATION' to limit the returned list
        to the specified type.
        """
        if type is not None:
            type = constwrap.XINE_POST_TYPE(type)
            return libxine.xine_list_post_plugins_typed(self.this, type)
        else:
            return libxine.xine_list_post_plugins(self.this)

    def get_log_names(self):
        """Get the names of the log buffers.
        """
        return libxine.xine_get_log_names(self.this)

    def __log_buf(self, buf):
        try:
            return int(buf)
        except ValueError:
            return list(self.get_log_names()).index(buf)
        
    def log(self, buf, *args):
        """Write a log message to a log buffer.
        """
        libxine.xine_log(self.this,
                         self.__log_buf(buf),
                         ' '.join(map(str, args)))
        
    def get_log(self, buf):
        """Retrieve messages from a log buffer.
        """
        return libxine.xine_get_log(self.this, self.__log_buf(buf))

    def register_log_cb(self, callback):
        """Register a log callback function.

        Note: This is unsupported as of libxine 1 beta4 (January, 2003)
        """
        libxine.xine_register_log_cb(self.this, callback)

            
class AudioPort:
    def __init__(self, xine, port, data=None):
        self.this, self.xine, self.data = port, xine, data

    def __del__(self):
        libxine.xine_close_audio_driver(self.xine.this, self.this)
        print "AudioPort deleted"

class VideoPort:
    def __init__(self, xine, port, data=None):
        self.this, self.xine, self.data = port, xine, data

    def __del__(self):
        libxine.xine_close_video_driver(self.xine.this, self.this)
        print "VideoPort deleted"

class MimeTypeInfo:
    def __init__(self, str):
        import re
        type, exts, desc = str.split(':')
        self.type = type.strip()
        self.extensions = map(lambda s: s.strip(), exts.split(','))
        self.description = desc.strip()

    def __str__(self):
        return ": ".join((self.type,
                          ", ".join(self.extensions),
                          self.description))

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, str(self))
        

################################################################
# class Stream    

class _param(property):
        
    def __init__(self, key, wrapper=int):
        key = constwrap.XINE_PARAM(key)
        def fget(stream):
            return wrapper(libxine.xine_get_param(stream.this, key))
        def fset(stream, val):
            libxine.xine_set_param(stream.this, key, wrapper(val))
        property.__init__(self, fget, fset)
        # FIXME: why can't I set this through property.__init__?
        self.__doc__ = "Stream parameter %s" % key

class _stream_info(property):
    def __init__(self, key):
        key = constwrap.XINE_STREAM_INFO(key)
        def fget(self):
            return libxine.xine_get_stream_info(self.this, key)
        property.__init__(self, fget)
        self.__doc__ = "Stream info %s" % key

class _meta_info(property):
    def __init__(self, key):
        key = constwrap.XINE_META_INFO(key)
        def fget(self):
            return libxine.xine_get_meta_info(self.this, key)
        property.__init__(self, fget)
        self.__doc__ = "Stream meta-info %s" % key

class _Stream_EventStream:
    class Error(Exception): pass
    
    def __init__(self, visual, stream):
        try:
            self.direct_events_to = visual.direct_events_to
        except AttributeError:
            raise self.Error
        self.direct_events_to(stream)

    def __del__(self):
        if hasattr(self, 'direct_events_to'):
            self.direct_events_to()
            
        
class Stream(object):

    __slots__ = [ 'xine', 'ao', 'vo', 'this', '_dest', 'estream', '__weakref__' ]

    def __init__(self, xine, ao, vo, streamptr):
        self.xine, self.ao, self.vo, self.this = xine, ao, vo, streamptr
        self._dest = {}
        try:
            self.estream = _Stream_EventStream(vo.data, self)
        except _Stream_EventStream.Error:
            self.estream = None
            
    def __del__(self):
        # FIXME: we get hung here sometimes, particularly when
        #  the movie has not completely starting playing...
        print "deleting Stream"
        #self.stop()
        del self.estream
        libxine.xine_dispose(self.this)
        print "Stream deleted"

    def __raise_error(self):
        raise StreamError, libxine.xine_get_error(self.this)

    def open(self, mrl):
        """Open a stream.

        Look for input, demux, and decoder plugins, find out about the format,
        see if it is supported, set up internal buffers and threads.

        Raises pyxine.StreamError upon failure.
        """
        if not libxine.xine_open(self.this, mrl):
            self.__raise_error()

    def play(self, start_pos=0, start_time=0):
        """Play a stream from a given position.

        To start playing a other than the beginning of the stream,
        specify either 'start_pos' (0..100: percentage of the way
        through the stream), or 'start_time' (in seconds).

        Raises pyxine.StreamError upon failure.
        """
        if start_pos:
            start_pos = int(start_pos * 655.36)
            start_time = 0
        else:
            start_time = int(start_time * 1000)
            
        if not libxine.xine_play(self.this, start_pos, start_time):
            self.__raise_error()

    def trick_mode(self, mode, value):
        """Set xine to a *trick* mode.

        Set xine to a *trick* mode for fast forward, backwards playback,
        low latency seeking. Please note that this works only with some
        input plugins. (In fact, as of libxine 1beta4 (Jan, 2003) this
        is not supported at all.)

        'Mode' can be one of:
          - 'OFF'
          - 'SEEK_TO_POSITION'
          - 'SEEK_TO_TIME'
          - 'FAST_FORWARD'
          - 'FAST_REWIND'

        Raises StreamError upon failure.
        """
        mode = constwrap.XINE_TRICK_MODE(mode)
        if not libxine.xine_trick_mode(self.this, mode, value):
            self.__raise_error()

    def stop(self):
        """Stop stream playback.

        Stream stays valid for new open() or play().
        """
        libxine.xine_stop(self.this)

    def close(self):
        """Stop stream playback, free all stream-related resource.

        Stream stays valid for new open().
        """
        libxine.xine_close(self.this)

    def eject(self):
        """Ask current/recent input plugin to eject media

        This may or may not work, depending on input plugin capabilities
        """
        libxine.xine_eject(self.this)

    def get_status(self):
        """Get current xine engine status.

        Returns one of:
            'XINE_STATUS_IDLE' -- No MRL assigned
            'XINE_STATUS_STOP'
            'XINE_STATUS_PLAY'
            'XINE_STATUS_QUIT'

        Actually, as of libxine 1beta4, 'XINE_STATUS_STOP' and
        'XINE_STATUS_PLAY' seem to be the only values you'll ever
        see.  'XINE_STATUS_IDLE' is never used, and 'XINE_STATUS_QUIT'
        is only used inside the stream destructor.
        """
        return constwrap.XINE_STATUS(
            libxine.xine_get_status(self.this))

    def get_audio_lang(self, channel=-1):
        """Try to find out language of an audio channel.

        Use -1 (the default) for current channel.
        This may raise pyxine.Error if unsuccessful.
        """
        return libxine.xine_get_audio_lang(self.this, channel)

    def get_spu_lang(self, channel=-1):
        """Try to find out language of an SPU channel.

        Use -1 (the default) for current channel.
        This may raise pyxine.Error if unsuccessful.
        """
        return libxine.xine_get_spu_lang(self.this, channel)

    def get_pos_length(self):
        """Get position / length information.

        Returns a triple of:
            - 'pos_stream' (0..100)
            - 'pos_time' (seconds)
            - 'length_time' (seconds)
        
        Depending of the nature and system layer of the stream,
        some or all of this information may be unavailable or incorrect
        (e.g. live network streams may not have a valid length)

        Raises pyxine.Error on failure (probably because data
        is not known yet... try again later)
        """
        pos_stream, pos_time, length_time = \
                    libxine.xine_get_pos_length(self.this)
        pos_stream = pos_stream /655.36
        pos_time = pos_time / 1000.0
        length_time = length_time / 1000.0
        return (pos_stream, pos_time, length_time)

    def send_input_event(self, type, button=0, x=0, y=0):
        """Send an event to the stream.

        All listeners on the stream will get the event.

        Currently, you can only send input events (type XINE_EVENT_INPUT_*).
        """
        import event
        e = event.InputEvent(type, button=button, x=x, y=y)
        libxine.xine_event_send(self.this, e.this)
    
    def new_event_queue(self):
        """Create a new EventQueue to receive events from this stream.
        """
        from pyxine import event
        return event.EventQueue(self,
                                libxine.xine_event_new_queue(self.this))

    def new_event_listener(self, callback):
        """Create a new listener thread to receive events from this tream.

        ALERT: We hold a reference to your callback.
        If it is, e.g. a bound method, you may have problems
        with garbage collection not happening at the right times.
        You can fix this by using a weakly bound method (see
        weakmethod.)
        """
        from pyxine import event
        return event.ListenerThread(self,
                                    libxine.xine_event_new_queue(self.this),
                                    callback)

    def get_video_source(self):
        """Get video source for the stream.

        Use this to rewire the video into post plugins.
        """
        from pyxine import post
        return post.PostOutput(self, libxine.xine_get_video_source(self.this))

    def get_audio_source(self):
        """Get audio source for the stream.

        Use this to rewire the video into post plugins.
        """
        from pyxine import post
        return post.PostOutput(self, libxine.xine_get_audio_source(self.this))
    
    # FIXME:
    # get_current_frame()
    # get_video_frame()

    # FIXME:
    def send_vo_data (self, type, data):
        type = constwrap.XINE_GUI_SEND(type)

        if type == constants.XINE_GUI_SEND_COMPLETION_EVENT:
            event = _XEvent(data)
            packed = event._ptr()
        elif type == constants.XINE_GUI_SEND_DRAWABLE_CHANGED:
            packed = _int2void_p(data.get('id', data))
        elif type == constants.XINE_GUI_SEND_EXPOSE_EVENT:
            event = _XEvent(data)
            packed = event._ptr()
        elif type == constants.XINE_GUI_SEND_VIDEOWIN_VISIBLE:
            packed = _int2void_p(data)
        else:
            raise Exception, "%s not supported" % type

        # FIXME: how to interpret return code?
        # (seems to be 0 if request recognized,
        #  somewhat random otherwise)...
        return libxine.xine_gui_send_vo_data(self.this, type, packed)


    # Stream parameters, and (meta-)info are accessible as properties
    #
    # e.g.
    #
    #    print "speed is", stream.speed
    #
    #    stream.audio_mute = 1

    # Parameters
    locals().update(dict(map(lambda key: (key.lower(), _param(key)),
                             constwrap.XINE_PARAM)))

    speed		= _param(constants.XINE_PARAM_SPEED,
                                 constwrap.XINE_SPEED)
    vo_aspect_ratio	= _param(constants.XINE_PARAM_VO_ASPECT_RATIO,
                                 constwrap.XINE_VO_ASPECT)

    # Stream info
    locals().update(dict(map(lambda key: (key.lower(), _stream_info(key)),
                             constwrap.XINE_STREAM_INFO)))
    # Meta info
    locals().update(dict(map(lambda key: (key.lower(), _meta_info(key)),
                             constwrap.XINE_META_INFO)))
    
    # Other miscellaneous properties as alternatives to the get_*() methods
    status		= property(get_status,
                                   doc="""Current stream status.

                                   See documentation for method get_status.
                                   """)
    audio_source	= property(get_audio_source,
                                   doc="""Current audio source for stream.

                                   See documentation for method get_audio_source.
                                   """)
    video_source	= property(get_video_source,
                                   doc="""Current video source for stream.

                                   See documentation for method get_video_source.
                                   """)
    
#FIXME: clean this up...

def _int2void_p (val):
    return "_%x_void_p" % val

import struct

class _XEvent:
    _size = 24 * len(struct.pack("l", 0))
    
    def __init__(self, e):
        type = e.type
        
        # The XAnyEvent structure
        data = struct.pack("iLiPL",
                           type,
                           e.sequence_number, # long unsigned serial
                           e.send_event, # Bool send_event
                           0, # FIXME: HACK: Display * display
                           e.window.id) # Window window

        # XINE_GUI_SEND_COMPLETION_EVENT wants an XShmCompletionEvent,
        # but doesn't seem to use anything but the window id (drawable).

        # XINE_GUI_SEND_EXPOSE_EVENT wants an XExposeEvent.
        # It uses count
        from Xlib import X              # FIXME
        if type == X.Expose:
            data += struct.pack("iiiii",
                                e.x, e.y, e.width, e.height, e.count)

        pad = self._size - len(data)
        assert pad >= 0
        data += "\0" * pad
            
        self.data = data

    def _ptr (self):
        return libxine.rawmem(self.data)
    

