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

from Tkinter import *
import pyxine
from pyxine import constwrap
import os, os.path


XINECFG = os.path.join(os.environ['HOME'], '.xine/config2')
LOGO = "/usr/share/xine/skins/xine-ui_logo.mpv"

# Callbacks from pyxine happen asynchronously.
# Tkinter doesn't seem to be thread-safe.
# So we need a mutex to make sure only one thread
# can call the Tkinter at a time.

class RMutex:
    class _Lock:
        def __init__(self, mutex):
            self.mutex = mutex
            mutex._lock.acquire()
        def __del__(self):
            self.mutex._lock.release()

    def __init__(self):
        import threading
        self._lock = threading.RLock()
        
    def __call__(self):
        return RMutex._Lock(self)

theTkMutex = RMutex()


class X11Visual(pyxine.TkWidget):
    def __init__(self, widget):
        pyxine.TkWidget.__init__(self, widget)
        self.widget = widget
        self.set_verbosity(2)
        self.video_geometry = None

    def compute_output_size(self, video_geometry):
        width, height = self.natural_output_size(video_geometry)
        parent = self.widget.master
        scale = max(1.0, min(parent.winfo_height() / float(height),
                             parent.winfo_width() / float(width)))
        return int(width * scale + 0.5), int(height * scale + 0.5)
    
    def resize_window(self, width, height):
        print "RESIZE WINDOW", (width, height)
        win = self.widget
        win.update_idletasks()
        if (width,height) != (win.winfo_width(), win.winfo_height()):
            print "WINDOW RESIZE", (width, height)
            win.config(width=width, height=height, bg="black")
            win.update_idletasks()
            win.config(bg="")

    def dest_size_cb(self, *args):
        lock = theTkMutex()
        return pyxine.TkWidget.dest_size_cb(self, *args)

    def frame_output_cb(self, *args):
        lock = theTkMutex()
        return pyxine.TkWidget.frame_output_cb(self, *args)
    
class Player(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master, bg='gray10', width=100, height=100)

        self.stream = None

        vidwin = Frame(self, bg='')
        vidwin.grid()
        self.grid_propagate(1)
        
        vidwin.bind('<Map>', lambda e: self.open_stream())
        vidwin.bind('<Destroy>', lambda e: self.close_stream())
        self.vidwin = vidwin

    def open_stream(self):
        if self.stream:
            return
        xine = pyxine.Xine(cfg_filename=XINECFG)
        visual = X11Visual(self.vidwin)
        vo = xine.open_video_driver("xv", data=visual)
        stream = xine.stream_new(vo=vo)
        self.listener = stream.new_event_listener(self.xine_event_cb)
        self.stream = stream
        self.visual = visual
        self.play(LOGO)

    def close_stream(self):
        self.listener = None
        self.stream = None
        self.visual = None

    def xine_event_cb(self, event):
        if event.type == "FRAME_FORMAT_CHANGE":
            self.frame_format_change(event.data)
        elif event.type == "UI_PLAYBACK_FINISHED":
            print "PLAYBACK DONE"
            self.stop()
        else:
            print "Unhandled event", event

    def frame_format_change(self, format):
        video_geometry = format.get_video_geometry()
        lock = theTkMutex()
        width, height = self.visual.natural_output_size(video_geometry)
        print video_geometry, '->', (width, height, self.visual.pixel_aspect)

        self.vidwin.config(width=width, height=height)
        top = self.winfo_toplevel()
        top.aspect(width, height, width, height)
        top.minsize(width, height)
        top.update_idletasks()

        fwidth = top.winfo_width() - (self.winfo_width() - self.winfo_reqwidth())
        fheight = top.winfo_height() - (self.winfo_height() - self.winfo_reqheight())
        
        top.geometry("%dx%d" % (fwidth, fheight))
        print "FRAME SIZE CHANGE", (width, height), (fwidth, fheight)
        
    def play(self, mrl):
        stream = self.stream
        stream.close()
        print "OPEN"
        stream.open(mrl)
        self.current_mrl = mrl
        if stream.has_video:
            self.degoomify()
        else:
            self.goomify()
        print "PLAY"
        stream.play()

    def stop(self):
        stream = self.stream
        if self.current_mrl != LOGO:
            self.play(LOGO)
        else:
            self.stream.close()

    def pause(self):
        stream = self.stream
        if stream.speed == "NORMAL":
            stream.speed = "PAUSE"
        else:
            stream.speed = "NORMAL"
        
    def seek(self, pos):
        stream = self.stream
        stream.stop()
        stream.play(pos)

    def seekrel(self, secs):
        stream = self.stream
        pos = stream.get_pos_length()[1]
        stream.stop()
        stream.play(start_time = pos + secs)

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

class Main(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.minsize(100,100)
        self.title("TkPyxine")
        self.config(bg="red")

        self.player = Player(self)
        self.player.pack(fill=BOTH, expand=1)

        self.playlist = sys.argv[1:]

        self.bind("p", lambda e: self.play())
        self.bind("<Return>", lambda e: self.play())
        self.bind("s", lambda e: self.player.stop())
        self.bind("q", lambda e: self.quit())
        self.bind("<space>", lambda e: self.player.pause())
        for d in range(0,10):
            self.bind(str(d), self.seek)
        self.bind("<Right>", lambda e: self.player.seekrel(30))
        self.bind("<Left>", lambda e: self.player.seekrel(-30))
        self.bind("<Page_Up>", lambda e: self.prev())
        self.bind("<Page_Down>", lambda e: self.next())
        
    def play(self):
        print "PLAY"
        self.player.play(self.playlist[0])

    def seek(self, e):
        pos = int(e.char) * 10
        print "SEEK", pos
        self.player.seek(pos)
    
    def next(self):
        head = self.playlist.pop(0)
        self.playlist.append(head)
        self.play()

    def prev(self):
        tail = self.playlist.pop()
        self.playlist.insert(0, tail)
        self.play()
        
def main ():
    root = Main()
    root.mainloop()

if __name__ == '__main__':
    main()
