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

#ifndef _Mutex_H
#define _Mutex_H

#include "pxlib.h"

extern "C" {
# include <pthread.h>
}

BEGIN_PXLIB_NAMESPACE

class Mutex
{
private:
  pthread_mutex_t m;

public:
  Mutex() { pthread_mutex_init(&m, NULL); }
  ~Mutex() { pthread_mutex_destroy(&m); }
  operator pthread_mutex_t * () { return &m; }
};

class MutexLock
{
  struct lock_t {
    pthread_mutex_t * mp;
    int ref_cnt;

    lock_t(pthread_mutex_t * _mp)
      : mp(_mp), ref_cnt(1)
    { pthread_mutex_lock(mp); }

    ~lock_t() { pthread_mutex_unlock(mp); }
  };

  lock_t * lock;

public:
  MutexLock() : lock(0) {}
  MutexLock(pthread_mutex_t * m) : lock(new lock_t(m)) {}
  MutexLock(Mutex * m) : lock(new lock_t(*m)) {}
  MutexLock(const MutexLock& l) : lock(l.lock) {
    if (lock)
      lock->ref_cnt++;
  }
  MutexLock& operator= (const MutexLock& l) {
    if (lock && --lock->ref_cnt == 0)
      delete lock;
    lock = l.lock;
    if (lock)
      lock->ref_cnt++;
    return *this;
  }
  ~MutexLock () {
    if (lock && --lock->ref_cnt == 0)
      delete lock;
  }
};

/** A atomic data item.
 *
 * The data contained within is protected by a mutex, so that
 * access to the data is guaranteed to be atomic.
 */
template <class T>
class atomic
{
public:
  typedef T data_type;

private:
  data_type	value;
  mutable Mutex	mutex;

public:
  atomic() {}
  atomic(const data_type& x) : value(x) {}
  atomic(const atomic& a) : value(a) {}

  /** Assigment.
   *
   * Data only comes in with the mutex held.
   */
  atomic& operator= (const data_type& new_value) {
    MutexLock l(mutex);
    value = new_value;
    return *this;
  }

  /** Update value.
   *
   * Update the value.
   *
   * @return True iff the update changed the value.
   */
  bool update (const data_type& new_value) {
    MutexLock l(mutex);
    bool changed = value != new_value;
    if (changed)
      value = new_value;
    return changed;
  }

  /**
   * Conversion to data_type.
   *
   * This is the only way to access the data.
   */
  operator data_type () const {
    MutexLock l(mutex);
    return value;
  }
};

END_PXLIB_NAMESPACE

#endif // !_Mutex_H
