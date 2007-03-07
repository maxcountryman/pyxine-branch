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
#ifndef _pxlib_H
#define _pxlib_H

#include <iostream>
#include <iomanip>
#include <string>

#define BEGIN_PXLIB_NAMESPACE	namespace pyxine {
#define END_PXLIB_NAMESPACE	}  

BEGIN_PXLIB_NAMESPACE

class Error
{
  std::string msg;
public:
  Error (const std::string& m) : msg(m) {}
  const char * get_message () const { return msg.c_str(); }
  operator const char * () const { return msg.c_str(); }
};

using std::cerr;
using std::endl;

END_PXLIB_NAMESPACE

#endif // !_pxlib_H
