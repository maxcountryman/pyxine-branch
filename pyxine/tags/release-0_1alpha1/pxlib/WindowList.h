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

#ifndef _WindowList_H
#define _WindowList_H

#include <map>

extern "C" {
#include <X11/Xlib.h>
}

#include "pxlib.h"
#include "Mutex.h"


BEGIN_PXLIB_NAMESPACE

class PxWindow;

class LockedWindowPtr
{
  PxWindow * w;
  MutexLock  lock;
  
public:
  LockedWindowPtr (PxWindow * _w);
  operator PxWindow * () { return w; }
  PxWindow* operator-> () { return w; }
  operator bool () { return w; }
};

class WindowList
  : private std::map<Window, PxWindow *>
{
  typedef std::map<Window, PxWindow *> super;

  mutable Mutex	mutex;

public:
  void add (PxWindow * w);
  void remove (PxWindow * w);
  LockedWindowPtr find (Window window);
  bool empty () const;
};

END_PXLIB_NAMESPACE

#endif // !_WindowList_H
