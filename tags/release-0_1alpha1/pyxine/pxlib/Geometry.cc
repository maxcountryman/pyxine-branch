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
#include "Geometry.h"

#include <sstream>
#include <typeinfo>
#include "Traits.h"
#include "Callback.h"

BEGIN_PXLIB_NAMESPACE

VideoGeometry
Traits<VideoGeometry>::unpack_tuple(PyObject * tuple)
{
  VideoGeometry g;

  if (!PyArg_ParseTuple(tuple, "iid:return from dest_size_cb",
			&g.width, &g.height, &g.pixel_aspect))
    throw PythonException();
  return g;
}

PyObject *
Traits<VideoGeometry>::pack_tuple(const VideoGeometry& g)
{
  PyObject * tuple = Py_BuildValue("(iid)",
				   g.width, g.height, g.pixel_aspect);
  if (!tuple)
    throw PythonException();
  return tuple;
}

////////////////////////////////////////////////////////////////

VideoOutputGeometry
Traits<VideoOutputGeometry>::unpack_tuple(PyObject * tuple)
{
  VideoOutputGeometry g;

  if (!PyArg_ParseTuple(tuple, "iiiidii:return from frame_output_cb",
			&g.dest_x, &g.dest_y,
			&g.width, &g.height, &g.pixel_aspect,
			&g.win_x, &g.win_y))
    throw PythonException();
  return g;
}

////////////////////////////////////////////////////////////////

PyObject *
Traits<WindowGeometry>::pack_tuple(const WindowGeometry& g)
{
  PyObject * tuple = Py_BuildValue("(iiiid)",
				   g.width, g.height, g.x0, g.y0, g.pixel_aspect);
  
  if (!tuple)
    throw PythonException();
  return tuple;
}

std::string
Traits<WindowGeometry>::to_string(const WindowGeometry& g)
{
  ostringstream buf;

  buf << "<" << typeid(g).name() << ": "
      << g.width << "x" << g.height
      << "+" << g.x0 << "+" << g.y0
      << " (" << std::setprecision(2) << g.pixel_aspect << ")"
      << ">";

  return buf.str();
}

END_PXLIB_NAMESPACE
