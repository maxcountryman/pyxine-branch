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

#ifndef _Geometry_H
#define _Geometry_H

#include "pxlib.h"

BEGIN_PXLIB_NAMESPACE


struct VideoGeometry
{
  int		width;
  int		height;
  double	pixel_aspect;

public:
  VideoGeometry() : pixel_aspect(1.0) {}

  VideoGeometry(int w, int h, double pa)
    : width(w), height(h), pixel_aspect(pa)
  {}

  bool operator==(const VideoGeometry& that) const;
  bool operator!=(const VideoGeometry& that) const { return ! (*this == that); }
};

inline bool
VideoGeometry::operator==(const VideoGeometry& that) const
{
  return width == that.width
    && height == that.height
    && pixel_aspect == that.pixel_aspect;
}

////////////////////////////////////////////////////////////////

struct VideoOutputGeometry
{
  int		dest_x, dest_y;
  int		width;
  int		height;
  double	pixel_aspect;
  int		win_x, win_y;

public:
  VideoOutputGeometry() : pixel_aspect(1.0) {}

  bool operator==(const VideoOutputGeometry& that) const;
  bool operator!=(const VideoOutputGeometry& that) const { return ! (*this == that); }
};

inline bool
VideoOutputGeometry::operator==(const VideoOutputGeometry& that) const
{
  return dest_x == that.dest_x
    && dest_y == that.dest_y
    && width == that.width
    && height == that.height
    && pixel_aspect == that.pixel_aspect
    && win_x == that.win_x
    && win_y == that.win_y;
}

////////////////////////////////////////////////////////////////

struct WindowGeometry
{
  int		x0;
  int		y0;
  int		width;
  int		height;
  double	pixel_aspect;

public:
  WindowGeometry() : pixel_aspect(1.0) {}

  bool operator==(const WindowGeometry& that) const;
  bool operator!=(const WindowGeometry& that) const { return ! (*this == that); }
};

inline bool
WindowGeometry::operator==(const WindowGeometry& that) const
{
  return x0 == that.x0 && y0 == that.y0
    && width == that.width && height == that.height
    && pixel_aspect == that.pixel_aspect;
}

END_PXLIB_NAMESPACE
#endif // !Geometry_H
