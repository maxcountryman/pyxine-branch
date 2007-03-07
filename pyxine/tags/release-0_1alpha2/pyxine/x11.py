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

from pyxine import weakmethod, pxlib

import weakref, re

_display_cache = weakref.WeakValueDictionary()

def _canonify_display_name(name):
    # Strip trailing '.<screen number>' (if any) from display name.
    return re.sub(r'\.\d+$', '', name)

def _get_display(name):
    name = _canonify_display_name(name)
    try:
        return _display_cache[name]
    except KeyError:
        display = pxlib.PxDisplay(name)
        _display_cache[name] = display
        return display

class X11Visual(pxlib.PxWindow):
    """A wrapper class for a python-xlib Window

    This class provides a few utility functions needed to allow
    pyxine to output to your python-xlib Window:

     * It starts a (non-python) thread to monitor certain events
       on the window.

       - Window size and position changes are tracked.

       - It provides the plumbing to forward 'Expose', 'ShmCompletion',
         'MapNotify' and 'UnmapNotify' events to the appropriate Stream.

     * It provides the x11_visual_t structure needed as an
       argument to Xine::open_video_driver().

    If you have special requirements you may want to subclass this class,
    and override the 'frame_output_cb' and/or 'dest_size_cb' methods.
    """

    pixel_aspect = 1.0
    
    def __init__(self, display_name, window_id):
        self._pxdisplay = _get_display(display_name)
        pxlib.PxWindow.__init__(self, self._pxdisplay, window_id,
                                self.__dest_size_cb, self.__frame_output_cb)

        self.pixel_aspect = self.get_pixel_aspect()

    def __del__(self):
        try:
            pxlib.PxWindow.__del__(self)
        except AttributeError:
            pass
        print "X11Visual deleted"

    def direct_events_to(self, stream=None):
        """Send window events to stream.

        Specify which 'Stream' window events should be directed to.
        (The events which will be forwarded are 'ShmCompletion',
        'Expose', 'MapNotify', and 'UnmapNotify'.

        When called with no argument, will cause window events to
        be discarded.
        """
        if stream is None:
            stream_p = "NULL"
        else:
            stream_p = stream.this

        pxlib.PxWindow.set_xine_stream(self, stream_p)

    set_xine_stream = direct_events_to
    
    def __dest_size_cb(self, *args):
        return self.dest_size_cb(*args)
    __dest_size_cb = weakmethod.weakmethod(__dest_size_cb)
    
    def __frame_output_cb(self, *args):
        return self.frame_output_cb(*args)
    __frame_output_cb = weakmethod.weakmethod(__frame_output_cb)

    def natural_output_size(self, video_geometry):
        """Compute the natural output size for video.

        This is the output size for ~1:1 enlargement, taking into account
        pixel aspect ratios.
        """
        video_width, video_height, video_pixel_aspect = video_geometry
        try:
            if video_pixel_aspect >= self.pixel_aspect:
                video_width = int(video_width * video_pixel_aspect / self.pixel_aspect + .5)
            else:
                video_height = int(video_height * self.pixel_aspect / video_pixel_aspect + .5)
        except ZeroDivisionError:
            pass                        # punt
        return video_width, video_height

    def compute_output_size(self, video_geometry):
        """Compute the output size for video.

        (You may want to override this method in subclasses.)
        """
        return self.natural_output_size(video_geometry)
    
    def dest_size_cb(self, *video_geometry):
        """Figure out video output size.

        This will be called by the video driver to find out
        how big the video output area size will be for a
        given video size. The ui should _not_ adjust it's
        video out area, just do some calculations and return
        the size.

        Should return a triple ('dest_width', 'dest_height',
        'dest_pixel_aspect').

        This will usually be called only when the video
        dimensions change, or the window size has changed,

        Dest_pixel_aspect should be set to the used display pixel aspect.
        """
        width, height = self.compute_output_size(video_geometry)
        output_geometry = (width, height, self.pixel_aspect)
        print "DEST_SIZE_CB", video_geometry, "->", output_geometry
        return output_geometry


    def frame_output_cb(self, *video_geometry):
        """Figure out and/or adjust video output size.
        
        This will be called by the video driver when it is
        about to draw a frame. The UI can adapt it's size if necessary
        here.

        Note: the UI doesn't have to adjust itself to this
        size, this is just to be taken as a hint.

        This will usually be called only when the video
        dimensions change, or the window size has changed.

        The UI must return the actual size of the video output
        area and the video output driver will do it's best
        to adjust the video frames to that size (while
        preserving aspect ratio and stuff).

            dest_x, dest_y -- offset inside window

            dest_width, dest_height -- available drawing space

            dest_pixel_aspect -- display pixel aspect

            win_x, win_y -- window absolute screen position
        """
        width, height = self.compute_output_size(video_geometry)

        window_geometry = self.get_window_geometry()
        window_size = window_geometry[:2]
        win_x, win_y = window_geometry[2:4]
        
        if (width, height) != window_size:
            newpos = self.resize_window(width, height)
            if newpos:
                win_x, win_y = newpos

        output_geometry = (0,0,
                           width, height, self.pixel_aspect,
                           win_x, win_y)
        print "FRAME_OUTPUT_CB", video_geometry, "->", output_geometry
        return output_geometry

    def resize_window(self, width, height):
        """Resize the video output window.

        Subclasses should override this method.

        It should return the pair (win_x, win_y), or None, if the
        window location is not available.
        """
        return None

class TkWidget(X11Visual):
    """An X11Visual which can be initialized with a Tkinter.Widget.
    """
    def __init__(self, widget):
        X11Visual.__init__(self,
                           widget.winfo_screen(),
                           widget.winfo_id())
            
class XlibDrawable(X11Visual):
    """An X11Visual which can be initialized with an Xlib Drawable.
    """
    def __init__(self, drawable):
        X11Visual.__init__(self,
                           drawable.display.get_display_name(),
                           drawable.id)


