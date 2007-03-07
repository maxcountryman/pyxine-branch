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

from pyxine import libxine, constants, constwrap, cstruct

class Event(cstruct.xine_event_t):

    _owned = 0

    def __init__(self, _raw, _owned=0):
        cstruct.xine_event_t.__init__(self, _raw)
        self._owned = _owned
        self.__super = cstruct.super(Event, self)
        
    def __get_type(self):
        return constwrap.XINE_EVENT(self.__super.type)
    def __set_type(self, val):
        self.__super.type = constwrap.XINE_EVENT(val)
    type = property(__get_type, __set_type, doc="The event type")

    def __get_data(self):
        data = self.__super.data
        try:
            return self._data_type(data)
        except AttributeError:
            return data
    data = property(__get_data, doc="The event data")
        
    def __del__(self):
        if self._owned:
            libxine.xine_event_free(self.this)
            print "Event freed"

class xine_format_change_data_t(cstruct.xine_format_change_data_t):
    def __init__(self, _raw):
        cstruct.xine_format_change_data_t.__init__(self, _raw)
        self.__super = cstruct.super(xine_format_change_data_t, self)
    
    def __get_aspect(self):
        return constwrap.XINE_VO_ASPECT(self.__super.aspect)
    aspect = property(__get_aspect, doc="The aspect ratio code")

    def get_video_geometry(self, default_aspect=4.0/3.0):
        width, height = self.width, self.height
        video_aspect = self.get_aspect_ratio(default_aspect)
        pixel_aspect = video_aspect * height / width
        return width, height, pixel_aspect
    
    def get_aspect_ratio(self, default=None):
        # FIXME: this may not be right
        aspect = self.aspect
        
        if aspect == "4_3":
            return 4.0 / 3.0
        elif aspect in ("ANAMORPHIC", "PAN_SCAN"):
            return 16.0 / 9.0
        elif aspect == "DVB":
            return 2.11
        elif aspect in ("SQUARE", "DONT_TOUCH"):
            return float(self.width) / float(self.height)
        else:
            return default
        
class UIDataEvent(Event):
    _data_type = cstruct.xine_ui_data_t

class FrameFormatChangeEvent(Event):
    _data_type = xine_format_change_data_t

class AudioLevelEvent(Event):
    _data_type = cstruct.xine_audio_level_data_t

class ProgressEvent(Event):
    _data_type = cstruct.xine_progress_data_t

class InputEvent(Event):

    _data_type = cstruct.xine_input_data_t
    
    def __init__(self, type=None, button=0, x=0, y=0, _raw=None, _owned=0):
        if _raw is None:
            if type is None:
                raise ValueError, "must specify a type"
            # FIXME: check type for validity as XINE_EVENT_INPUT type
            type = constwrap.XINE_EVENT(type)
            _raw = libxine.px_make_input_event(type, button, x, y)
            # This is a PyBuffer and will auto-free itself...
            _owned = 0
        Event.__init__(self, _raw, _owned)


_event_types = {
    constants.XINE_EVENT_UI_SET_TITLE:		UIDataEvent,
    constants.XINE_EVENT_UI_MESSAGE:		UIDataEvent,
    constants.XINE_EVENT_FRAME_FORMAT_CHANGE:	FrameFormatChangeEvent,
    constants.XINE_EVENT_AUDIO_LEVEL:		AudioLevelEvent,
    constants.XINE_EVENT_PROGRESS:		ProgressEvent,
    #constants.XINE_EVENT_INPUT_MOUSE_BUTTON:	InputEvent,
    #constants.XINE_EVENT_INPUT_MOUSE_MOVE:	InputEvent,
    #constants.XINE_EVENT_INPUT_BUTTON_FORCE:	spu_button_t, #???
    }

def _wrap_event(raw, owned=0):
    event = cstruct.xine_event_t(raw)
    if event.data_length == 0:
        # FIXME: check for actual data size needed?
        return Event(_raw=raw, _owned=owned)
    elif constwrap.XINE_EVENT_INPUT.contains(event.type):
        return InputEvent(_raw=raw, _owned=owned)
    else:
        cls = _event_types.get(event.type, Event)
        return cls(_raw=raw, _owned=owned)

    
class EventQueueBase:
    def __init__(self, stream, this):
        self.stream, self.this = stream, this
        
    def __del__(self):
        libxine.xine_event_dispose_queue(self.this)
        print "deleted EventQueue"
        
class EventQueue(EventQueueBase):

    def get(self):
        e = libxine.xine_event_get(self.this)
        if e is None:
            return None
        return _wrap_event(e, owned=1)

    def wait(self):
        e = libxine.xine_event_wait(self.this)
        return _wrap_event(e, owned=1)

class ListenerThread(EventQueueBase):
    """

    ALERT: We hold a reference to your callback.
    If it is, e.g. a bound method, you may have problems
    with garbage collection not happening at the right times.
    You can fix this by using a weakly bound method (see
    weakmethod.)
    """
    def __init__(self, stream, this, callback):
        EventQueueBase.__init__(self, stream, this)

        if not callable(callback):
            raise ValueError, "callback not callable"
            
        def cb_wrap (e):
            callback(_wrap_event(e, owned=0))
            
        libxine.xine_event_create_listener_thread(self.this, cb_wrap)

    
