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

#ifndef _PxWindow_H
#define _PxWindow_H

extern "C" {
//# include <X11/Xlib.h>
# include <xine.h>  
}

#include <map>

#include "pxlib.h"
#include "Mutex.h"
#include "Thread.h"
#include "Geometry.h"
#include "XDisplay.h"
#include "Callback.h"
#include "WindowList.h"

#ifndef SWIG

BEGIN_PXLIB_NAMESPACE

extern "C" {
  typedef void c_dest_size_cb_t (void *user_data,
				 int video_width, int video_height,
				 double video_pixel_aspect,
				 int *dest_width, int *dest_height,
				 double *dest_pixel_aspect);

  typedef void c_frame_output_cb_t (void *user_data,
				    int video_width, int video_height,
				    double video_pixel_aspect,
				    int *dest_x, int *dest_y,
				    int *dest_width, int *dest_height,
				    double *dest_pixel_aspect,
				    int *win_x, int *win_y);
}
#endif // !SWIG

class PxWindow;

typedef CachedPythonCallback<VideoGeometry,VideoGeometry> DestSizeCallback;
typedef CachedPythonCallback<VideoGeometry,VideoOutputGeometry> FrameOutputCallback;

////////////////////////////////////////////////////////////////

class PxDisplay
  : public XDisplay, private Thread
{
  WindowList	windows;
  ThreadRunner	event_thread;
  
  LockedWindowPtr find_window (Window window) { return windows.find(window); }

#ifndef SWIG  
  PxDisplay(const PxDisplay&);	// not allowed
  PxDisplay& operator= (const PxDisplay&); // not allowed
#endif // !SWIG

public:
  PxDisplay(const char * display_name);
  virtual ~PxDisplay();

  bool has_windows();
  
#ifndef SWIG
  void add_window (PxWindow * w) { windows.add(w); }
  void remove_window (PxWindow * w) { windows.remove(w); }

  virtual void run ();		// the event loop
#endif // !defined(SWIG)
};

////////////////////////////////////////////////////////////////

class PxWindow
  : public Mutex
{
#ifndef SWIG  
  struct XineVisual
    : public x11_visual_t
  {
    XineVisual(XDisplay& _display, Window window, PxWindow *pxwindow);
  };
#endif
  
  PxDisplay&	display;
  Window	window;
  const int	SHM_COMPLETION;
  
  atomic<xine_stream_t *> stream;  /* Stream to which to report events */
  const XineVisual	xine_visual;

  atomic<WindowGeometry> window_geometry;

  DestSizeCallback	dest_size_cb;
  FrameOutputCallback	frame_output_cb;

  int			verbosity;
  
#ifndef SWIG  
  PxWindow(const PxWindow&);	// not allowed
  PxWindow& operator= (const PxWindow&); // not allowed
#endif

  static c_dest_size_cb_t	c_dest_size_cb;
  static c_frame_output_cb_t	c_frame_output_cb;
  
public:
  PxWindow(PxDisplay * display, Window window,
	   PyObject *py_dest_size_cb, PyObject *py_frame_output_cb);

  ~PxWindow();

  PyObject * get_window_geometry () const;
  const x11_visual_t * get_xine_x11_visual () const;
  void set_xine_stream (xine_stream_t * s);
  int get_verbosity () const;
  void set_verbosity (int verbosity);
  double get_pixel_aspect () const;
  void invalidate_cache() const;

#ifndef SWIG  
  void _handle_event (XEvent * e);
  
  operator Window () const { return window; }
#endif // !defined(SWIG)
};

#ifndef SWIG
END_PXLIB_NAMESPACE
#endif // !SWIG

#endif // !_PxWindow_H
