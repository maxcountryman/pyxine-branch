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
#include "Thread.h"

BEGIN_PXLIB_NAMESPACE
void *
ThreadRunner::c_thread_runner (void *data)
{
  static_cast<pyxine::Thread *>(data)->run();
  return 0;
}


ThreadRunner::ThreadRunner (Thread * thread)
{
  pthread_create(&t, NULL, c_thread_runner, thread);
}


ThreadRunner::~ThreadRunner ()
{
  cerr << "Stopping Thread" << endl;
  // FIXME: check for errors
  pthread_cancel(t);
  pthread_join(t, NULL);
  cerr << "Thread stopped" << endl;
}

END_PXLIB_NAMESPACE
