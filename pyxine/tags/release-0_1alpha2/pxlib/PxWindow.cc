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
#include "PxWindow.h"

#include "Traits.h"

BEGIN_PXLIB_NAMESPACE

PxDisplay::PxDisplay(const char * display_name)
  : XDisplay(display_name),
    event_thread(this)
{}

PxDisplay::~PxDisplay()
{
  if (has_windows())
    cerr << "Deleting PxDisplay which still has managed windows" << endl;
}

bool
PxDisplay::has_windows ()
{
  return ! windows.empty();
}

void 
PxDisplay::run ()
{
  XEvent xev;
  
  cerr << "Event Thread started for '" << get_name() << "'" << endl;
  
  while (1) {
    next_event(&xev);

    LockedWindowPtr w = find_window(xev.xany.window);
    if (w)
      w->_handle_event(&xev);
  }
}

////////////////////////////////////////////////////////////////

PxWindow::XineVisual::XineVisual(XDisplay& _display, Window window, PxWindow *pxwindow)
{
  display = _display;
  d = window;
  screen = _display.get_screen_number_of_window(window);
  user_data = static_cast<void *>(pxwindow);
  dest_size_cb = PxWindow::c_dest_size_cb;
  frame_output_cb = PxWindow::c_frame_output_cb;
}

PxWindow::PxWindow(PxDisplay * _display, Window _window,
		   PyObject * _dest_size_cb, PyObject * _frame_output_cb)
  : display(*_display),
    window(_window),
    SHM_COMPLETION(_display->get_ShmCompletionEvent_type()),
    stream(0),
    xine_visual(*_display, _window, this),
    dest_size_cb(_dest_size_cb, "dest_size_cb"),
    frame_output_cb(_frame_output_cb, "frame_output_cb"),
    verbosity(0)
{
  // Get window geometry after selecting StructureNotify events
  MutexLock lock(this);
  display.add_window(this);
  display.select_input(window, ExposureMask | StructureNotifyMask);
  window_geometry = display.get_window_geometry(window);
}

PxWindow::~PxWindow()
{
  display.remove_window(this);
  //MutexLock lock(this);
  display.select_input(window, NoEventMask);
}

const x11_visual_t *
PxWindow::get_xine_x11_visual () const
{
  return &xine_visual;
}
  
void
PxWindow::set_xine_stream (xine_stream_t * s)
{
  stream = s;
}

void
PxWindow::set_verbosity (int _verbosity)
{
  verbosity = _verbosity;
}

int
PxWindow::get_verbosity () const
{
  return verbosity;
}

double
PxWindow::get_pixel_aspect () const
{
  int screen = display.get_screen_number_of_window(window);
  return display.get_pixel_aspect(screen);
}

void
PxWindow::invalidate_cache() const
{
  dest_size_cb.invalidate_cache();
  frame_output_cb.invalidate_cache();
}

void
PxWindow::_handle_event(XEvent * e)
{
  xine_stream_t * stream = this->stream; // atomic copy
  
  if (e->type == SHM_COMPLETION) {
    if (stream)
      xine_gui_send_vo_data(stream, XINE_GUI_SEND_COMPLETION_EVENT,
			    static_cast<void *>(e));
    if (verbosity > 2)
      cerr << "Got ShmCompletionEvent" << endl;
    return;
  }
  
  switch (e->type) {
  case Expose:
    if (stream)
      xine_gui_send_vo_data(stream, XINE_GUI_SEND_EXPOSE_EVENT,
			    static_cast<void *>(e));
    if (verbosity > 1)
      cerr << "Got ExposeEvent" << endl;
    break;
  case ConfigureNotify:
    {
      WindowGeometry new_geometry( display.get_window_geometry(e->xconfigure) );
      if (window_geometry.update(new_geometry))
	invalidate_cache();

      if (verbosity > 1)
	cerr << "Got ConfigureNotify: " << str(new_geometry) << endl;
    }
    break;
  case MapNotify:
    // This seems not to be used by any X11 xine video output drivers,
    // but, what the hell?
    if (stream)
      xine_gui_send_vo_data(stream, XINE_GUI_SEND_VIDEOWIN_VISIBLE,
			    reinterpret_cast<void*>(1));
    if (verbosity > 1)
      cerr << "Got MapNotify" << endl;
    break;
  case UnmapNotify:
    // This seems not to be used by any X11 xine video output drivers,
    // but, what the hell?
    if (stream)
      xine_gui_send_vo_data(stream, XINE_GUI_SEND_VIDEOWIN_VISIBLE,
			    reinterpret_cast<void*>(0));
    if (verbosity > 1)
      cerr << "Got UnmapNotify" << endl;
    break;
  default:
    if (verbosity > 0)
      cerr << "Got unhandled event: type = " << e->type << endl;
    break;
  }
}
    
PyObject *
PxWindow::get_window_geometry () const
{
  return pack_tuple(WindowGeometry(window_geometry));
}

void
PxWindow::c_dest_size_cb (void *user_data,
			  int video_width, int video_height,
			  double video_pixel_aspect,
			  int *dest_width, int *dest_height,
			  double *dest_pixel_aspect)
{
  PxWindow * self = static_cast<PxWindow *>(user_data);

  VideoGeometry input(video_width, video_height, video_pixel_aspect);
  VideoGeometry output;
  try {
    output = self->dest_size_cb(input, self->verbosity);
  }
  catch (Error e) {
    cerr << "Exception during callback: " << e << endl;
  }
  *dest_width = output.width;
  *dest_height = output.height;
  *dest_pixel_aspect = output.pixel_aspect;
}

void
PxWindow::c_frame_output_cb (void *user_data,
			     int video_width, int video_height,
			     double video_pixel_aspect,
			     int *dest_x, int *dest_y,
			     int *dest_width, int *dest_height,
			     double *dest_pixel_aspect,
			     int *win_x, int *win_y)
{
  PxWindow * self = static_cast<PxWindow *>(user_data);

  VideoGeometry input(video_width, video_height, video_pixel_aspect);
  VideoOutputGeometry output;
  try {
    output = self->frame_output_cb(input, self->verbosity);
  }
  catch (Error e) {
    cerr << "Exception during callback: " << e << endl;
  }
  *dest_x = output.dest_x;
  *dest_y = output.dest_y;
  *dest_width = output.width;
  *dest_height = output.height;
  *dest_pixel_aspect = output.pixel_aspect;
  *win_x = output.win_x;
  *win_y = output.win_y;
}

END_PXLIB_NAMESPACE
