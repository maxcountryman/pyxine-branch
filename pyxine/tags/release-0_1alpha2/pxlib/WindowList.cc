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
#include "WindowList.h"

#include "PxWindow.h"

BEGIN_PXLIB_NAMESPACE

////////////////////////////////////////////////////////////////

LockedWindowPtr::LockedWindowPtr (PxWindow * _w)
  : w(_w)
{
  if (w)
    lock = MutexLock(w);
}

////////////////////////////////////////////////////////////////

void
WindowList::add (PxWindow * w)
{
  MutexLock lock(mutex);
  if (! insert(value_type(Window(*w), w)).second)
    throw Error("window already in list");
}

void
WindowList::remove (PxWindow * w)
{
  MutexLock lock(mutex);
  if (!erase(Window(*w)))
    throw Error("window not in list");
}

LockedWindowPtr
WindowList::find (Window window)
{
  MutexLock lock(mutex);
  iterator i = super::find(window);
  return i == end() ? 0 : i->second;
}

bool
WindowList::empty () const
{
  MutexLock lock(mutex);
  return super::empty();
}

END_PXLIB_NAMESPACE
