#!/usr/bin/env python

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

"""Demo pyxine player.

Note that, at present, tkplayer.py is slightly more polished than this one.
"""
from Xlib import X, Xutil, threaded, display, XK

import pyxine

import sys, os, os.path

XINECFG = os.path.join(os.environ['HOME'], '.xine/config2')
LOGO = "/usr/share/xine/skins/xine-ui_logo.mpv"

class Display(display.Display):

    def __init__(self, display_name=""):
        if not display_name:
            display_name = os.environ['DISPLAY']
        display.Display.__init__(self, display_name)

        self.WM_DELETE_WINDOW = self.intern_atom('WM_DELETE_WINDOW')
        self.WM_PROTOCOLS = self.intern_atom('WM_PROTOCOLS')

class Window:
    def __init__(self, display):
        self.display = display
        self.screen = display.screen()
        self.colormap = self.screen.default_colormap
        bg = self.colormap.alloc_named_color("gray10").pixel
        self.window = self.screen.root.create_window(
            50, 50, 600, 400, 0,
            self.screen.root_depth,
            X.InputOutput,
            X.CopyFromParent,

            # special attribute values
            background_pixel = bg,
            event_mask = (#X.ExposureMask |
                          X.StructureNotifyMask),
            colormap = self.colormap
            )
        
        
        self.window.set_wm_name('Pyxine')
        self.window.set_wm_icon_name('Pyxine')
        self.window.set_wm_class('pyxine', 'PyXine')

        self.window.set_wm_protocols([display.WM_DELETE_WINDOW])
        self.window.set_wm_hints(flags = Xutil.StateHint,
                                 initial_state = Xutil.NormalState)
        self.window.set_wm_normal_hints(flags = (Xutil.PPosition | Xutil.PSize | Xutil.PMinSize),
                                        min_width = 20,
                                        min_height = 20)

        # Map the window, making it visible
        self.window.map()

        # Wait for window to map.
        # FIXME: is this right?
        while 1:
            e = display.next_event()
            if e.type == X.MapNotify:
                break

        self.xine_visual = pyxine.XlibDrawable(self.window)

class Player:
    def __init__(self, window):
        xine = pyxine.Xine(cfg_filename=XINECFG)
        ao = xine.open_audio_driver()
        vo = xine.open_video_driver(data=window.xine_visual)
        #vo = xine.open_video_driver("xv", visual="X11", data=vis)
        stream = xine.stream_new(ao, vo)
        self.stream = stream
        self.play(LOGO)
    
    def play(self, mrl, pos=0, time=0):
        stream = self.stream
        stream.open(mrl)
        if stream.has_video:
            self.degoomify()
        else:
            self.goomify()
        stream.play(pos, time)

    def stop(self):
        self.stream.stop()
        
    def pause(self):
        stream = self.stream
        if stream.speed == "NORMAL":
            stream.speed = "PAUSE"
        else:
            stream.speed = "NORMAL"

    def degoomify(self):
        stream = self.stream
        stream.audio_source.wire(stream.ao)

    def goomify(self):
        stream = self.stream
        from pyxine import post
        goom = post.Post(stream, "goom",
                         audio_target=stream.ao,
                         video_target=stream.vo)
        stream.audio_source.wire(goom.inputs["audio in"])


class Quit(Exception):
    pass

class Main:

    def __init__(self):
        self.display = Display()
        self.window = Window(self.display)
        self.player = Player(self.window)

        self.playlist = sys.argv[1:]
        
        self.window.window.change_attributes(
            event_mask=(X.StructureNotifyMask
                        | X.KeyPressMask))

        try:
            while 1:
                e = self.display.next_event()
                print "X11 EVENT", e
                self.handle_event(e)
        except Quit:
            pass

    def handle_event(self, e):
        if e.type == X.DestroyNotify:
            raise Quit
        elif e.type == X.ClientMessage:
            self.handle_ClientMessage(e)
        elif e.type == X.KeyPress:
            self.handle_KeyPress(e)

    _actions = {
        XK.XK_Page_Down:'play_next',
        XK.XK_Page_Up:	'play_prev',
        XK.XK_Return:	'play',
        XK.XK_p:	'play',
        XK.XK_q:	'quit',
        XK.XK_s:	'stop',
        XK.XK_space:	'pause',
        }
            
    def handle_KeyPress(self, e):
        display = self.display
        keycode = display.keycode_to_keysym(e.detail ,0)

        action = self._actions.get(keycode)
        if action:
            print "ACTION", action
            getattr(self, action)()
        else:
            print "KEYCODE", keycode

    def quit(self):
        raise Quit

    def play(self):
        self.player.play(self.playlist[0])

    def stop(self):
        self.player.stop()

    def pause(self):
        self.player.pause()
        
    def play_next(self):
        self.playlist.append(self.playlist.pop(0))
        self.play()
        
    def play_prev(self):
        self.playlist.insert(0, self.playlist.pop())
        self.play()
        
    def handle_ClientMessage(self, e):
        if e.client_type == window.WM_PROTOCOLS:
            fmt, data = e.data
            if fmt == 32 and data[0] == window.WM_DELETE_WINDOW:
                raise Quit

    
if __name__ == '__main__':
    Main()
