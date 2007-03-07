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
%module pxlib
%{
#include "pxlib.h"
#include "PxWindow.h"
using namespace pyxine;
%}

%typemap (python,in)  PyObject * { $target = $source; }
%typemap (python,out) PyObject * { $target = $source; }

%except(python) {
  try {
    $function;
  }
  catch (Error e) {
    PyErr_SetString(PyExc_Exception, e.get_message());
    return 0;
  }
}

typedef unsigned long Window;

%include "PxWindow.h"
