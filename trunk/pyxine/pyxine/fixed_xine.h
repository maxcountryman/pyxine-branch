/*
 * $Id$
 *
 * Copyright (C) 2003 Geoffrey T. Dairiki
 *
 * This file is part of Pyxine, Python bindings for xine.
 *
 * This is a *modification* of xine.h which is part of xine,
 * a free video player.  Xine is available from http://xinehq.de/
 *
 * This version of xine.h is modified so as to make it an
 * acceptable input to SWIG.
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
/*
 * The original copyright follows:
 *
 *
 * Copyright (C) 2000-2002 the xine project
 *
 * This file is part of xine, a free video player.
 *
 * xine is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * xine is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
 *
 * Id: xine.h.in,v 1.58 2003/01/29 02:33:35 miguelfreitas Exp
 *
 * public xine-lib (libxine) interface and documentation
 *
 *
 * some programming guidelines about this api:
 * -------------------------------------------
 *
 * (1) libxine has (per stream instance) a fairly static memory
 *     model
 * (2) as a rule of thumb, never free() or realloc() any pointers
 *     returned by the xine engine (unless stated otherwise)
 *     or, in other words:
 *     do not free() stuff you have not malloc()ed
 * (3) xine is multi-threaded, make sure your programming environment
 *     can handle this.
 *     for x11-related stuff this means that you either have to properly
 *     use xlockdisplay() or use two seperate connections to the x-server
 *
 */

#ifndef HAVE_XINE_H
#define HAVE_XINE_H

#ifdef __cplusplus
extern "C" {
#endif

#include <sys/types.h>
#include <unistd.h>
#include <inttypes.h>
#include <sys/time.h>
#include <time.h>


/*********************************************************************
 * xine opaque data types                                            *
 *********************************************************************/

typedef struct xine_s xine_t;
typedef struct xine_stream_s xine_stream_t;
typedef struct xine_audio_port_s xine_audio_port_t;
typedef struct xine_video_port_s xine_video_port_t;

/* convenience types: simple player UIs might want to call ports drivers */
typedef xine_audio_port_t xine_ao_driver_t;
typedef xine_video_port_t xine_vo_driver_t;


/*********************************************************************
 * global engine handling                                            *
 *********************************************************************/

/*
 * version information
 */

/* dynamic info from actually linked libxine */
const char *xine_get_version_string (void);
void xine_get_version (int *major, int *minor, int *sub);

/* compare given version to libxine version,
   return 1 if compatible, 0 otherwise */
int  xine_check_version (int major, int minor, int sub) ;

/* static info - which libxine release this header came from */
#define XINE_MAJOR_VERSION 1
#define XINE_MINOR_VERSION 0
#define XINE_SUB_VERSION   0
#define XINE_VERSION       "1-beta4"

/*
 * pre-init the xine engine
 *
 * will first malloc and init a xine_t, create an empty config
 * system, then scan through all installed plugins and add them
 * to an internal list for later use.
 *
 * to fully init the xine engine, you have to load config values
 * (either using your own storage method and calling
 * xine_config_register_entry, or by using the xine_load_config
 * utility function - see below) and then call xine_init
 *
 * the only proper way to shut down the xine engine is to
 * call xine_exit() - do not try to free() the xine pointer
 * yourself and do not try to access any internal data structures
 */
xine_t *xine_new (void);

/*
 * post_init the xine engine
 */
void xine_init (xine_t *self);

/*
 * helper functions to find and init audio/video drivers
 * from xine's plugin collection
 *
 * id    : identifier of the driver, may be NULL for auto-detection
 * data  : special data struct for ui/driver communications, depends
 *         on driver
 * visual: video driver flavor selector, constants see below
 *
 * both functions may return NULL if driver failed to load, was not
 * found ...
 *
 * use xine_close_audio/video_driver() to close loaded drivers
 * and free resources allocated by them
 */
xine_audio_port_t *xine_open_audio_driver (xine_t *self, const char *id,
					   void *data);
xine_video_port_t *xine_open_video_driver (xine_t *self, const char *id,
					   int visual, void *data);

void xine_close_audio_driver (xine_t *self, xine_audio_port_t  *driver);
void xine_close_video_driver (xine_t *self, xine_video_port_t  *driver);

/* valid visual types */
#define XINE_VISUAL_TYPE_NONE              0
#define XINE_VISUAL_TYPE_X11               1
#define XINE_VISUAL_TYPE_AA                2
#define XINE_VISUAL_TYPE_FB                3
#define XINE_VISUAL_TYPE_GTK               4
#define XINE_VISUAL_TYPE_DFB               5
#define XINE_VISUAL_TYPE_PM                6 /* used by the OS/2 port */

/*
 * free all resources, close all plugins, close engine.
 * self pointer is no longer valid after this call.
 */
void xine_exit (xine_t *self);


/*********************************************************************
 * stream handling                                                   *
 *********************************************************************/

/*
 * create a new stream for media playback/access
 *
 * returns xine_stream_t* if OK,
 *         NULL on error (use xine_get_error for details)
 *
 * the only proper way to free the stream pointer returned by this
 * function is to call xine_dispose() on it. do not try to access any
 * fields in xine_stream_t, they're all private and subject to change
 * without further notice.
 */
xine_stream_t *xine_stream_new (xine_t *self,
				xine_audio_port_t *ao, xine_video_port_t *vo);

/*
 * Make one stream the slave of another.
 * This establishes a binary master slave relation on streams, where
 * certain operations (specified by parameter "affection") on the master
 * stream are also applied to the slave stream.
 * If you want more than one stream to react to one master, you have to
 * apply the calls in a top down way:
 *  xine_stream_master_slave(stream1, stream2, 3);
 *  xine_stream_master_slave(stream2, stream3, 3);
 * This will make stream1 affect stream2 and stream2 affect stream3, so
 * effectively, operations on stream1 propagate to stream2 and 3.
 *
 * Please note that subsequent master_slave calls on the same streams
 * will overwrite their previous master/slave setting.
 * Be sure to not mess around.
 *
 * returns 1 on success, 0 on failure
 */
int xine_stream_master_slave(xine_stream_t *master, xine_stream_t *slave,
                             int affection);

/* affection is some of the following ORed together: */
/* playing the master plays the slave */
#define XINE_MASTER_SLAVE_PLAY     (1<<0)
/* slave stops on master stop */
#define XINE_MASTER_SLAVE_STOP     (1<<1)

/*
 * open a stream
 *
 * look for input / demux / decoder plugins, find out about the format
 * see if it is supported, set up internal buffers and threads
 *
 * returns 1 if OK, 0 on error (use xine_get_error for details)
 */
int xine_open (xine_stream_t *stream, const char *mrl);

/*
 * play a stream from a given position
 *
 * start_pos:  0..65535
 * start_time: milliseconds
 * if both start position parameters are != 0 start_pos will be used
 * for non-seekable streams both values will be ignored
 *
 * returns 1 if OK, 0 on error (use xine_get_error for details)
 */
int  xine_play (xine_stream_t *stream, int start_pos, int start_time);

/*
 * set xine to a trick mode for fast forward, backwards playback,
 * low latency seeking. Please note that this works only with some
 * input plugins. mode constants see below.
 *
 * returns 1 if OK, 0 on error (use xine_get_error for details)
 */
int  xine_trick_mode (xine_stream_t *stream, int mode, int value);

/* trick modes */
#define XINE_TRICK_MODE_OFF                0
#define XINE_TRICK_MODE_SEEK_TO_POSITION   1
#define XINE_TRICK_MODE_SEEK_TO_TIME       2
#define XINE_TRICK_MODE_FAST_FORWARD       3
#define XINE_TRICK_MODE_FAST_REWIND        4

/*
 * stop stream playback
 * xine_stream_t stays valid for new xine_open or xine_play
 */
void xine_stop (xine_stream_t *stream);

/*
 * stop stream playback, free all stream-related resources
 * xine_stream_t stays valid for new xine_open
 */
void xine_close (xine_stream_t *stream);

/*
 * ask current/recent input plugin to eject media - may or may not work,
 * depending on input plugin capabilities
 */
int  xine_eject (xine_stream_t *stream);

/*
 * stop playback, dispose all stream-related resources
 * xine_stream_t no longer valid when after this
 */
void xine_dispose (xine_stream_t *stream);

/*
 * set/get xine engine parameters
 * e.g. playback speed, constants see below
 */
void xine_set_param (xine_stream_t *stream, int param, int value);
int  xine_get_param (xine_stream_t *stream, int param);

/*
 * xine engine parameters
 */
#define XINE_PARAM_SPEED                   1 /* see below                   */
#define XINE_PARAM_AV_OFFSET               2 /* unit: 1/90000 sec           */
#define XINE_PARAM_AUDIO_CHANNEL_LOGICAL   3 /* -1 => auto, -2 => off       */
#define XINE_PARAM_SPU_CHANNEL             4
#define XINE_PARAM_VIDEO_CHANNEL           5
#define XINE_PARAM_AUDIO_VOLUME            6 /* 0..100                      */
#define XINE_PARAM_AUDIO_MUTE              7 /* 1=>mute, 0=>unmute          */
#define XINE_PARAM_AUDIO_COMPR_LEVEL       8 /* <100=>off, % compress otherw*/
#define XINE_PARAM_AUDIO_AMP_LEVEL         9 /* 0..200, 100=>100% (default) */
#define XINE_PARAM_AUDIO_REPORT_LEVEL     10 /* 1=>send events, 0=> don't   */
#define XINE_PARAM_VERBOSITY              11 /* control console output      */
#define XINE_PARAM_SPU_OFFSET             12 /* unit: 1/90000 sec           */

/* speed values */
#define XINE_SPEED_PAUSE                   0
#define XINE_SPEED_SLOW_4                  1
#define XINE_SPEED_SLOW_2                  2
#define XINE_SPEED_NORMAL                  4
#define XINE_SPEED_FAST_2                  8
#define XINE_SPEED_FAST_4                  16

/* video parameters */
#define XINE_PARAM_VO_DEINTERLACE          0x01000000 /* bool               */
#define XINE_PARAM_VO_ASPECT_RATIO         0x01000001 /* see below          */
#define XINE_PARAM_VO_HUE                  0x01000002 /* 0..65535           */
#define XINE_PARAM_VO_SATURATION           0x01000003 /* 0..65535           */
#define XINE_PARAM_VO_CONTRAST             0x01000004 /* 0..65535           */
#define XINE_PARAM_VO_BRIGHTNESS           0x01000005 /* 0..65535           */
#define XINE_PARAM_VO_ZOOM_X               0x01000008 /* percent            */
#define XINE_PARAM_VO_ZOOM_Y               0x0100000d /* percent            */
#define XINE_PARAM_VO_PAN_SCAN             0x01000009 /* bool               */
#define XINE_PARAM_VO_TVMODE               0x0100000a /* ???                */

#define XINE_VO_ZOOM_STEP                  100
#define XINE_VO_ZOOM_MAX                   400
#define XINE_VO_ZOOM_MIN                   -85

/* possible ratios for XINE_PARAM_VO_ASPECT_RATIO */
#define XINE_VO_ASPECT_AUTO                0
#define XINE_VO_ASPECT_SQUARE              1 /* 1:1  */
#define XINE_VO_ASPECT_4_3                 2 /* 4:3  */
#define XINE_VO_ASPECT_ANAMORPHIC          3 /* 16:9 */
#define XINE_VO_ASPECT_DVB                 4 /* 1:2  */
#define XINE_VO_ASPECT_NUM_RATIOS          5
#define XINE_VO_ASPECT_PAN_SCAN            41
#define XINE_VO_ASPECT_DONT_TOUCH          42

/* stream format detection strategies */

/* recognize stream type first by content then by extension. */
#define XINE_DEMUX_DEFAULT_STRATEGY        0
/* recognize stream type first by extension then by content. */
#define XINE_DEMUX_REVERT_STRATEGY         1
/* recognize stream type by content only.                    */
#define XINE_DEMUX_CONTENT_STRATEGY        2
/* recognize stream type by extension only.                  */
#define XINE_DEMUX_EXTENSION_STRATEGY      3

#ifndef SWIG
/*
 * snapshot function
 *
 * image format can be YUV 4:2:0 or 4:2:2
 * will copy the image data into memory that <img> points to
 * (interleaved for yuv 4:2:2 or planary for 4:2:0)
 *
 * returns 1 on success, 0 failure.
 */
int  xine_get_current_frame (xine_stream_t *stream,
			     int *width, int *height,
			     int *ratio_code, int *format,
			     uint8_t *img);

/* xine image formats */
#define XINE_IMGFMT_YV12 (int) (('2'<<24)|('1'<<16)|('V'<<8)|'Y')
#define XINE_IMGFMT_YUY2 (int) (('2'<<24)|('Y'<<16)|('U'<<8)|'Y')
  
/*********************************************************************
 * media processing                                                  *
 *********************************************************************/

#ifdef XINE_ENABLE_EXPERIMENTAL_FEATURES

/*
 * access to decoded audio and video frames from a stream
 * these functions are intended to provide the basis for
 * re-encoding and other video processing applications
 *
 * warning: highly experimental
 *
 */

xine_video_port_t *xine_new_framegrab_video_port (xine_t *self);

typedef struct {

  int64_t  vpts;       /* timestamp 1/90000 sec for a/v sync */
  int64_t  duration;
  int      width, height;
  int      colorspace; /* XINE_IMGFMT_* */
  double   aspect_ratio;

  int      pos_stream; /* bytes from stream start */
  int      pos_time;   /* milliseconds */

  uint8_t *data;
  void    *xine_frame; /* used internally by xine engine */
} xine_video_frame_t;

int xine_get_next_video_frame (xine_video_port_t *port,
			       xine_video_frame_t *frame);

void xine_free_video_frame (xine_video_port_t *port, xine_video_frame_t *frame);

xine_audio_port_t *xine_new_framegrab_audio_port (xine_t *self);

typedef struct {

  int64_t  vpts;       /* timestamp 1/90000 sec for a/v sync */
  int      num_samples;
  int      sample_rate;
  int      num_channels;
  int      bits_per_sample; /* per channel */

  off_t    pos_stream; /* bytes from stream start */
  int      pos_time;   /* milliseconds */

  uint8_t *data;
  void    *xine_frame; /* used internally by xine engine */
} xine_audio_frame_t;

int xine_get_next_audio_frame (xine_audio_port_t *port,
			       xine_audio_frame_t *frame);

void xine_free_audio_frame (xine_audio_port_t *port, xine_audio_frame_t *frame);

  /*
   * maybe future aproach:
   */

int xine_get_video_frame (xine_stream_t *stream,
			  int timestamp, /* msec */
			  int *width, int *height,
			  int *ratio_code, 
			  int *duration, /* msec */
			  int *format,
			  uint8_t *img);

/* TODO: xine_get_audio_frame */

#endif
#endif /* !SWIG */

  
/*********************************************************************
 * post plugin handling                                              *
 *********************************************************************/

/*
 * post effect plugin functions
 *
 * after the data leaves the decoder it can pass an arbitrary tree
 * of post plugins allowing for effects to be applied to the video
 * frames/audio buffers before they reach the output stage
 */

typedef struct xine_post_s xine_post_t;

struct xine_post_s {

  /* a NULL-terminated array of audio input ports this post plugin
   * provides; you can hand these to other post plugin's outputs or
   * pass them to the initialization of streams
   */
  xine_audio_port_t **audio_input;
  
  /* a NULL-terminated array of video input ports this post plugin
   * provides; you can hand these to other post plugin's outputs or
   * pass them to the initialization of streams
   */
  xine_video_port_t **video_input;
  
  /* the type of the post plugin
   * one of XINE_POST_TYPE_* can be used here
   */
  int type;
  
};

/*
 * initialize a post plugin
 *
 * returns xine_post_t* on success, NULL on failure
 *
 * Initializes the post plugin with the given name and connects its
 * outputs to the NULL-terminated arrays of audio and video ports.
 * Some plugins also care about the number of inputs you request
 * (e.g. mixer plugins), others simply ignore this number.
 */
xine_post_t *xine_post_init(xine_t *xine, const char *name,
			    int inputs,
			    xine_audio_port_t **audio_target,
			    xine_video_port_t **video_target);

/* get a list of all available post plugins */
STRING *xine_list_post_plugins(xine_t *xine);

/* get a list of all post plugins of one type */
STRING *xine_list_post_plugins_typed(xine_t *xine, int type);

/*
 * post plugin input/output
 *
 * These structures encapsulate inputs/outputs for post plugins
 * to transfer arbitrary data. Frontends can also provide inputs
 * and outputs and connect them to post plugins to exchange data
 * with them.
 */

typedef struct xine_post_in_s  xine_post_in_t;
typedef struct xine_post_out_s xine_post_out_t;

struct xine_post_in_s {

  /* the name identifying this input */
  STRING        name;
  
  /* the datatype of this input, use one of XINE_POST_DATA_* here */
  int           type;
#ifndef SWIG  
  /* the data pointer; input is directed to this memory location,
   * so you simply access the pointer to access the input data */
  void         *data;
#endif  
};

struct xine_post_out_s {

  /* the name identifying this output */
  STRING        name;
  
  /* the datatype of this output, use one of XINE_POST_DATA_* here */
  int           type;

#ifndef SWIG  
  /* the data pointer; output should be directed to this memory location,
   * so in the easy case you simply write through the pointer */
  void         *data;
  
  /* this function is called, when the output should be redirected
   * to another input, you sould set the data pointer to direct
   * any output to this new input;
   * a special situation is, when this function is called with a NULL
   * argument: in this case you should disconnect the data pointer
   * from any output and if necessary to avoid writing to some stray
   * memory you should make it point to some dummy location,
   * returns 1 on success, 0 on failure;
   * if you do not implement rewiring, set this to NULL */
  int (*rewire) (xine_post_out_t *self, void *data);
#endif  
};

/* get a list of all inputs of a post plugin */
STRING *xine_post_list_inputs(xine_post_t *self);

/* get a list of all outputs of a post plugin */
STRING *xine_post_list_outputs(xine_post_t *self);

/* retrieve one specific input of a post plugin */
const xine_post_in_t *xine_post_input(xine_post_t *self, char *name);

/* retrieve one specific output of a post plugin */
const xine_post_out_t *xine_post_output(xine_post_t *self, char *name);

/*
 * wire an input to an output
 * returns 1 on success, 0 on failure
 */
int xine_post_wire(xine_post_out_t *source, xine_post_in_t *target);

/*
 * wire a video port to a video output
 * This can be used to rewire different post plugins to the video output
 * plugin layer. The ports you hand in at xine_post_init() will already
 * be wired with the post plugin, so you need this function for
 * _re_connecting only.
 *
 * returns 1 on success, 0 on failure
 */
int xine_post_wire_video_port(xine_post_out_t *source, xine_video_port_t *vo);

/*
 * wire an audio port to an audio output
 * This can be used to rewire different post plugins to the audio output
 * plugin layer. The ports you hand in at xine_post_init() will already
 * be wired with the post plugin, so you need this function for
 * _re_connecting only.
 *
 * returns 1 on success, 0 on failure
 */
int xine_post_wire_audio_port(xine_post_out_t *source, xine_audio_port_t *vo);

/*
 * Extracts an output for a stream. Use this to rewire the outputs of streams.
 */
xine_post_out_t * xine_get_video_source(xine_stream_t *stream);
xine_post_out_t * xine_get_audio_source(xine_stream_t *stream);

/*
 * disposes the post plugin
 * please make sure that no other post plugin and no stream is
 * connected to any of this plugin's inputs
 */
void xine_post_dispose(xine_t *xine, xine_post_t *self);


/* post plugin types */
#define XINE_POST_TYPE_VIDEO_FILTER		0x010000
#define XINE_POST_TYPE_VIDEO_VISUALIZATION	0x010001
#define XINE_POST_TYPE_AUDIO_FILTER		0x020000
#define XINE_POST_TYPE_AUDIO_VISUALIZATION	0x020001


/* post plugin data types */

/* video port data
 * input->data is a xine_video_port_t*
 * output->data usually is a xine_video_port_t**
 */
#define XINE_POST_DATA_VIDEO          0

/* audio port data
 * input->data is a xine_audio_port_t*
 * output->data usually is a xine_audio_port_t**
 */
#define XINE_POST_DATA_AUDIO          1

/* integer data
 * input->data is a int*
 * output->data usually is a int*
 */
#define XINE_POST_DATA_INT            3

/* double precision floating point data
 * input->data is a double*
 * output->data usually is a double*
 */
#define XINE_POST_DATA_DOUBLE         4


/*********************************************************************
 * information retrieval                                             *
 *********************************************************************/

/*
 * xine log functions
 *
 * frontends can display xine log output using these functions
 */
int    xine_get_log_section_count(xine_t *self);

/* return a NULL terminated array of log sections names */
STRING *xine_get_log_names(xine_t *self);

/* print some log information to <buf> section */
#ifdef SWIG
void   xine_log (xine_t *self, int buf,
		 const char *xine_log_format, const char *str);
#else
void   xine_log (xine_t *self, int buf,
		 const char *format, ...);
#endif
  
/* get log messages of specified section */
STRING *xine_get_log (xine_t *self, int buf);

/* log callback will be called whenever something is logged */
typedef void (*xine_log_cb_t) (void *user_data, int section);
void   xine_register_log_cb (xine_t *self, xine_log_cb_t cb,
			     void *user_data);

/*
 * error handling / engine status
 */

/* return last error  */
int  xine_get_error (xine_stream_t *stream);

/* get current xine engine status (constants see below) */
int  xine_get_status (xine_stream_t *stream);

/*
 * engine status codes
 */
#define XINE_STATUS_IDLE                   0 /* no mrl assigned */
#define XINE_STATUS_STOP                   1
#define XINE_STATUS_PLAY                   2
#define XINE_STATUS_QUIT                   3

/*
 * xine error codes
 */
#define XINE_ERROR_NONE                    0
#define XINE_ERROR_NO_INPUT_PLUGIN         1
#define XINE_ERROR_NO_DEMUX_PLUGIN         2
#define XINE_ERROR_DEMUX_FAILED            3
#define XINE_ERROR_MALFORMED_MRL           4

/*
 * try to find out audio/spu language of given channel
 * (use -1 for current channel)
 *
 * returns 1 on success, 0 on failure
 */
int xine_get_audio_lang (xine_stream_t *stream, int channel,
			 char *lang);
int xine_get_spu_lang   (xine_stream_t *stream, int channel,
			 char *lang);

/*
 * get position / length information
 *
 * depending of the nature and system layer of the stream,
 * some or all of this information may be unavailable or incorrect
 * (e.g. live network streams may not have a valid length)
 *
 * returns 1 on success, 0 on failure (data was not updated,
 * probably because it's not known yet... try again later)
 */
int  xine_get_pos_length (xine_stream_t *stream,
			  int *pos_stream,  /* 0..65535     */
			  int *pos_time,    /* milliseconds */
			  int *length_time);/* milliseconds */

/*
 * get information about the stream such as
 * video width/height, codecs, audio format, title, author...
 *
 * constants see below
 */
uint32_t    xine_get_stream_info (xine_stream_t *stream, int info);
const char *xine_get_meta_info   (xine_stream_t *stream, int info);

/* xine_get_stream_info */
#define XINE_STREAM_INFO_BITRATE           0
#define XINE_STREAM_INFO_SEEKABLE          1
#define XINE_STREAM_INFO_VIDEO_WIDTH       2
#define XINE_STREAM_INFO_VIDEO_HEIGHT      3
#define XINE_STREAM_INFO_VIDEO_RATIO       4 /* *10000 */
#define XINE_STREAM_INFO_VIDEO_CHANNELS    5
#define XINE_STREAM_INFO_VIDEO_STREAMS     6
#define XINE_STREAM_INFO_VIDEO_BITRATE     7
#define XINE_STREAM_INFO_VIDEO_FOURCC      8
#define XINE_STREAM_INFO_VIDEO_HANDLED     9  /* codec available? */
#define XINE_STREAM_INFO_FRAME_DURATION    10 /* 1/90000 sec */
#define XINE_STREAM_INFO_AUDIO_CHANNELS    11
#define XINE_STREAM_INFO_AUDIO_BITS        12
#define XINE_STREAM_INFO_AUDIO_SAMPLERATE  13
#define XINE_STREAM_INFO_AUDIO_BITRATE     14
#define XINE_STREAM_INFO_AUDIO_FOURCC      15
#define XINE_STREAM_INFO_AUDIO_HANDLED     16 /* codec available? */
#define XINE_STREAM_INFO_HAS_CHAPTERS      17
#define XINE_STREAM_INFO_HAS_VIDEO         18
#define XINE_STREAM_INFO_HAS_AUDIO         19
#define XINE_STREAM_INFO_IGNORE_VIDEO      20
#define XINE_STREAM_INFO_IGNORE_AUDIO      21
#define XINE_STREAM_INFO_IGNORE_SPU        22
#define XINE_STREAM_INFO_VIDEO_HAS_STILL   23
#define XINE_STREAM_INFO_MAX_AUDIO_CHANNEL 24
#define XINE_STREAM_INFO_MAX_SPU_CHANNEL   25

/* xine_get_meta_info */
#define XINE_META_INFO_TITLE               0
#define XINE_META_INFO_COMMENT             1
#define XINE_META_INFO_ARTIST              2
#define XINE_META_INFO_GENRE               3
#define XINE_META_INFO_ALBUM               4
#define XINE_META_INFO_YEAR                5
#define XINE_META_INFO_VIDEOCODEC          6
#define XINE_META_INFO_AUDIOCODEC          7
#define XINE_META_INFO_SYSTEMLAYER         8
#define XINE_META_INFO_INPUT_PLUGIN        9


/*********************************************************************
 * plugin management / autoplay / mrl browsing                       *
 *********************************************************************/

/*
 * note: the pointers to strings or string arrays returned
 *       by some of these functions are pointers to statically
 *       alloced internal xine memory chunks.
 *       they're only valid between xine function calls
 *       and should never be free()d.
 */
#ifndef SWIG
typedef struct {
  char      *origin; /* file plugin: path */
  char      *mrl;    /* <type>://<location> */
  char      *link;
  uint32_t   type;   /* see below */
  off_t      size;   /* size of this source, may be 0 */
} xine_mrl_t;
#endif
  
/* mrl types */
#define XINE_MRL_TYPE_unknown        (0 << 0)
#define XINE_MRL_TYPE_dvd            (1 << 0)
#define XINE_MRL_TYPE_vcd            (1 << 1)
#define XINE_MRL_TYPE_net            (1 << 2)
#define XINE_MRL_TYPE_rtp            (1 << 3)
#define XINE_MRL_TYPE_stdin          (1 << 4)
#define XINE_MRL_TYPE_cda            (1 << 5)
#define XINE_MRL_TYPE_file           (1 << 6)
#define XINE_MRL_TYPE_file_fifo      (1 << 7)
#define XINE_MRL_TYPE_file_chardev   (1 << 8)
#define XINE_MRL_TYPE_file_directory (1 << 9)
#define XINE_MRL_TYPE_file_blockdev  (1 << 10)
#define XINE_MRL_TYPE_file_normal    (1 << 11)
#define XINE_MRL_TYPE_file_symlink   (1 << 12)
#define XINE_MRL_TYPE_file_sock      (1 << 13)
#define XINE_MRL_TYPE_file_exec      (1 << 14)
#define XINE_MRL_TYPE_file_backup    (1 << 15)
#define XINE_MRL_TYPE_file_hidden    (1 << 16)

/* get a list of browsable input plugin ids */
STRING *xine_get_browsable_input_plugin_ids (xine_t *self) ;

/*
 * ask input plugin named <plugin_id> to return
 * a list of available MRLs in domain/directory <start_mrl>.
 *
 * <start_mrl> may be NULL indicating the toplevel domain/dir
 * returns <start_mrl> if <start_mrl> is a valid MRL, not a directory
 * returns NULL if <start_mrl> is an invalid MRL, not even a directory.
 */
xine_mrl_t **xine_get_browse_mrls (xine_t *self,
				   const char *plugin_id,
				   const char *start_mrl,
				   int *num_mrls);

/* get a list of plugins that support the autoplay feature */
STRING *xine_get_autoplay_input_plugin_ids (xine_t *self);

/* get autoplay MRL list from input plugin named <plugin_id> */
STRING *xine_get_autoplay_mrls (xine_t *self,
			       const char *plugin_id,
			       int *num_mrls);

/* get a list of file extensions for file types supported by xine
 * the list is separated by spaces
 *
 * the pointer returned can be free()ed when no longer used */
char *xine_get_file_extensions (xine_t *self);

/* get a list of mime types supported by xine
 *
 * the pointer returned can be free()ed when no longer used */
char *xine_get_mime_types (xine_t *self);

/* get the demuxer identifier that handles a given mime type
 *
 * the pointer returned can be free()ed when no longer used
 * returns NULL if no demuxer is available to handle this. */
char *xine_get_demux_for_mime_type (xine_t *self, const char *mime_type);

/* get a description string for an input plugin */
const char *xine_get_input_plugin_description (xine_t *self,
					       const char *plugin_id);

/* get lists of available audio and video output plugins */
STRING *xine_list_audio_output_plugins (xine_t *self) ;
STRING *xine_list_video_output_plugins (xine_t *self) ;


/*********************************************************************
 * visual specific gui <-> xine engine communication                 *
 *********************************************************************/

/* talk to video output driver */
int    xine_gui_send_vo_data (xine_stream_t *self,
			      int type, void *data);

typedef struct {

  /* area of that drawable to be used by video */
  int      x,y,w,h;

} x11_rectangle_t;

#ifndef SWIG  
/*
 * this is the visual data struct any x11 gui
 * must supply to the xine_open_video_driver call
 * ("data" parameter)
 */
typedef struct {

  /* some information about the display */
  void             *display; /* Display* */
  int               screen;

  /* drawable to display the video in/on */
  unsigned long     d; /* Drawable */

  void             *user_data;

  /*
   * dest size callback
   *
   * this will be called by the video driver to find out
   * how big the video output area size will be for a
   * given video size. The ui should _not_ adjust it's
   * video out area, just do some calculations and return
   * the size. This will be called for every frame, ui
   * implementation should be fast.
   * dest_pixel_aspect should be set to the used display pixel aspect.
   * NOTE: Semantics has changed: video_width and video_height
   * are no longer pixel aspect corrected. Get the old semantics
   * in the UI with
   *   *dest_pixel_aspect = display_pixel_aspect;
   *   if (video_pixel_aspect >= display_pixel_aspect)
   *     video_width  = video_width * video_pixel_aspect / display_pixel_aspect + .5;
   *   else
   *     video_height = video_height * display_pixel_aspect / video_pixel_aspect + .5;
   */
  void (*dest_size_cb) (void *user_data,
			int video_width, int video_height,
			double video_pixel_aspect,
			int *dest_width, int *dest_height,
			double *dest_pixel_aspect);

  /*
   * frame output callback
   *
   * this will be called by the video driver for every frame
   * it's about to draw. ui can adapt it's size if necessary
   * here.
   * note: the ui doesn't have to adjust itself to this
   * size, this is just to be taken as a hint.
   * ui must return the actual size of the video output
   * area and the video output driver will do it's best
   * to adjust the video frames to that size (while
   * preserving aspect ratio and stuff).
   *    dest_x, dest_y: offset inside window
   *    dest_width, dest_height: available drawing space
   *    dest_pixel_aspect: display pixel aspect
   *    win_x, win_y: window absolute screen position
   * NOTE: Semantics has changed: video_width and video_height
   * are no longer pixel aspect corrected. Get the old semantics
   * in the UI with
   *   *dest_pixel_aspect = display_pixel_aspect;
   *   if (video_pixel_aspect >= display_pixel_aspect)
   *     video_width  = video_width * video_pixel_aspect / display_pixel_aspect + .5;
   *   else
   *     video_height = video_height * display_pixel_aspect / video_pixel_aspect + .5;
   */
  void (*frame_output_cb) (void *user_data,
			   int video_width, int video_height,
			   double video_pixel_aspect,
			   int *dest_x, int *dest_y,
			   int *dest_width, int *dest_height,
			   double *dest_pixel_aspect,
			   int *win_x, int *win_y);

} x11_visual_t;
#endif
  
/*
 * "type" constants for xine_gui_send_vo_data (...)
 */

/* xevent *data */
#define XINE_GUI_SEND_COMPLETION_EVENT       1

/* Drawable data */
#define XINE_GUI_SEND_DRAWABLE_CHANGED       2

/* xevent *data */
#define XINE_GUI_SEND_EXPOSE_EVENT           3

/* x11_rectangle_t *data */
#define XINE_GUI_SEND_TRANSLATE_GUI_TO_VIDEO 4

/* int data */
#define XINE_GUI_SEND_VIDEOWIN_VISIBLE	     5

/* *data contains chosen visual, select a new one or change it to NULL
 * to indicate the visual to use or that no visual will work */
/* XVisualInfo **data */
#define XINE_GUI_SEND_SELECT_VISUAL          8

#ifndef SWIG
/*********************************************************************
 * xine health check stuff                                           *
 *********************************************************************/

#define XINE_HEALTH_CHECK_OK            0
#define XINE_HEALTH_CHECK_FAIL          1
#define XINE_HEALTH_CHECK_UNSUPPORTED   2
#define XINE_HEALTH_CHECK_NO_SUCH_CHECK 3

#define CHECK_KERNEL    0
#define CHECK_MTRR      1
#define CHECK_CDROM     2
#define CHECK_DVDROM    3
#define CHECK_DMA       4
#define CHECK_X         5
#define CHECK_XV        6

struct xine_health_check_s {
  int         status;
  const char* cdrom_dev;
  const char* dvd_dev;
  char*       msg;
  char*       title;
  char*       explanation;
};

typedef struct xine_health_check_s xine_health_check_t;
xine_health_check_t* xine_health_check(xine_health_check_t*, int check_num);

#endif /* !SWIG */

/*********************************************************************
 * configuration system                                              *
 *********************************************************************/

/*
 * config entry data types
 */

#define XINE_CONFIG_TYPE_UNKNOWN 0
#define XINE_CONFIG_TYPE_RANGE   1
#define XINE_CONFIG_TYPE_STRING  2
#define XINE_CONFIG_TYPE_ENUM    3
#define XINE_CONFIG_TYPE_NUM     4
#define XINE_CONFIG_TYPE_BOOL    5

typedef struct xine_cfg_entry_s xine_cfg_entry_t;

typedef void (*xine_config_cb_t) (void *user_data,
				  xine_cfg_entry_t *entry);
struct xine_cfg_entry_s {
  STRING           key;     /* unique id (example: gui.logo_mrl) */

  int              type;

  /* type unknown */
  char            *unknown_value;

  /* type string */
  char            *str_value;
  char            *str_default;
  char            *str_sticky;

  /* common to range, enum, num, bool: */
  int              num_value;
  int              num_default;

  /* type range specific: */
  int              range_min;
  int              range_max;

  /* type enum specific: */
  char           **enum_values;

  /* help info for the user */
  STRING           description;
  STRING           help;

  /* user experience level */
  int              exp_level; /* 0 => beginner,
			        10 => advanced user,
			        20 => expert */
#ifndef SWIG
  /* callback function and data for live changeable values */
  xine_config_cb_t callback;
  void            *callback_data;
#endif
};

const char *xine_config_register_string (xine_t *self,
					 const char *key,
					 const char *def_value,
					 const char *description,
					 const char *help,
					 int   exp_level,
					 xine_config_cb_t changed_cb,
					 void *cb_data);

int   xine_config_register_range  (xine_t *self,
				   const char *key,
				   int def_value,
				   int min, int max,
				   const char *description,
				   const char *help,
				   int   exp_level,
				   xine_config_cb_t changed_cb,
				   void *cb_data);

int   xine_config_register_enum   (xine_t *self,
				   const char *key,
				   int def_value,
				   char **values,
				   const char *description,
				   const char *help,
				   int   exp_level,
				   xine_config_cb_t changed_cb,
				   void *cb_data);

int   xine_config_register_num    (xine_t *self,
				   const char *key,
				   int def_value,
				   const char *description,
				   const char *help,
				   int   exp_level,
				   xine_config_cb_t changed_cb,
				   void *cb_data);

int   xine_config_register_bool   (xine_t *self,
				   const char *key,
				   int def_value,
				   const char *description,
				   const char *help,
				   int   exp_level,
				   xine_config_cb_t changed_cb,
				   void *cb_data);

/*
 * the following functions will copy data from the internal xine_config
 * data database to the xine_cfg_entry_t *entry you provide
 *
 * they return 1 on success, 0 on failure
 */

/* get first config item */
int  xine_config_get_first_entry (xine_t *self, xine_cfg_entry_t *OUTPUT);

/* get next config item (iterate through the items) */
int  xine_config_get_next_entry (xine_t *self, xine_cfg_entry_t *OUTPUT);

/* search for a config entry by key */
int  xine_config_lookup_entry (xine_t *self, const char *key,
			       xine_cfg_entry_t *OUTPUT);

/*
 * update a config entry (which was returned from lookup_entry() )
 *
 * xine will make a deep copy of the data in the entry into it's internal
 * config database.
 */
void xine_config_update_entry (xine_t *self,
			       const xine_cfg_entry_t *entry);

/*
 * load/save config data from/to afile (e.g. $HOME/.xine/config)
 */
void xine_config_load  (xine_t *self, const char *cfg_filename);
void xine_config_save  (xine_t *self, const char *cfg_filename);
void xine_config_reset (xine_t *self);


/*********************************************************************
 * asynchroneous xine event mechanism                                *
 *********************************************************************/

/*
 * to receive events you have to register an event queue with
 * the xine engine (xine_event_new_queue, see below).
 *
 * then you can either
 * 1) check for incoming events regularly (xine_event_get/wait),
 *    process them and free them using xine_event_free
 * 2) use xine_event_create_listener_thread and specify a callback
 *    which will then be called for each event
 *
 * to send events to every module listening you don't need
 * to register an event queue but simply call xine_event_send.
 */

/* event types */
#define XINE_EVENT_UI_PLAYBACK_FINISHED   1 /* frontend can e.g. move on to next playlist entry */
#define XINE_EVENT_UI_CHANNELS_CHANGED    2 /* inform ui that new channel info is available */
#define XINE_EVENT_UI_SET_TITLE           3 /* request title display change in ui */
#define XINE_EVENT_UI_MESSAGE             4 /* message (dialog) for the ui to display */
#define XINE_EVENT_FRAME_FORMAT_CHANGE    5 /* e.g. aspect ratio change during dvd playback */
#define XINE_EVENT_AUDIO_LEVEL            6 /* report current audio level (l/r) */
#define XINE_EVENT_QUIT                   7 /* last event sent when stream is disposed */
#define XINE_EVENT_PROGRESS               8 /* index creation/network connections */
#define XINE_EVENT_MRL_REFERENCE          9 /* demuxer->frontend: MRL reference(s) for the real stream */

/* input events coming from frontend */
#define XINE_EVENT_INPUT_MOUSE_BUTTON   101
#define XINE_EVENT_INPUT_MOUSE_MOVE     102
#define XINE_EVENT_INPUT_MENU1          103
#define XINE_EVENT_INPUT_MENU2          104
#define XINE_EVENT_INPUT_MENU3          105
#define XINE_EVENT_INPUT_MENU4          106
#define XINE_EVENT_INPUT_MENU5          107
#define XINE_EVENT_INPUT_MENU6          108
#define XINE_EVENT_INPUT_MENU7          109
#define XINE_EVENT_INPUT_UP             110
#define XINE_EVENT_INPUT_DOWN           111
#define XINE_EVENT_INPUT_LEFT           112
#define XINE_EVENT_INPUT_RIGHT          113
#define XINE_EVENT_INPUT_SELECT         114
#define XINE_EVENT_INPUT_NEXT           115
#define XINE_EVENT_INPUT_PREVIOUS       116
#define XINE_EVENT_INPUT_ANGLE_NEXT     117
#define XINE_EVENT_INPUT_ANGLE_PREVIOUS 118
#define XINE_EVENT_INPUT_BUTTON_FORCE   119
#define XINE_EVENT_INPUT_NUMBER_0       120
#define XINE_EVENT_INPUT_NUMBER_1       121
#define XINE_EVENT_INPUT_NUMBER_2       122
#define XINE_EVENT_INPUT_NUMBER_3       123
#define XINE_EVENT_INPUT_NUMBER_4       124
#define XINE_EVENT_INPUT_NUMBER_5       125
#define XINE_EVENT_INPUT_NUMBER_6       126
#define XINE_EVENT_INPUT_NUMBER_7       127
#define XINE_EVENT_INPUT_NUMBER_8       128
#define XINE_EVENT_INPUT_NUMBER_9       129
#define XINE_EVENT_INPUT_NUMBER_10_ADD  130

/*
 * xine event struct
 */
typedef struct {
  int                              type;   /* event type (constants see above) */
  xine_stream_t                   *stream; /* stream this event belongs to     */

  void                            *data;   /* contents depending on type */
  int                              data_length;

  /* you do not have to provide this, it will be filled in by xine_event_send() */
  struct timeval                   tv;     /* timestamp of event creation */
} xine_event_t;

/*
 * input event dynamic data
 */
typedef struct {
  xine_event_t        event;
  uint8_t             button; /* Generally 1 = left, 2 = mid, 3 = right */
  uint16_t            x,y;    /* In Image space */
} xine_input_data_t;

/*
 * UI event dynamic data - send information to/from UI.
 */
typedef struct {
  int                 num_buttons;
  int                 str_len;
  char                str[256]; /* might be longer */
} xine_ui_data_t;

/*
 * notify frame format change
 */
typedef struct {
  int                 width;
  int                 height;
  int                 aspect;
} xine_format_change_data_t;

/*
 * audio level for left/right channel
 */
typedef struct {
  int                 left;
  int                 right;  /* 0..255 */
} xine_audio_level_data_t;

/*
 * index generation / buffering
 */
typedef struct {
  const char         *description; /* e.g. "connecting..." */
  int                 percent;
} xine_progress_data_t;

/*
 * mrl reference data is sent by demuxers when a reference stream is found.
 * this stream just contains pointers (urls) to the real data, which are
 * passed to frontend using this event type. (examples: .asx, .mov and .ram)
 * 
 * ideally, frontends should add these mrls to a "hierarchical playlist". 
 * that is, instead of the original file, the ones provided here should be
 * played instead. on pratice, just using a simple playlist should work.
 *
 * mrl references should be played in the same order they are received, just
 * after the current stream finishes.
 * alternative playlists may be provided and should be used in case of
 * failure of the primary playlist.
 */
typedef struct {
  int                 alternative; /* alternative playlist number, usually 0 */
  char                mrl[1]; /* might (will) be longer */
} xine_mrl_reference_data_t;


/* opaque xine_event_queue_t */
typedef struct xine_event_queue_s xine_event_queue_t;

/*
 * register a new event queue
 *
 * you have to receive messages from this queue regularly
 *
 * use xine_event_dispose_queue to unregister and free the queue
 */
xine_event_queue_t *xine_event_new_queue (xine_stream_t *stream);
void xine_event_dispose_queue (xine_event_queue_t *queue);

/*
 * receive events (poll)
 *
 * use xine_event_free on the events received from these calls
 * when they're no longer needed
 */
xine_event_t *xine_event_get  (xine_event_queue_t *queue);
xine_event_t *xine_event_wait (xine_event_queue_t *queue);
void          xine_event_free (xine_event_t *event);

/*
 * receive events (callback)
 *
 * a thread is created which will receive all events from
 * the specified queue, call your callback on each of them
 * and will then free the event when your callback returns
 *
 */
typedef void (*xine_event_listener_cb_t) (void *user_data,
					  const xine_event_t *event);
void xine_event_create_listener_thread (xine_event_queue_t *queue,
					xine_event_listener_cb_t callback,
					void *user_data);

/*
 * send an event to all queues
 *
 * the event will be copied so you can free or reuse
 * *event as soon as xine_event_send returns.
 */
void xine_event_send (xine_stream_t *stream, const xine_event_t *event);


/*********************************************************************
 * OSD (on screen display)                                           *
 *********************************************************************/

#define XINE_TEXT_PALETTE_SIZE 11

#define XINE_OSD_TEXT1  (0 * XINE_TEXT_PALETTE_SIZE)
#define XINE_OSD_TEXT2  (1 * XINE_TEXT_PALETTE_SIZE)
#define XINE_OSD_TEXT3  (2 * XINE_TEXT_PALETTE_SIZE)
#define XINE_OSD_TEXT4  (3 * XINE_TEXT_PALETTE_SIZE)
#define XINE_OSD_TEXT5  (4 * XINE_TEXT_PALETTE_SIZE)
#define XINE_OSD_TEXT6  (5 * XINE_TEXT_PALETTE_SIZE)
#define XINE_OSD_TEXT7  (6 * XINE_TEXT_PALETTE_SIZE)
#define XINE_OSD_TEXT8  (7 * XINE_TEXT_PALETTE_SIZE)
#define XINE_OSD_TEXT9  (8 * XINE_TEXT_PALETTE_SIZE)
#define XINE_OSD_TEXT10 (9 * XINE_TEXT_PALETTE_SIZE)

/* white text, black border, transparent background  */
#define XINE_TEXTPALETTE_WHITE_BLACK_TRANSPARENT    0
/* white text, noborder, transparent background      */
#define XINE_TEXTPALETTE_WHITE_NONE_TRANSPARENT     1
/* white text, no border, translucid background      */
#define XINE_TEXTPALETTE_WHITE_NONE_TRANSLUCID      2
/* yellow text, black border, transparent background */
#define XINE_TEXTPALETTE_YELLOW_BLACK_TRANSPARENT   3

typedef struct xine_osd_s xine_osd_t;

xine_osd_t *xine_osd_new           (xine_stream_t *self, int x, int y,
				    int width, int height);
void        xine_osd_draw_point    (xine_osd_t *self, int x, int y, int color);

void        xine_osd_draw_line     (xine_osd_t *self, int x1, int y1,
				    int x2, int y2, int color);
void        xine_osd_draw_rect     (xine_osd_t *self, int x1, int y1,
				    int x2, int y2,
				    int color, int filled );
void        xine_osd_draw_text     (xine_osd_t *self, int x1, int y1,
				    const char *text, int color_base);
void        xine_osd_get_text_size (xine_osd_t *self, const char *text,
				    int *width, int *height);
void        xine_osd_set_font      (xine_osd_t *self, const char *fontname,
				    int size);
/* set position were overlay will be blended */
void        xine_osd_set_position  (xine_osd_t *self, int x, int y);
void        xine_osd_show          (xine_osd_t *self, int64_t vpts);
void        xine_osd_hide          (xine_osd_t *self, int64_t vpts);
/* empty drawing area */
void        xine_osd_clear         (xine_osd_t *self);
/*
 * close osd rendering engine
 * loaded fonts are unloaded
 * osd objects are closed
 */
void        xine_osd_free          (xine_osd_t *self);
void        xine_osd_set_palette   (xine_osd_t *self,
				    color_t *INPUT, trans_t *INPUT);
/*
 * set on existing text palette
 * (-1 to set used specified palette)
 *
 * color_base specifies the first color index to use for this text
 * palette. The OSD palette is then modified starting at this
 * color index, up to the size of the text palette.
 *
 * Use OSD_TEXT1, OSD_TEXT2, ... for some preasssigned color indices.
 */
void        xine_osd_set_text_palette (xine_osd_t *self,
				       int palette_number,
				       int color_base );
/* get palette (color and transparency) */
void        xine_osd_get_palette   (xine_osd_t *self,
				    color_t *OUTPUT, trans_t *OUTPUT);


#ifndef SWIG  
/*********************************************************************
 * TV-mode API, to make it possible to use nvtvd to view movies      *
 *********************************************************************/

/* connect to nvtvd server and save current TV and X settings */
void xine_tvmode_init (xine_t *self);

/* try to change TV state if enabled
 *   type select 'regular' (0) or 'TV' (1) state
 *   width frame width the mode should match best or 0 if unknown
 *   height frame height the mode should match best or 0 if unknown
 *   fps frame rate the mode should match best or 0 if unknown
 * returns: finally selected state
 */
int xine_tvmode_switch (xine_t *self, int type, int width, int height, double fps);

/* adapt (maximum) output size to visible area if necessary and return pixel
 * aspect and real frame rate if available
 */
void xine_tvmode_size (xine_t *self, int *width, int *height,
		       double *pixelratio, double *fps);

/* restore old TV and X settings and close nvtvd connection */
void xine_tvmode_exit (xine_t *self);
       
#endif /* !SWIG */  
#ifdef __cplusplus
}
#endif

#endif
