/* -*-c++-*-
 *
 * $Id$
 *
 * Copyright (C) 2003 Geoffrey T. Dairiki
 *
 * This file is part of Pyxine, Python bindings for xine.
 *
 * Pyxine is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * Pyxine is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */
#pragma implementation
#include "XDisplay.h"

BEGIN_PXLIB_NAMESPACE

class XDisplayLock
{
  Display * display;
public:
  XDisplayLock(Display * _d) : display(_d) { XLockDisplay(display); }
  ~XDisplayLock() { XUnlockDisplay(display); }
};

////////////////////////////////////////////////////////////////


XDisplay::XDisplay (const char * display_name)
  : name(XDisplayName(display_name))
{
  static bool seen = false;

  if (!seen) {
    if (!XInitThreads())
      throw Error("Your Xlib doesn't support threads?");
    seen = true;
  }
  
  display = XOpenDisplay(name.c_str());
  if (!display)
    throw Error("Can't open display");
}

XDisplay::~XDisplay ()
{
  //FIXME:cerr << "XDisplay destroy" << endl;
  XDisplayLock lock(display);
  XCloseDisplay(display);
  //FIXME:cerr << "XDisplay destroyed" << endl;
}

Bool
XDisplay::pick_any_event (Display *, XEvent *, XPointer)
{
  return True;
}

bool
XDisplay::get_event (XEvent * e)
{
  XDisplayLock l(display);
  return XCheckIfEvent(display, e, pick_any_event, 0);
}

void
XDisplay::next_event (XEvent * e)
{
  pthread_testcancel();
  while (! get_event(e)) {
    int fd = ConnectionNumber(display);
    fd_set rfds;
    FD_ZERO(&rfds);
    FD_SET(fd, &rfds);
    fd_set efds = rfds;
    select(fd+1, &rfds, 0, &efds, 0);
    pthread_testcancel();
  }
}

int
XDisplay::get_screen_number_of_window (Window w)
{
  XWindowAttributes attr;
  XDisplayLock xlock(display);
  if (!XGetWindowAttributes(display, w, &attr))
    throw Error("XGetWindowAttributes failed");
  return XScreenNumberOfScreen(attr.screen);
}

double
XDisplay::get_pixel_aspect(int screen)
{
  XDisplayLock lock(display);
  double res_h = ( (double)DisplayWidth(display, screen)
		   / DisplayWidthMM(display, screen));
  double res_v = ( (double)DisplayHeight(display, screen)
		   / DisplayHeightMM(display, screen));
  return res_v / res_h;
}
  
WindowGeometry
XDisplay::get_window_geometry(Window w)
{
  WindowGeometry g;
  Window _window;
  unsigned width, height, _border_width, _depth;
  
  XDisplayLock lock(display);

  if (!XGetGeometry(display, w,
		    &_window,
		    &g.x0, &g.y0, &width, &height,
		    &_border_width, &_depth))
    throw Error("XGetGeometry failed");
  
  g.width = width;
  g.height = height;
  
  int screen = get_screen_number_of_window(w);
  g.pixel_aspect = get_pixel_aspect(screen);

  return g;
}

WindowGeometry
XDisplay::get_window_geometry(const XConfigureEvent& e)
{
  WindowGeometry g;
  g.width  = e.width;
  g.height = e.height;

  if (e.display != display)
    cerr << "Warning: event.display != display" << endl;
    
#if 0
  // This doesn't seem to work...
  g.x0 = e.x;
  g.y0 = e.y;
#else
  Window tmp_win;
  XDisplayLock lock(e.display);
  XTranslateCoordinates(e.display, e.window, DefaultRootWindow(e.display),
			0, 0, &g.x0, &g.y0, &tmp_win);
#endif

  int screen = get_screen_number_of_window(e.window);
  g.pixel_aspect = get_pixel_aspect(screen);

  return g;
}

inline void
XDisplay::select_input(Window w, long event_mask)
{
  XDisplayLock xlock(display);
  XSelectInput(display, w, event_mask);
}

int
XDisplay::get_ShmCompletionEvent_type() const
{
  static int SHM_COMPLETION = 0;
  if (SHM_COMPLETION == 0) {
    SHM_COMPLETION = XShmGetEventBase(display) + ShmCompletion;
  }
  return SHM_COMPLETION;
}

END_PXLIB_NAMESPACE
