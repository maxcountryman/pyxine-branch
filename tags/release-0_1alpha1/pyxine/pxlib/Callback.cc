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
#include "Callback.h"

BEGIN_PXLIB_NAMESPACE

////////////////////////////////////////////////////////////////

PythonObject::PythonObject (PyObject * object, bool owned)
  : ptr(object)
{
  if (!object) throw PythonException();
  if (!owned) { Py_INCREF(ptr); }
}

PythonObject::PythonObject (const PythonObject& that)
  : ptr(that.ptr)
{
  if (ptr) { Py_INCREF(ptr); }
}
  
PythonObject&
PythonObject::operator= (const PythonObject& that)
{
  if (ptr) { Py_DECREF(ptr); }
  ptr = that.ptr;
  if (ptr) { Py_INCREF(ptr); }
  return *this;
}
  
PythonObject::~PythonObject()
{
  if (ptr) { Py_DECREF(ptr); }
}
  

////////////////////////////////////////////////////////////////

PythonContext::rep_t::rep_t()
  : ref_cnt(1)
{
  // You must call this from a python thread.
  PyEval_InitThreads();
  state = PyThreadState_New(PyThreadState_Get()->interp);
  if (!state)
    throw Error("PyThreadState_New failed");
  cerr.form("NEW PyThreadState: %p\n", state);
  PyThreadState_Clear(state);
}

PythonContext::rep_t::~rep_t()
{
  cerr.form("DELETE PyThreadState: %p\n", state);
  PyThreadState_Delete(state);
}

PythonContext::PythonContext()
  : rep(new rep_t)		// You must call this from a python thread.
{}

PythonContext::PythonContext(const PythonContext& c)
  : rep(c.rep)
{
  rep->ref_cnt++;
}

PythonContext::PythonContext&
PythonContext::operator=(const PythonContext& c)
{
  if (--rep->ref_cnt == 0)
    delete rep;
  rep = c.rep;
  rep->ref_cnt++;
  return *this;
}

PythonContext::~PythonContext ()
{
  if (--rep->ref_cnt == 0)
    delete rep;
}

////////////////////////////////////////////////////////////////

PythonGlobalLock::PythonGlobalLock(PythonContext& _context)
  : mutex_lock(_context),
    context(_context)
{
  // WARNING: You must not be in a python thread when this is called.
  PyEval_AcquireLock();
  saved_state = PyThreadState_Swap(context);
}

PythonGlobalLock::~PythonGlobalLock()
{
  // Report any pending exception
  // (This is redundant.  Exceptions should be reported and clears
  // when (the C++ exception) PythonException is thrown.
  if (PyErr_Occurred())
    PyErr_Print();
  PyThreadState_Swap(saved_state);
  PyThreadState_Clear(context);
  PyEval_ReleaseLock();
}


END_PXLIB_NAMESPACE
