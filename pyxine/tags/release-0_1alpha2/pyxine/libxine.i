/* -*-C-*-
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
%module libxine
%{
#include <xine.h>

#ifdef LIST_OUTPUT
# define output_helper l_output_helper
#else
# define output_helper t_output_helper
#endif

#define STRINGIFY(s) #s
  
void initlibxine (void);

PyObject * Pyxine_Error = 0;

static void
init_statics (void)
{  
  PyObject * pyxine = PyImport_ImportModule("pyxine");

  if (pyxine) {
    Pyxine_Error = PyObject_GetAttrString(pyxine, "Error");
    Py_DECREF(pyxine);
  }
    
  if (!Pyxine_Error) {
    if (PyErr_Occurred())
      PyErr_Print();
    Pyxine_Error = PyExc_Exception; /* punt */
    Py_INCREF(Pyxine_Error);
  }
}  

%}

%init %{ init_statics(); %}
 
     
%section "libxine", before, pre

/*****************************************************************
 *
 * Typemaps
 *
 ****************************************************************/
%include "typemaps.i"

/*
 * These typedefs are not necessarily correct, but they convince SWIG to
 * treat the types as simple scalars.  (Which is all we really
 * want...)
 */
typedef long int64_t;
typedef unsigned uint32_t;
typedef unsigned short uint16_t;
typedef unsigned char uint8_t;


/** int64_t
 *
 * (SWIG doesn't know about long long's.)
 */
%typemap (python,in) int64_t
{
  PyObject * aslong = PyNumber_Long($source);
  if (!aslong)
    return NULL;
  $target = PyLong_AsLongLong(aslong);
  Py_DECREF(aslong);
  if (PyErr_Occurred())
    return NULL;
}


/**
 * CONSTANT_MEMBER
 *
 * Raise an exception upon attempts to modify struct member.
 */
%typemap (python,memberin) CONSTANT_MEMBER
{
  PyErr_Format(PyExc_AttributeError,
	       "%s is read-only", STRINGIFY($target));
  return 0;
}


/** INT_ARRAY256_t *INPUT
 *
 * Typemap for pointer to an array of ints of length 256.
 */
%typemap (python,arginit) INT_ARRAY256_t *INPUT
{
  if (!($target = alloca(256 * sizeof(*$target))))
    return PyErr_NoMemory();
}
%typemap (python,in) INT_ARRAY256_t *INPUT
{
  int i;
  PyObject * seq = PySequence_Fast($source, "");

  if (!seq || PySequence_Fast_GET_SIZE(seq) != 256) {
    if (seq) {
      Py_DECREF(seq);
    }
    return PyErr_Format(PyExc_ValueError,
			"expected sequence of length 256 for arg %d of %s",
			$argnum, STRINGIFY($name));
  }

  
  for (i = 0; i < 256; i++) {
    long val = PyInt_AsLong(PySequence_Fast_GET_ITEM(seq, i));
    if (val == -1) {
      Py_DECREF(seq);
      return PyErr_Format(PyExc_ValueError,
			  "expected sequence of length 256 for arg %d of %s",
			  $argnum, STRINGIFY($name));
    }
    $target[i] = val;
  }
  Py_DECREF(seq);
}

/** INT_ARRAY256_t *OUTPUT
 *
 * Typemap for pointer to an array of length 256.
 */
%typemap (python,ignore) INT_ARRAY256_t *OUTPUT
{
  if (!($target = alloca(256 * sizeof(*$target))))
    return PyErr_NoMemory();
}
%typemap (python,argout) INT_ARRAY256_t *OUTPUT
{
  int i;
  PyObject * tuple = PyTuple_New(256);
  if (!tuple)
    return NULL;
  for (i = 0; i < 256; i++) {
    PyObject * c = PyInt_FromLong((long)$source[i]);
    if (!c)
      return NULL;
    PyTuple_SET_ITEM(tuple, i, c);
  }
  $target = l_output_helper($target, tuple);
}


typedef char * STRING;
%{
  typedef const char * STRING;
%}

/** STRING
 *
 * Output typemap for (possible NULL) strings.
 *
 * HACK ALERT: This checks for python exceptions which might have
 * been thrown as a result of the CONSTANT_MEMBER memberin typemap.
 */
%typemap (python, out) STRING
{
  if (PyErr_Occurred())
    return NULL;
  $target = Py_BuildValue("s", $source);
  if (!$target)
    return NULL;
}

%typemap (python,memberin) STRING = CONSTANT_MEMBER;
%typemap (python,memberout) STRING = char *;

/** FREEABLE_STRING_t
 *
 * Output typemap for functions which return a freeable char *.
 */
%typemap (python,out) FREEABLE_STRING_t
{
  if ($source) {
    $target = PyString_FromString($source);
    free($source);
    if (!$target)
      return NULL;
  }
  else {
    Py_INCREF(Py_None);
    $target = Py_None;
  }
}

/** STRING *
 *
 * Typemap to convert array of strings to tuple of strings.
 */
%typemap (python,out) STRING *
{
  PyObject * stmp;
  size_t i, len = 0;

  while ($source[len])
    len++;

  if (!($target = PyTuple_New(len)))
    return NULL;

  for (i = 0; i < len; i++) {
    if (!(stmp = PyString_FromString($source[i])))
      return NULL;
    PyTuple_SET_ITEM($target, i, stmp);
  }
}
%typemap (python,memberin) STRING * = CONSTANT_MEMBER;


/** STRINGDUP
 *
 * Input typemap for strings which need to be in their own memory.
 */
%typemap (python,in) STRINGDUP
{
  char * str = PyString_AsString($source);
  if (!str) {
    return PyErr_Format(PyExc_TypeError,
			"expected string for arg %d of %s",
			$argnum, STRINGIFY($name));
  }
  $target = strdup(str);
  if (!$target) {
    return PyErr_NoMemory();
  }
}

  
/** STRINGDUP *
 *
 * Input typemap for array of strings which need to be copied
 * into their own memory.
 */
%typemap (python,in) STRINGDUP *
{
  int i, length;
  PyObject * seq = PySequence_Fast($source, "");

  
  if (!seq) {
    return PyErr_Format(PyExc_TypeError,
			"expected sequence of strings for arg %d of %s",
			$argnum, STRINGIFY($name));
  }

  length = PySequence_Fast_GET_SIZE(seq);
  $target = malloc((length + 1) * sizeof(*$target));
  if (!$target) {
    Py_DECREF(seq);
    return PyErr_NoMemory();
  }
  
  for (i = 0; i < length; i++) {
    char * str = PyString_AsString(PySequence_Fast_GET_ITEM(seq, i));
    if (!str) {
      Py_DECREF(seq);
      return PyErr_Format(PyExc_TypeError,
			  "expected sequence of strings for arg %d of %s",
			  $argnum, STRINGIFY($name));
    }
    $target[i] = strdup(str);
    if (!$target[i]) {
      Py_DECREF(seq);
      return PyErr_NoMemory();
    }
  }
  $target[length] = 0;
  Py_DECREF(seq);
}


/** opt_STRING_t INPUT
 *
 * A optional string input.
 * Expects either a python string or None, converts to char * or NULL.
 */
%typemap (python,in) opt_STRING_t INPUT {
  if ($source == Py_None) {
    $target = 0;
  }
  else {
    if (!($target = PyString_AsString($source)))
      return NULL;
  }
}

/** STRING64_t *OUTPUT
 *
 * An output argument which is a string of length < 64.
 */
%typemap (python,ignore) STRING64_t OUTPUT (char temp[64])
{
  $target = temp;
}
%typemap (python,argout) STRING64_t OUTPUT
{
  $target = output_helper($target, PyString_FromString($source));
}


/** SWIGPTR *INPUT
 *
 * Converts a sequence of SWIG ptrs (strings, e.g. "_2e14f2_xine_t_p")
 * to a NULL terminated array of C pointers.
 */
%typemap (python,in) SWIGPTR *INPUT ($type tmp)
{
  static const char * ptrtype = "_" STRINGIFY($basetype) "_p";
  PyObject * seq = PySequence_Fast($source, "");
  int length, i;
  
  if (! seq) {
    if (!PyErr_ExceptionMatches(PyExc_TypeError))
      return NULL;
    return PyErr_Format(PyExc_TypeError,
			"expected a sequence of %s's for arg %d of %s",
			ptrtype, $argnum, STRINGIFY($name));
  }

  length = PySequence_Fast_GET_SIZE(seq);

  if ( ! (tmp = alloca(sizeof(*tmp) * (length + 1))) ) {
    Py_DECREF(seq);
    return PyErr_NoMemory();
  }

  for (i = 0; i < length; i++) {
    char * str = PyString_AsString(PySequence_Fast_GET_ITEM(seq, i));
    if (!str || SWIG_GetPtr(str, (void **)&tmp[i], (char *)ptrtype)) {
      Py_DECREF(seq);
      return PyErr_Format(PyExc_TypeError,
			  "expected a sequence of %s's for arg %d of %s",
			  ptrtype, $argnum, STRINGIFY($name));
    }
  }
  Py_DECREF(seq);
  tmp[length] = 0;
  $target = tmp;
}

/** SWIGPTR *
 *
 * Convert pointer to NULL-terminated array of SWIGPTRs to
 * python sequence object.
 */
%typemap (python,out) SWIGPTR *
{
  static const char * ptrtype = "_" STRINGIFY($basetype) "_p";
  PyObject * stmp;
  char	ptmp[128];
  size_t i, len = 0;

  while ($source[len])
    len++;
  
  if (!($target = PyTuple_New(len)))
    return NULL;

  for (i = 0; i < len; i++) {
    SWIG_MakePtr(ptmp, (char *) $source[i], (char *) ptrtype);
    if (!(stmp = PyString_FromString(ptmp)))
      return NULL;
    PyTuple_SET_ITEM($target, i, stmp);
  }
}

/** xine_mrl_t **
 *
 * Convert list of xine_mrl_t to tuple of dicts...
 */
%typemap (python, out) xine_mrl_t **
{
  size_t i, len = 0;

  while ($source[len])
    len++;
  
  if (!($target = PyTuple_New(len)))
    return NULL;

  for (i = 0; i < len; i++) {
    xine_mrl_t * item = $source[i];
    PyObject * val = Py_BuildValue("{s:s,s:s,s:s,s:l,s:l}",
				   "origin",	item->origin,
				   "mrl",	item->mrl,
				   "link",	item->link,
				   "type",	(long)item->type,
				   "off_t",	(long)item->size);
    if (!val)
      return NULL;
    PyTuple_SET_ITEM($target, i, val);
  }
}

/** struct timeval *
 *
 * Convert struct timeval's to/from floating point seconds.
 */
%typemap (python,out) struct timeval *
{
  $target = PyFloat_FromDouble($source->tv_sec + $source->tv_usec / 1e6);
}
%typemap (python,in) struct timeval * (struct timeval tmp)
{
  double secs;
  secs = PyFloat_AsDouble($source);
  tmp.tv_sec = floor(secs);
  tmp.tv_usec = floor((secs - tmp.tv_sec) * 1e6);
  $target = &tmp;
}


/** PyBuffer *OUTPUT
 *
 * Return structs as as PyBuffer objects, rather than SWIG pointers.
 * We do this with xine_cfg_entry_t's and xine_event_t's because
 * it makes the memory management automatic.
 *
 * FIXME: this typemap wont work if applied to more than one
 * argument of a function.
 */
%typemap (python,ignore) PyBuffer *OUTPUT (PyObject * buffer)
{
  void * ptr;
  int length;
  buffer = PyBuffer_New(sizeof($basetype));
  if (!buffer)
    return NULL;
  PyObject_AsWriteBuffer(buffer, &ptr, &length);
  $target = ptr;
}
%typemap (python,argout) PyBuffer *OUTPUT
{
  $target = output_helper($target, buffer);
}

/** PyBuffer *INPUT
 *
 * Convert PyBuffer to pointers to data on input.
 */
%typemap (python,in) PyBuffer *INPUT
{
  int length;
  void * ptr;
  
  if (PyObject_AsWriteBuffer($source, (void **)&ptr, &length))
    return NULL;
#unassert BASETYPE
#assert BASETYPE($basetype)
#if #BASETYPE(xine_event_t)
  if (length != sizeof($basetype) && length != sizeof(xine_input_data_t)) 
#else
  if (length != sizeof($basetype)) 
#endif
#unassert BASETYPE    
    return PyErr_Format(PyExc_TypeError,
			"arg %d of %s has bad size for %s",
			$argnum, STRINGIFY($name), STRINGIFY($basetype));
  $target = ptr;
}

/** PyBuffer *
 *
 * Wrap returned pointers in PyBuffer for compatibility.
 * HACK ALERT: These PyBuffers do not free their associated
 * memory upon destruction, so you need to arrange for that
 * some other way.
 */
%typemap (python,out) PyBuffer *
{
  if ($source) {
    $target = PyBuffer_FromReadWriteMemory($source, sizeof($basetype));
    if (!$target)
      return NULL;
  }
  else {
    Py_INCREF(Py_None);
    $target = Py_None;
  }
}




#ifndef SWIG
/** xine_cfg_entry_t *OUTPUT
 *
 * Return these as PyBuffer objects.  (We do this, rather than
 * returning SWIG pointers, because it handles freeing of the
 * structures memory automatically.)
 *
 * FIXME: this typemap wont work if applied to more than one
 * argument of a function.
 */
%typemap (python,ignore) xine_cfg_entry_t *OUTPUT (PyObject * buffer)
{
  void * ptr;
  int length;
  buffer = PyBuffer_New(sizeof(xine_cfg_entry_t));
  if (!buffer)
    return NULL;
  PyObject_AsWriteBuffer(buffer, &ptr, &length);
  $target = (xine_cfg_entry_t *)ptr;
}
%typemap (python,argout) xine_cfg_entry_t *OUTPUT
{
  $target = output_helper($target, buffer);
}

%typemap (python,in) xine_cfg_entry_t * 
{
  int length;
  void * ptr;
  
  if (PyObject_AsWriteBuffer($source, (void **)&ptr, &length))
    return NULL;
  if (length != sizeof(xine_cfg_entry_t)) 
    return PyErr_Format(PyExc_TypeError,
			"arg %d of %s has bad size for xine_cfg_entry_t",
			$argnum, STRINGIFY($name));
  $target = ptr;
}
%typemap (python,in) struct xine_cfg_entry_s * = xine_cfg_entry_t *;
#endif

/** NONNULL_SWIGPTR
 *
 * Raise failure exception for those "constructor-like" functions which
 * should return non-NULL SWIG pointers but don't.
 */ 
%typemap (python,out) NONNULL_SWIGPTR
{
  char ptmp[128];
  if ($source == NULL)
    return PyErr_Format(Pyxine_Error, "%s failed", STRINGIFY($name));
  SWIG_MakePtr(ptmp, (char *)$source, STRINGIFY($mangle));
  $target = PyString_FromString(ptmp);
  if (!$target)
    return NULL;
}

/** bool OKAY
 *
 * Raise failure exception for those function which
 * return zero upon failure.
 */ 
%typemap (python,out) bool OKAY
{
  if (! $source)
    return PyErr_Format(Pyxine_Error, "%s failed", STRINGIFY($name));
  Py_INCREF(Py_None);
  $target = Py_None;
}

/** bool ITER_OKAY
 *
 * Raise StopIteration for those functions which
 * return zero upon failure.
 */ 
%typemap (python,out) bool ITER_OKAY
{
  if (! $source) {
    PyErr_SetNone(PyExc_StopIteration);
    return NULL;
  }
  Py_INCREF(Py_None);
  $target = Py_None;
}

/** bool LOOKUP_OKAY
 *
 * Raise KeyError for those functions which
 * return zero upon failure.
 */ 
%typemap (python,out) bool LOOKUP_OKAY
{
  if (! $source) {
    PyErr_SetNone(PyExc_KeyError);
    return NULL;
  }
  Py_INCREF(Py_None);
  $target = Py_None;
}

/*****************************************************************
 * Python callback handling
 ****************************************************************/
%{
struct callback_s 
{
  PyThreadState * state;
  PyObject * callback;
};
typedef struct callback_s callback_t;

static callback_t *
callback_t_new(PyObject * callback)
{
  callback_t * cb;

  if (!PyCallable_Check(callback)) {
    PyErr_SetString(PyExc_TypeError, "Need a callable object for callback");
    return 0;
  }

  if (!(cb = malloc(sizeof(callback_t)))) {
    PyErr_NoMemory();
    return 0;
  }

  /* You must call this from a python thread. */
  PyEval_InitThreads();
  cb->state = PyThreadState_New(PyThreadState_Get()->interp);
  if (!cb->state) {
    free(cb);
    return 0;
  }
  PyThreadState_Clear(cb->state);

  cb->callback = callback;
  Py_INCREF(callback);

  return cb;
}

static void
callback_t_delete(callback_t * cb)
{
  PyThreadState_Delete(cb->state);
  Py_DECREF(cb->callback);
  free(cb);
}

#define BEGIN_CALLBACK_CONTEXT(cb)					\
    {									\
      PyThreadState * saved_state;					\
      PyEval_AcquireLock();						\
      saved_state = PyThreadState_Swap(cb->state);
#define END_CALLBACK_CONTEXT(cb)					\
      /* Report any pending exception */				\
      if (PyErr_Occurred())						\
        PyErr_Print();							\
      PyThreadState_Swap(saved_state);					\
      PyEval_ReleaseLock();						\
    }
%}

/** CALLBACK_t *INPUT
 *
 * Convert python callable object to callback_t * (for use a C callback
 * user_data).
 */
%typemap (python,arginit) CALLBACK_t *INPUT
{
  $target = 0;
}
%typemap (python,in) CALLBACK_t *INPUT
{
  /* FIXME: memory leak: callback_t is never freed */
  $target = callback_t_new($source);
  if (!$target)
    return NULL;
}

/** opt_CALLBACK_t *INPUT
 *
 * Convert optional python callable object to callback_t * (for use a
 * C callback user_data).
 */
%typemap (python,arginit) opt_CALLBACK_t *INPUT = CALLBACK_t *INPUT;
%typemap (python,in) opt_CALLBACK_t *INPUT
{
  if ($source != Py_None) {
    /* FIXME: memory leak: callback_t is never freed */
    $target = callback_t_new($source);
    if (!$target)
      return NULL;
  }
}


/*
 * The C callback functions for various types of callbacks.
 */
%{
void
event_listener_callback (void *user_data, const xine_event_t *event)
{
  callback_t * cb = (callback_t *)user_data;
  PyObject * buffer;
  
  if (!cb)
    return;

  BEGIN_CALLBACK_CONTEXT(cb);

  buffer = PyBuffer_New(sizeof(xine_event_t));
  if (buffer) {
    void * ptr;
    int length;
    PyObject_AsWriteBuffer(buffer, &ptr, &length);
    *(xine_event_t *)ptr = *event;
    PyObject_CallFunction(cb->callback, "O", buffer);
    Py_DECREF(buffer);
  }
  
  END_CALLBACK_CONTEXT(cb);
}
%}
%typemap (python,ignore) xine_event_listener_cb_t
{
  $target = event_listener_callback;
}

%{
void
xine_cfg_entry_callback (void *user_data, xine_cfg_entry_t *entry)
{
  callback_t * cb = (callback_t *)user_data;
  PyObject * buffer;
  
  if (!cb)
    return;
  
  BEGIN_CALLBACK_CONTEXT(cb);

  buffer = PyBuffer_New(sizeof(xine_cfg_entry_t));
  if (buffer) {
    void * ptr;
    int length;
    PyObject_AsWriteBuffer(buffer, &ptr, &length);
    *(xine_cfg_entry_t *)ptr = *entry;
    PyObject_CallFunction(cb->callback, "O", buffer);
    Py_DECREF(buffer);
  }

  END_CALLBACK_CONTEXT(cb);
}
%}    
%typemap (python,ignore) xine_config_cb_t
{
  $target = xine_cfg_entry_callback;
}

%{
void
xine_log_callback (void *user_data, int section)
{
  callback_t * cb = (callback_t *)user_data;
  
  if (!cb)
    return;
  
  BEGIN_CALLBACK_CONTEXT(cb);

  PyObject_CallFunction(cb->callback, "i", section);

  END_CALLBACK_CONTEXT(cb);
}
%}
%typemap (python,ignore) xine_log_cb_t
{
  $target = xine_log_callback;
}

/*****************************************************************
 *
 ****************************************************************/

/** BLOCKING
 *
 * Drop python global lock for functions which may take a long
 * time to complete.
 *
 * Also for functions which may call python-side callbacks.
 * (The callbacks need to acquire the python lock themselves.)
 */
%typemap (python,except) BLOCKING
{
  Py_BEGIN_ALLOW_THREADS
  $function  
  Py_END_ALLOW_THREADS
}

/* These may call callbacks */
%apply BLOCKING {
  xine_video_port_t *xine_open_video_driver,
    void xine_log,
    void xine_config_update_entry,
    int xine_open,
    int xine_play,
    void xine_stop,
    void xine_close
    };

/* These may block */
%apply BLOCKING { xine_event_t *xine_event_wait };



/*****************************************************************
 * Input argument fixups.
 */

/* For xine_open_audio_driver(), xine_open_video_driver() */
%apply opt_STRING_t INPUT { char *id };

/* xine_register_log_cb(), xine_event_create_listener_thread() */
%apply CALLBACK_t *INPUT { void *user_data };

/* xine_config_register_*() */
%apply opt_CALLBACK_t *INPUT { void *cb_data };
%apply STRINGDUP { char *def_value, char *description, char *help }
%apply STRINGDUP * { char **values }
   
/* xine_post_init() */
%apply SWIGPTR *INPUT { xine_audio_port_t **audio_target,
			  xine_video_port_t **video_target };

/* xine_osd_set_palette() */
%{
  typedef uint32_t color_t;
  typedef uint8_t  trans_t;
%}
%apply INT_ARRAY256_t *INPUT { trans_t *, color_t * }

/* xine_log */
%typemap (python,ignore) char *xine_log_format { $target = "%s\n"; }

/* xine_config_update_entry() */
%apply PyBuffer *INPUT  { xine_cfg_entry_t * }

/* xine_cfg_t_*() accessors */
%apply PyBuffer *INPUT  { struct xine_cfg_entry_s * }

/* xine_event_free(), xine_event_send(), xine_event_t_*() accessors */
%apply PyBuffer *INPUT  { xine_event_t * }


/*****************************************************************
 * Output argument fixups.
 */

/* For xine_get_pos_length() */
%apply int *OUTPUT { int *pos_stream, int *pos_time, int *length_time };

/* For xine_get_spu_lang(), xine_get_audio_lang() */
%apply STRING64_t OUTPUT { char *lang };

/* xine_osd_get_text_size() */
%apply int *OUTPUT { int *width, int *height };

/* xine_osd_get_palette() */
%apply INT_ARRAY256_t *OUTPUT { trans_t *OUTPUT, color_t *OUTPUT };

/* xine_get_version() */
%apply int *OUTPUT { int *major, int *minor, int *sub };

/* xine_config_get_{first,next}_entry(), xine_config_lookup_entry() */
%apply PyBuffer *OUTPUT { xine_cfg_entry_t *OUTPUT }

/*****************************************************************
 * Return value fixups
 */

%apply FREEABLE_STRING_t { char *xine_get_file_extensions,
			     char *xine_get_mime_types,
			     char *xine_get_demux_for_mime_type};

/* xine_post_s::audio_input, xine_post_s::video_input */
%apply SWIGPTR * { xine_audio_port_t **, xine_video_port_t ** };
%typemap (python, memberin) xine_audio_port_t ** = CONSTANT_MEMBER;
%typemap (python, memberin) xine_video_port_t ** = CONSTANT_MEMBER;

/* xine_cfg_entry_s::enum_values */
%apply STRING * { char **xine_cfg_entry_s_enum_values_get }

/* xine_event_get(), xine_event_wait() */
%apply PyBuffer * { xine_event_t *xine_event_get, xine_event_t *xine_event_wait }

/*****************************************************************
 * Return value checks
 */

/* "constructor-like" functions which return NULL upon failure */
%apply NONNULL_SWIGPTR {
  xine_t *xine_new,
    xine_audio_port_t *xine_open_audio_driver,
    xine_video_port_t *xine_open_video_driver,
    xine_stream_t *xine_stream_new,
    xine_post_t *xine_post_init,
    xine_post_in_t *xine_post_input,
    xine_post_out_t *xine_post_output,
    xine_post_out_t *xine_get_video_source,
    xine_post_out_t *xine_get_audio_source,
    xine_health_check_t *xine_health_check,
    xine_event_queue_t *xine_event_new_queue,
    xine_osd_t *xine_osd_new };

/* Functions which return a boolean (zero for failure),
 *  exit code, with more information available from xine_get_error.
 *
 * For now, error checking is done on the python side of things...
 */
%apply int {
  int xine_open,
    int xine_play,
    int xine_trick_mode};

/* Functions which return a boolean (zero for failure) exit code */
%apply bool OKAY {
  int xine_eject,
    int xine_get_audio_lang,
    int xine_get_spu_lang,
    int xine_get_pos_length,
    int xine_get_current_frame,
    int xine_get_video_frame,
    int xine_post_wire,
    int xine_post_wire_video_port,
    int xine_post_wire_audio_port };

%apply bool ITER_OKAY {
  int xine_config_get_first_entry,
    int xine_config_get_next_entry };

%apply bool LOOKUP_OKAY { int xine_config_lookup_entry }

/*****************************************************************
 * Constant fixups.
 *
 * SWIG doesn't seem to recognize these as constants.
 */
%{
  static const int _XINE_IMGFMT_YV12 = XINE_IMGFMT_YV12;
  static const int _XINE_IMGFMT_YUY2 = XINE_IMGFMT_YUY2;
%}
#define XINE_IMGFMT_YV12 (int) _XINE_IMGFMT_YV12
#define XINE_IMGFMT_YUY2 (int) _XINE_IMGFMT_YUY2

/*****************************************************************/

/*****************************************************************
 * Utility functions
 */
%apply PyBuffer *OUTPUT { xine_input_data_t *OUTPUT }

%inline %{
void
px_make_input_event(int type, uint8_t button, uint16_t x, uint16_t y,
		    xine_input_data_t *OUTPUT)
{
  xine_input_data_t * buf = OUTPUT;
  
  memset(buf, 0, sizeof(*buf));
  buf->event.type = type;
  buf->event.data = buf;
  buf->event.data_length = sizeof(*buf);
  buf->button = button;
  buf->x = x;
  buf->y = y;
}
%} 

  
/*****************************************************************/

%include "fixed_xine.h"

