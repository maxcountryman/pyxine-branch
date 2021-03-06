
DEF DEPRICATED = False

# Pseudo Types to make cython happy
cdef extern from *:
	ctypedef char* const_char_ptr    "const char*"
	ctypedef char* ConstCharPtr      "const char"
	ctypedef char* ConstCharConstPtr "const char *const"
	ctypedef char* CharConstPtr      "char *const"
	ctypedef void * VoidPtr          "void *"
	ctypedef int *intp
	ctypedef int uInt8               "uint8_t"
	ctypedef int uInt16              "uint16_t"
	ctypedef int uInt32              "uint32_t"
	ctypedef int uInt64              "uint64_t"
	ctypedef int int32               "int32_t"
	ctypedef int int64               "int64_t"
	ctypedef char* VaList            "va_list"
	ctypedef long off_t
	ctypedef unsigned long int uint32_t

cdef extern from "xine_internal.h":
	# Forward Declaration
	ctypedef extern struct xine_t
	ctypedef extern struct metronom_t
	ctypedef extern struct input_plugin_t
	ctypedef extern struct xine_event_queue_s
	# Type Def
	ctypedef xine_event_queue_s xine_event_queue_t
	
	cdef extern struct xine_stream_s
	ctypedef xine_stream_s xine_stream_t

cdef extern from "xine.h":
	cdef extern struct xine_s
	cdef extern struct xine_audio_port_s
	cdef extern struct xine_video_port_s
	cdef extern struct xine_mrl_t:
		char		*origin # file plugin: path 
		char		*mrl    # <type>://<location> 
		char		*link
		uint32_t	type   # see below 
		off_t		size   # size of this source, may be 0
		
	cdef extern struct xine_config_entry_translation_t:
		ConstCharPtr *old_name, *new_name

	ctypedef xine_audio_port_s xine_audio_port_t
	ctypedef xine_video_port_s xine_video_port_t
	
	cdef extern struct xine_post_s:
		xine_audio_port_t **audio_input
		xine_video_port_t **video_input
		int type
	
	cdef extern struct xine_current_frame_data_t:
		int width
		int height
		int crop_left
		int crop_right
		int crop_top
		int crop_bottom
		int ratio_code
		int interlaced
		int format
		int img_size
		uInt8 *img
		
	cdef extern struct xine_post_out_s
	cdef extern struct xine_post_in_s:
		ConstCharPtr	 *name
		int		 type
		void		 *void
		
	ctypedef xine_post_in_s xine_post_in_t
	ctypedef xine_post_out_s xine_post_out_t
	
	cdef extern struct xine_post_out_s:
		ConstCharPtr	  *name
		int               type
		void		  *void
		int (*rewire) (xine_post_out_t *self, void *data)
	
	
	ctypedef void (*xine_config_cb_t)
	cdef extern struct xine_cfg_entry_s:
		ConstCharPtr 	 *key
		int		 type
		char		 *unknown_value
		char             *str_value
		char		 *str_default
		void		 *dummy
		int		 *num_value
		int		 *num_default
		int		 *range_min
		int		 *range_max
		char		 **enum_values
		ConstCharPtr	 *description
		ConstCharPtr	 *help
		int		 exp_level
		xine_config_cb_t callback
		void		 *callback_data
		
	cdef extern struct timeval:
		pass
	cdef extern struct xine_event_t:
		int						type
		xine_stream_t			*stream
		void					*data
		int						data_length
		timeval				tv
		
	cdef extern struct xine_input_data_t:
		xine_event_t		event
		uInt8				button # Generally 1 = left, 2 = mid, 3 = right
		uInt16				x,y    # In Image space
		
	cdef extern struct xine_ui_data_t:
		int					num_buttons
		int					str_len
		char				str[256]
		
	cdef extern struct xine_message_ui_data_t:
		xine_ui_data_t		compatibility
		int					type
		int					explanation
		int					num_parameters
		int					parameters
		char				messages[1]
		
	cdef extern struct xine_format_change_data_t:
		int					width
		int					height
		int					aspect
		int					pan_scan
		
	cdef extern struct xine_audio_level_data_t:
		int					left  #0...100%
		int					right #0...100%
		int					mute
		
	cdef extern struct xine_progress_data_t:
		ConstCharPtr		*description # e.g. "connecting..."
		int					percent
		
	cdef extern struct xine_mrl_reference_data_ext_t:
		int					alternative 		 # Alternative playlist number, usually 0
		uInt32				start_time, duration # Milliseconds
		uInt32				spare[20]			 # For future expansion
		ConstCharPtr		mrl[1]
		
	cdef extern struct xine_set_mpeg_data_t:
		int		bitrate_vbr   # 1 = vbr, 0 = cbr 
		int		bitrate_mean  # mean (target) bitrate in kbps
		int		bitrate_peak  # peak (max) bitrate in kbps
		int		gop_size      # GOP size in frames
		int		gop_closure   # open/closed GOP
		int		b_frames	  # number of B frames to use
		int		aspect_ratio  # XINE_VO_ASPECT_xxx
		uInt32	spare[20]
		
	cdef extern struct xine_spu_button_t:
		int		direction
		int32	button
		
	cdef extern struct xine_dropped_frame_t:
		int skipped_frames
		int skipped_threshold
		int discarded_frames
		int discarded_threshold
		

	
	ctypedef xine_cfg_entry_s xine_cfg_entry_t
	ctypedef void (*xine_config_cb_t) (void *user_data,xine_cfg_entry_t *entry)
	ctypedef xine_post_s xine_post_t
	ctypedef xine_s xine_t
	ctypedef xine_cfg_entry_t Const_xine_cfg_entry_t  "const xine_cfg_entry_t"
	ctypedef xine_event_t Const_xine_event_t "const xine_event_t"
	ctypedef xine_mrl_t XineMrlDbl  "xine_mrl_t *"



# Version stuff
# DONE
cdef extern const_char_ptr xine_get_version_string()
# DONE
cdef extern void xine_get_version (int *major, int *minor, int *sub)
# DONE
cdef extern int xine_check_version(int major, int minor, int sub)
# Xine creation and deletion
# DONE
cdef extern xine_t *xine_new()
# DONE
cdef extern void xine_init (xine_t *self)
# DONE
cdef extern void xine_exit (xine_t *self)
# Open Drivers
# DONE
cdef extern xine_audio_port_t *xine_open_audio_driver(xine_t *self, ConstCharPtr *id,void *data)
# DONE
cdef extern xine_video_port_t *xine_open_video_driver (xine_t *self, ConstCharPtr *id,int visual, void *data)
# Close Drivers
# DONE
cdef extern void xine_close_audio_driver (xine_t *self, xine_audio_port_t  *driver)
# DONE
cdef extern void xine_close_video_driver (xine_t *self, xine_video_port_t  *driver)
# Streams
# DONE
cdef extern xine_stream_t *xine_stream_new(xine_t *self,xine_audio_port_t *ao, xine_video_port_t *vo)
# DONE
cdef extern int xine_stream_master_slave(xine_stream_t *master, xine_stream_t *slave,int affection)
# DONE
cdef extern int xine_open (xine_stream_t *stream, ConstCharPtr *mrl)
# DONE
cdef extern int xine_play (xine_stream_t *stream, int start_pos, int start_time)
# DONE
cdef extern void xine_stop (xine_stream_t *stream)
# DONE
cdef extern void xine_close (xine_stream_t *stream)
# DONE
cdef extern int xine_eject (xine_stream_t *stream)
# DONE
cdef extern void xine_dispose (xine_stream_t *stream)

#### Engine ##################################################################
# DONE
cdef extern void xine_engine_set_param(xine_t *self, int param, int value)
# DONE
cdef extern int xine_engine_get_param(xine_t *self, int param)

#### Video ###################################################################

# ----- Not implemented -----
#cdef extern int xine_get_current_frame (xine_stream_t *stream,int *width, int *height,int *ratio_code, int *format,uInt8 *img)
#cdef extern int xine_get_current_frame_s (xine_stream_t *stream,int *width, int *height,int *ratio_code, int *format,uInt8 *img, int *img_size)
#cdef extern int xine_get_current_frame_alloc (xine_stream_t *stream,int *width, int *height,int *ratio_code, int *format,uInt8 **img, int *img_size)
#cdef extern int xine_get_current_frame_data (xine_stream_t *stream,xine_current_frame_data_t *data,int flags)
#cdef extern int64 xine_get_current_vpts(xine_stream_t *stream)
# ----- End -----

#### Post ####################################################################
cdef extern xine_post_t *xine_post_init(xine_t *xine, ConstCharPtr *name,int inputs,xine_audio_port_t **audio_target,xine_video_port_t **video_target)
cdef extern ConstCharConstPtr *xine_list_post_plugins(xine_t *xine)
cdef extern ConstCharConstPtr *xine_list_post_plugins_typed(xine_t *xine, int type)
cdef extern ConstCharConstPtr *xine_post_list_inputs(xine_post_t *self)
cdef extern ConstCharConstPtr *xine_post_list_outputs(xine_post_t *self)
cdef extern xine_post_in_t *xine_post_input(xine_post_t *self, ConstCharPtr *name)
cdef extern xine_post_out_t *xine_post_output(xine_post_t *self, ConstCharPtr *name)
cdef extern int xine_post_wire(xine_post_out_t *source, xine_post_in_t *target)
cdef extern int xine_post_wire_video_port(xine_post_out_t *source, xine_video_port_t *vo)
cdef extern int xine_post_wire_audio_port(xine_post_out_t *source, xine_audio_port_t *ao)

# Extracts an output for a stream. Use this to rewire the outputs of streams.

cdef extern xine_post_out_t * xine_get_video_source(xine_stream_t *stream)
cdef extern xine_post_out_t * xine_get_audio_source(xine_stream_t *stream)
cdef extern void xine_post_dispose(xine_t *xine, xine_post_t *self)

#### Xine Logging ############################################################
# DONE
cdef extern int xine_get_log_section_count(xine_t *self)
cdef extern ConstCharConstPtr *xine_get_log_names(xine_t *self)
cdef extern void xine_log (xine_t *self, int buf,ConstCharPtr *format, ...)

cdef extern void xine_vlog(xine_t *self, int buf,ConstCharPtr *format, VaList args)
cdef extern CharConstPtr *xine_get_log (xine_t *self, int buf)
ctypedef void (*xine_log_cb_t) (void *user_data, int section)

#### Error Code! #############################################################
# DONE
cdef extern int xine_get_error(xine_stream_t *stream)
# DONE
cdef extern int xine_get_status(xine_stream_t *stream)

#### Foreign Languages #######################################################
cdef extern int xine_get_audio_lang(xine_stream_t *stream, int channel,char *lang)
cdef extern int xine_get_spu_lang(xine_stream_t *stream, int channel,char *lang)

#### Get Position / Length ###################################################
# DONE
cdef extern int xine_get_pos_length(xine_stream_t *stream,int *pos_stream,int *pos_time,int *length_time)
# DONE
cdef extern uInt32 xine_get_stream_info(xine_stream_t *stream, int info)
# DONE
cdef extern ConstCharPtr *xine_get_meta_info(xine_stream_t *stream, int info)

#### Plugins #################################################################

# Get a list of browsable input plugin ids
cdef extern ConstCharConstPtr *xine_get_browsable_input_plugin_ids (xine_t *self)

# Ask input plugin named <plugin_id> to return
# a list of available MRLs in domain/directory <start_mrl>.

# <start_mrl> may be NULL indicating the toplevel domain/dir
# returns <start_mrl> if <start_mrl> is a valid MRL, not a directory
# returns NULL if <start_mrl> is an invalid MRL, not even a directory.

# this is broken because of a struct in a struct

cdef extern XineMrlDbl *xine_get_browse_mrls(xine_t *self,ConstCharPtr *plugin_id,ConstCharPtr *start_mrl,int *num_mrls)
# Get autoplay MRL list from input plugin named <plugin_id>
cdef extern ConstCharConstPtr *xine_get_autoplay_input_plugin_ids (xine_t *self)
# Get a list of file extensions for file types supported by xine
# the list is separated by spaces
# the pointer returned can be free()ed when no longer used
cdef extern char **xine_get_autoplay_mrls (xine_t *self,ConstCharPtr *plugin_id,int *num_mrls)
cdef extern char *xine_get_file_extensions (xine_t *self)
cdef extern char *xine_get_mime_types (xine_t *self)
cdef extern char *xine_get_demux_for_mime_type (xine_t *self, ConstCharPtr *mime_type)
cdef extern ConstCharPtr *xine_get_input_plugin_description (xine_t *self,ConstCharPtr *plugin_id)
cdef extern ConstCharPtr *xine_get_demux_plugin_description (xine_t *self,ConstCharPtr *plugin_id)
cdef extern ConstCharPtr *xine_get_spu_plugin_description   (xine_t *self,ConstCharPtr *plugin_id)
cdef extern ConstCharPtr *xine_get_audio_plugin_description (xine_t *self,ConstCharPtr *plugin_id)
cdef extern ConstCharPtr *xine_get_video_plugin_description (xine_t *self,ConstCharPtr *plugin_id)
cdef extern ConstCharPtr *xine_get_audio_driver_plugin_description (xine_t *self,ConstCharPtr *plugin_id)
cdef extern ConstCharPtr *xine_get_video_driver_plugin_description (xine_t *self,ConstCharPtr *plugin_id)
cdef extern ConstCharPtr *xine_get_post_plugin_description  (xine_t *self,ConstCharPtr *plugin_id)
# Get lists of available audio and video output plugins */
cdef extern ConstCharConstPtr *xine_list_audio_output_plugins (xine_t *self)
cdef extern ConstCharConstPtr *xine_list_video_output_plugins (xine_t *self)
# typemask is (1ULL << XINE_VISUAL_TYPE_FOO) | ...
cdef extern ConstCharConstPtr *xine_list_video_output_plugins_typed (xine_t *self, uInt64 typemask)
# Get list of available demultiplexor plugins 
cdef extern ConstCharConstPtr *xine_list_demuxer_plugins(xine_t *self)
# Get list of available input plugins
cdef extern ConstCharConstPtr *xine_list_input_plugins(xine_t *self)
# Get list of available subpicture plugins
cdef extern ConstCharConstPtr *xine_list_spu_plugins(xine_t *self)
# Get list of available audio and video decoder plugins
cdef extern ConstCharConstPtr *xine_list_audio_decoder_plugins(xine_t *self)
cdef extern ConstCharConstPtr *xine_list_video_decoder_plugins(xine_t *self)
# Unload unused plugins 
cdef extern void xine_plugins_garbage_collector(xine_t *self)
#### Config ##################################################################
cdef extern ConstCharPtr *xine_config_register_string(xine_t *self,ConstCharPtr *key,ConstCharPtr *def_value,ConstCharPtr *description,ConstCharPtr *help,int exp_level,xine_config_cb_t changed_cb,void *cb_data)
cdef extern ConstCharPtr *xine_config_register_filename(xine_t *self,ConstCharPtr *key,ConstCharPtr *def_value,int req_type, ConstCharPtr *description,ConstCharPtr *help,int exp_level,xine_config_cb_t changed_cb,void *cb_data)
cdef extern int xine_config_register_range(xine_t *self,ConstCharPtr *key,int def_value,int min, int max,ConstCharPtr *description,ConstCharPtr *help,int exp_level,xine_config_cb_t changed_cb,void *cb_data)
cdef extern int xine_config_register_enum(xine_t *self,ConstCharPtr *key,int def_value,char **values,ConstCharPtr *description,ConstCharPtr *help,int exp_level,xine_config_cb_t changed_cb,void *cb_data)
cdef extern int xine_config_register_num(xine_t *self,ConstCharPtr *key,int def_value,ConstCharPtr *description,ConstCharPtr *help,int exp_level,xine_config_cb_t changed_cb,void *cb_data)
cdef extern int xine_config_register_bool(xine_t *self,ConstCharPtr *key,int def_value,ConstCharPtr *description,ConstCharPtr *help,int exp_level,xine_config_cb_t changed_cb,void *cb_data)

# The following functions will copy data from the internal xine_config
# data database to the xine_cfg_entry_t *entry you provide
# they return 1 on success, 0 on failure

# Get first config item
cdef extern int xine_config_get_first_entry(xine_t *self, xine_cfg_entry_t *entry)
cdef extern int xine_config_get_next_entry(xine_t *self, xine_cfg_entry_t *entry)
# Search for a config entry by key
cdef extern int xine_config_lookup_entry(xine_t *self, ConstCharPtr *key,xine_cfg_entry_t *entry)
# update a config entry (which was returned from lookup_entry() )
# xine will make a deep copy of the data in the entry into its internal
# config database.
cdef extern void xine_config_update_entry(xine_t *self,Const_xine_cfg_entry_t *entry)
# void xine_config_set_translation_user (const xine_config_entry_translation_t *) XINE_PROTECTED;
cdef extern void xine_config_load(xine_t *self, ConstCharPtr *cfg_filename)
cdef extern void xine_config_save(xine_t *self, ConstCharPtr *cfg_filename)
cdef extern void xine_config_reset(xine_t *self)

#### Event Queue #############################################################
cdef extern xine_event_queue_t *xine_event_new_queue(xine_stream_t *stream)
cdef extern void xine_event_dispose_queue(xine_event_queue_t *queue)
# Fails because of the struct
# cdef extern xine_event_t *xine_event_get  (xine_event_queue_t *queue)
# cdef extern xine_event_t *xine_event_wait(xine_event_queue_t *queue)
# cdef extern void xine_event_free(xine_event_t *event)

ctypedef void (*xine_event_listener_cb_t) (void *user_data,Const_xine_event_t *event)
cdef extern void xine_event_create_listener_thread (xine_event_queue_t *queue,xine_event_listener_cb_t callback,void *user_data)
cdef extern void xine_event_send (xine_stream_t *stream, Const_xine_event_t *event)

# X =  xine.libxine()
# X.xineNew()
# X.xineInit()
# X.xineOpenAudioDriver("auto")
# X.xineStreamNew()
# X.xineOpen("file")
# X.xinePlay(0,0)
import time
cdef class AudioEngine:
	cdef object MrlQueue
	cdef object LibXine
	def __init__(self):
		self.MrlQueue = []
	def Initialize(self):
		self.LibXine = libxine()
		self.LibXine.xineNew()
		self.LibXine.xineInit()
		self.LibXine.xineOpenAudioDriver("auto")
		self.LibXine.xineStreamNew()
	def DeInitialize(self):
		self.LibXine.xineStop()
		self.LibXine.xineClose()
		self.LibXine.xineDispose()
		self.LibXine.xineCloseAudioDriver()
		self.LibXine.xineExit()
	def Open(self,File):
		self.LibXine.xineOpen(File)
	def Play(self):
		self.LibXine.xinePlay(0,0)
	def Stop(self):
		self.LibXine.xineStop()
	def PlayStatus(self):
		return self.LibXine.xineGetStatus()
	def PollStatus(self):
		waitTime = 0.02
		while self.PlayStatus() == 'XINE_STATUS_PLAY':
			time.sleep(waitTime)
		return True
	def GetMeta(self,xineMetaCode):
		return self.LibXine.xineGetMetaInfo(xineMetaCode)
	def GetAllMeta(self):
		Counter = 0
		while Counter <= 12:
			print self.LibXine.xineGetMetaInfo(Counter)
			Counter = Counter + 1
	def GetStreamInfo(self,xineStreamCode):
		return self.LibXine.xineGetStreamInfo(xineStreamCode)
	def GetAllStreamInfo(self):
		Counter = 0
		while Counter <= 35:
			print self.LibXine.xineGetStreamInfo(Counter)
			Counter = Counter + 1
cdef class libxine:

	cdef xine_t *xinePtr
	cdef xine_audio_port_t *xineAudioPort
	cdef xine_video_port_t *xineVideoPort
	cdef xine_event_queue_t *xineEventQueue
	cdef ConstCharConstPtr *xinePostPlugins
	cdef xine_stream_t *xineStream
	
	def xineGetError(self):
		Error = xine_get_error(self.xineStream)
		if Error == 1:
			raise Exception('NoInputPlugin')
		if Error == 2:
			raise Exception('NoDemuxPlugin')
		if Error == 3:
			raise Exception('DemuxFailed')
		if Error == 4:
			raise Exception('MalformedMRL')
		if Error == 5:
			raise Exception('InputFailed')
	
	# DONE: Tested
	# DONE: Unit test
	def xineGetVersionString(self):
		return xine_get_version_string()

	# Returns void
	cdef xineGetVersion(self,int *Major,int *Minor,int *Sub):
		xine_get_version(Major,Minor,Sub)

	# DONE: Tested
	# DONE: Unit test
	def xineCheckVersion(self,Major,Minor,Sub):
		Version = xine_check_version(Major,Minor,Sub)
		if Version:
			return True
		else:
			return False

	# Returns xine_stream_t
	# DONE: Tested
	# DONE: Unit test
	def xineNew(self):
		self.xinePtr = xine_new()
	def dbg_xineNew(self):
		if self.xinePtr == NULL:
			return False
		else:
			return True
	
	# Returns void
	def xineInit(self):
		xine_init(self.xinePtr)

	# Returns void
	def xineExit(self):
		xine_exit(self.xinePtr)

	# DONE: Tested
	# DONE: Unit tested
	def xineOpenAudioDriver(self,char *Id):
		#print Id
		cdef ConstCharPtr *Cast 
		Cast = <ConstCharPtr *> Id
		self.xineAudioPort = xine_open_audio_driver(self.xinePtr,Cast,NULL)
	def dbg_xineOpenAudioDriver(self):
		if self.xineAudioPort == NULL:
			return False
		else:
			return True
	
	cdef public xineOpenVideoDriver(self,ConstCharPtr *Id,int Visual,void *Data):
		self.xineVideoPort = xine_open_video_driver(self.xinePtr,Id,Visual,Data)
	def xineCloseAudioDriver(self):
		xine_close_audio_driver(self.xinePtr,self.xineAudioPort)
	cdef public xineCloseVideoDriver(self,xine_video_port_t *Driver):
		xine_close_video_driver(self.xinePtr,Driver)

	# DONE: Tested
	# DONE: Unit tested
	def xineStreamNew(self):
		self.xineStream = xine_stream_new(self.xinePtr,self.xineAudioPort,NULL)
	def dbg_xineStreamNew(self):
		if self.xineStream == NULL:
			return False
		else:
			return True

	# DONE: Tested
	# DONE: Unit tested
	# 
	# look for input / demux / decoder plugins, find out about the format
	# see if it is supported, set up internal buffers and threads
	# returns 1 if OK, 0 on error (use xine_get_error for details)
	def xineOpen(self,char *Mrl):
		Open = xine_open(self.xineStream,<ConstCharPtr *>Mrl)
		if Open == 1:
			return True
		elif Open == 0:
			self.xineGetError()
			return False

	# DONE: Tested
	# DONE: Unit tested
	def xinePlay(self,int StartPosition, int StartTime):
		Play = xine_play(self.xineStream,StartPosition,StartTime)
		if Play:
			return True
		else:
			self.xineGetError()


	# Stop stream playback
	# xine_stream_t stays valid for new xine_open or xine_play
	def xineStop(self):
		xine_stop(self.xineStream)
	# Stop stream playback, free all stream-related resources
	# xine_stream_t stays valid for new xine_open or xine_play
	def xineClose(self):
		xine_close(self.xineStream)
	# Ask current/recent input plugin to eject media - may or may not work,
	# depending on input plugin capabilities
	def xineEject(self):
		return xine_eject(self.xineStream)
	# stop playback, dispose all stream-related resources
	# xine_stream_t no longer valid when after this
	def xineDispose(self):
		xine_dispose(self.xineStream)
		
	#define XINE_PARAM_SPEED                   1 /* see below                   */
	#define XINE_PARAM_AV_OFFSET               2 /* unit: 1/90000 sec           */
	#define XINE_PARAM_AUDIO_CHANNEL_LOGICAL   3 /* -1 => auto, -2 => off       */
	#define XINE_PARAM_SPU_CHANNEL             4
	#define XINE_PARAM_VIDEO_CHANNEL           5
	#define XINE_PARAM_AUDIO_VOLUME            6 /* 0..100                      */
	#define XINE_PARAM_AUDIO_MUTE              7 /* 1=>mute, 0=>unmute          */
	#define XINE_PARAM_AUDIO_COMPR_LEVEL       8 /* <100=>off, % compress otherw*/
	#define XINE_PARAM_AUDIO_AMP_LEVEL         9 /* 0..200, 100=>100% (default) */
	#define XINE_PARAM_AUDIO_REPORT_LEVEL     10 /* 1=>send events, 0=> dont   */
	#define XINE_PARAM_VERBOSITY              11 /* control console output      */
	#define XINE_PARAM_SPU_OFFSET             12 /* unit: 1/90000 sec           */
	#define XINE_PARAM_IGNORE_VIDEO           13 /* disable video decoding      */
	#define XINE_PARAM_IGNORE_AUDIO           14 /* disable audio decoding      */
	#define XINE_PARAM_IGNORE_SPU             15 /* disable spu decoding        */
	#define XINE_PARAM_BROADCASTER_PORT       16 /* 0: disable, x: server port  */
	#define XINE_PARAM_METRONOM_PREBUFFER     17 /* unit: 1/90000 sec           */
	#define XINE_PARAM_EQ_30HZ                18 /* equalizer gains -100..100   */
	#define XINE_PARAM_EQ_60HZ                19 /* equalizer gains -100..100   */
	#define XINE_PARAM_EQ_125HZ               20 /* equalizer gains -100..100   */
	#define XINE_PARAM_EQ_250HZ               21 /* equalizer gains -100..100   */
	#define XINE_PARAM_EQ_500HZ               22 /* equalizer gains -100..100   */
	#define XINE_PARAM_EQ_1000HZ              23 /* equalizer gains -100..100   */
	#define XINE_PARAM_EQ_2000HZ              24 /* equalizer gains -100..100   */
	#define XINE_PARAM_EQ_4000HZ              25 /* equalizer gains -100..100   */
	#define XINE_PARAM_EQ_8000HZ              26 /* equalizer gains -100..100   */
	#define XINE_PARAM_EQ_16000HZ             27 /* equalizer gains -100..100   */
	#define XINE_PARAM_AUDIO_CLOSE_DEVICE     28 /* force closing audio device  */
	#define XINE_PARAM_AUDIO_AMP_MUTE         29 /* 1=>mute, 0=>unmute */
	#define XINE_PARAM_FINE_SPEED             30 /* 1.000.000 => normal speed   */ 
	#define XINE_PARAM_EARLY_FINISHED_EVENT   31 /* send event when demux finish*/
	#define XINE_PARAM_GAPLESS_SWITCH         32 /* next stream only gapless swi*/
	#define XINE_PARAM_DELAY_FINISHED_EVENT   33 /* 1/10sec,0=>disable,-1=>forev*/	
	def xineEngineSetParam(self,int Parameter,int Value):
		xine_engine_set_param(self.xinePtr,Parameter,Value)
	def xineEngineGetParam(self,int Parameter):
		return xine_engine_get_param(self.xinePtr,Parameter)
	def xineGetStatus(self):
		Status = xine_get_status(self.xineStream)
		if Status == 0:
			return "XINE_STATUS_IDLE"
		if Status == 1:
			return "XINE_STATUS_STOP"
		if Status == 2:
			return "XINE_STATUS_PLAY"
		if Status == 3:
			return "XINE_STATUS_QUIT"

	# Depending of the nature and system layer of the stream,
	# some or all of this information may be unavailable or incorrect
	# (e.g. live network streams may not have a valid length)
	# returns 1 on success, 0 on failure (data was not updated,
	# probably because its not known yet... try again later)
	# PosStream - 0...65535
	# PosTime - milliseconds
	# LengthTime - milliseconds
	# def xineGetPosLength(self,int *PosStream,int *PosTime,int *LengthTime):
	#	Len = xine_get_pos_length(self.xineStream,PosStream,PosTime,LengthTime)
	#	if Len:
	#		return True
	#	else:
	#		return False

	def xineGetStreamInfo(self,int Info):
		StreamInfo = {
			0 : "XINE_STREAM_INFO_BITRATE",
			1 : "XINE_STREAM_INFO_SEEKABLE",
			2 : "XINE_STREAM_INFO_VIDEO_WIDTH",
			3 : "XINE_STREAM_INFO_VIDEO_HEIGHT",
			4 : "XINE_STREAM_INFO_VIDEO_RATIO",
			5 : "XINE_STREAM_INFO_VIDEO_CHANNELS",
			6 : "XINE_STREAM_INFO_VIDEO_STREAMS",
			7 : "XINE_STREAM_INFO_VIDEO_BITRATE",
			8 : "XINE_STREAM_INFO_VIDEO_FOURCC",
			9 : "XINE_STREAM_INFO_VIDEO_HANDLED",
			10: "XINE_STREAM_INFO_FRAME_DURATION",
			11: "XINE_STREAM_INFO_AUDIO_CHANNELS",
			12: "XINE_STREAM_INFO_AUDIO_BITS",
			13: "XINE_STREAM_INFO_AUDIO_SAMPLERATE",
			14: "XINE_STREAM_INFO_AUDIO_BITRATE",
			15: "XINE_STREAM_INFO_AUDIO_FOURCC",
			16: "XINE_STREAM_INFO_AUDIO_HANDLED",
			17: "XINE_STREAM_INFO_HAS_CHAPTERS",
			18: "XINE_STREAM_INFO_HAS_VIDEO",
			19: "XINE_STREAM_INFO_HAS_AUDIO",
			20: "XINE_STREAM_INFO_IGNORE_VIDEO",
			21: "XINE_STREAM_INFO_IGNORE_AUDIO",
			22: "XINE_STREAM_INFO_IGNORE_SPU",
			23: "XINE_STREAM_INFO_VIDEO_HAS_STILL",
			24: "XINE_STREAM_INFO_MAX_AUDIO_CHANNEL",
			25: "XINE_STREAM_INFO_MAX_SPU_CHANNEL",
			26: "XINE_STREAM_INFO_AUDIO_MODE",
			27: "XINE_STREAM_INFO_SKIPPED_FRAMES",
			28: "XINE_STREAM_INFO_DISCARDED_FRAMES",
			29: "XINE_STREAM_INFO_VIDEO_AFD",
			30: "XINE_STREAM_INFO_DVD_TITLE_NUMBER",
			31: "XINE_STREAM_INFO_DVD_TITLE_COUNT",
			32: "XINE_STREAM_INFO_DVD_CHAPTER_NUMBER",
			33: "XINE_STREAM_INFO_DVD_CHAPTER_COUNT",
			34: "XINE_STREAM_INFO_DVD_ANGLE_NUMBER",
			35: "XINE_STREAM_INFO_DVD_ANGLE_COUNT"
		 }
		In = xine_get_stream_info(self.xineStream,Info)
		return In


	def xineGetMetaInfo(self,int Info):
		MetaTable = {
			0: "Title",
			1: "Comment",
			2: "Artist",
			3: "Genre",
			4: "Album",
			5: "Year"
		}
		
		cdef char *GetMeta
		GetMeta = <char *>xine_get_meta_info(self.xineStream,Info)
		if GetMeta == NULL:
			raise Exception('MetaFail')
		return MetaTable[Info],GetMeta

	cdef extern xineGetLoadSectionCount(self):
		return xine_get_log_section_count(self.xinePtr)
	cdef extern xineEventNewQueue(self, xine_stream_t *Stream):
		self.xineEventQueue = xine_event_new_queue(Stream)
	cdef extern xineConfigLoad(self,ConstCharPtr *Filename):
		xine_config_load(self.xinePtr,Filename)
