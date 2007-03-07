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

#ifndef _Callback_H
#define _Callback_H

#include "pxlib.h"
#include "Mutex.h"
#include "Traits.h"

extern "C" {
# include <Python.h>
}

BEGIN_PXLIB_NAMESPACE

class PythonException
  : public Error
{
public:
  PythonException()
    : Error("A python exception occurred.")
  {
    PyErr_Print();
  }
};

////////////////////////////////////////////////////////////////

class PythonObject
{
  PyObject * ptr;

public:
  PythonObject() : ptr(0) {}
  PythonObject(PyObject * object, bool owned=true);
  PythonObject(const PythonObject& that);
  PythonObject& operator= (const PythonObject& that);

  ~PythonObject();

  operator PyObject * () const { return ptr; }
  operator bool () const { return ptr != 0; }
  int refcnt () const { return ptr ? ptr->ob_refcnt : 0; } // debugging
};

////////////////////////////////////////////////////////////////

class PythonContext
{
  struct rep_t {
    int			ref_cnt;
    Mutex		mutex;
    PyThreadState *	state;
    
    rep_t();
    ~rep_t();
  };

  rep_t *	rep;
  
  friend class PythonGlobalLock;
  operator PyThreadState * () const { return rep->state; }
  operator Mutex * () const { return &rep->mutex; }
  
public:
  PythonContext();		// You must call this from a python thread. 
  PythonContext(const PythonContext& c);
  PythonContext& operator=(const PythonContext& c);
  ~PythonContext();
};


class PythonGlobalLock
{
  MutexLock	  mutex_lock;
  PythonContext&  context;
  PyThreadState * saved_state;

public:
  PythonGlobalLock(PythonContext& context); // Never call this from a python thread
  ~PythonGlobalLock();
};

/////////////////////////////////////////////////////////////////////

template<class ArgType, class ReturnType>
class PythonCallback
{
public:
  typedef ReturnType return_type;
  typedef ArgType    arg_type;

private:
  mutable PythonContext	context;
  PythonObject		callback;
  
public:
  PythonCallback(PyObject *callable)
    : callback(callable, false)
  {
    if (!PyCallable_Check(callable))
      throw Error("callback object not callable");
  }

  return_type operator() (const arg_type& arg) const
  {
    PythonGlobalLock s(context);
    PythonObject args = pack_tuple(arg);
    PythonObject retval = PyObject_CallObject(callback, args);
    return Traits<return_type>::unpack_tuple(retval);
  }
};

////////////////////////////////////////////////////////////////

template <class Callback>
class CachedCallback
{
public:
  typedef typename Callback::return_type return_type;
  typedef typename Callback::arg_type arg_type;

private:
  const std::string	name;

  Callback		callback;
  
  mutable Mutex		mutex;
  mutable bool		cache_valid;
  mutable arg_type	cached_arg;
  mutable return_type	cached_retval;

public:
  CachedCallback(const Callback& cb, const char * _name = "")
    : name(_name), callback(cb), cache_valid(false) {}
  
  void invalidate_cache() const
  {
    MutexLock lock(mutex);	// this is paranoia
    cache_valid = false;
  }
  
  return_type operator() (const arg_type& arg, int verbosity = 0) const
  {
    MutexLock lock(mutex);
    if (!cache_valid || cached_arg != arg) {
      if (verbosity > 1)
	cerr << "Calling callback " << name << endl;
      cached_retval = callback(arg);
      cached_arg = arg;
      cache_valid = true;
    }
    else {
      if (verbosity > 2)
	cerr << "Not calling callback " << name << endl;
    }
    return cached_retval;
  }
};


////////////////////////////////////////////////////////////////

template<class ArgType, class ReturnType>
class CachedPythonCallback
  : public CachedCallback<PythonCallback<ArgType, ReturnType> >
{
  typedef CachedCallback<PythonCallback<ArgType, ReturnType> > super;
  
public:
  CachedPythonCallback(PyObject *callable, const char * name="")
    : super(callable, name)
  {}
};

////////////////////////////////////////////////////////////////
END_PXLIB_NAMESPACE
#endif // !Callback_H
