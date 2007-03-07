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
#pragma interface

#ifndef _XDisplay_H
#define _XDisplay_H


extern "C" {
# include <unistd.h>
# include <sys/types.h>
# include <X11/Xlib.h>
# include <X11/extensions/XShm.h>

  extern int XShmGetEventBase(Display *);
}

#include <string>

#include "pxlib.h"
#include "Geometry.h"

BEGIN_PXLIB_NAMESPACE

extern "C" {
  typedef Bool event_predicate_t (Display *, XEvent *, XPointer);
}

class WindowGeometry;

class XDisplay
{
  std::string	name;
  Display *	display;

  static event_predicate_t pick_any_event;
  bool get_event (XEvent * e);
  
public:
  XDisplay (const char * display_name);
  ~XDisplay ();

  operator Display * () { return display; }
  const std::string& get_name () { return name; }

  int get_screen_number_of_window (Window w);
  double get_pixel_aspect(int screen);
  void select_input (Window w, long event_mask);
  WindowGeometry get_window_geometry (Window w);
  WindowGeometry get_window_geometry (const XConfigureEvent& e);

  int get_ShmCompletionEvent_type() const;
  
  /**
   * We implement our own version of XNextEvent, because
   * the normal one doesn't appear to be completely thread safe.
   * (If thread is cancelled while in XNextEvent, it seems
   * the Display lock is still held... XCloseDisplay hangs)
   */
  void next_event (XEvent * e);
};




END_PXLIB_NAMESPACE

#endif // !_XDisplay_H
