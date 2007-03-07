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
"""Generic higher-level multimedia player support
"""

# FIXME: include a log in the distribution
LOGO = "/usr/share/xine/skins/xine-ui_logo.mpv"

class Player:
    """Mixin which adds higher level player control methods.
    """
    __stream = None
    __listener = None
    __logo = LOGO
    __mrl = None
    
    def __init__(self, stream=None, logo=LOGO):
        self.__logo = logo
        if (stream):
            self.set_stream(stream)

    def set_stream(self, stream):
        self.__stream = stream
        if stream:
            self.__listener = stream.new_event_listener(self.__xine_event_cb)
            self.stop()
        else:
            self.__listener = None

    def __xine_event_cb(self, event):
        if event.type == "FRAME_FORMAT_CHANGE":
            # FIXME:?
            self.frame_format_change(event.data)
        elif event.type == "UI_PLAYBACK_FINISHED":
            self.stop()

    def frame_format_change(self, event_data):
        pass

    def play(self, mrl):
        stream = self.__stream
        stream.close()
        stream.open(mrl)
        self.__mrl = mrl
        if stream.has_video:
            # disconnect any audio visualization post plugin
            stream.audio_source.wire(stream.ao)
        else:
            self.__visualize_audio("goom")
        stream.play()

    def __visualize_audio(self, post_name="goom"):
        stream = self.__stream
        from pyxine import post
        goom = post.Post(stream, post_name,
                         audio_target=stream.ao,
                         video_target=stream.vo)
        stream.audio_source.wire(goom.inputs["audio in"])

    def stop(self):
        stream = self.__stream
        if self.__mrl != self.__logo:
            self.play(self.__logo)

    def pause(self, do_pause="TOGGLE"):
        stream = self.__stream
        if do_pause == "TOGGLE":
            do_pause = stream.speed != "PAUSE"
        stream.speed = do_pause and "PAUSE" or "NORMAL";

    # FIXME: % or secs
    def seek(self, pos):
        stream = self.__stream
        stream.stop()
        stream.play(pos)


    # FIXME: % or secs?
    def seekrel(self, secs):
        stream = self.__stream
        pos = stream.get_pos_length()[1]
        stream.stop()
        stream.play(start_time = pos + secs)

