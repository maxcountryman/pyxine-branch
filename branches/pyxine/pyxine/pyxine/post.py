# $Id$
#
# Copyright (C) 2003  Geoffrey T. Dairiki <dairiki@dairiki.org>
#
# This file is part of Pyxine, Python bindings for xine.
#
# Pyxine is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# Pyxine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from pyxine import libxine, constants, constwrap, cstruct, xine
from pyxine import Error

def _tuplize(val):
    """Convert val to tuple.

    If 'val' is a sequence, just convert to tuple.
    If 'val' is None, return a 0-tuple.
    Otherwise return a 1-tuple containing 'val'.
    """
    try:
        return tuple(val)
    except TypeError:
        if val is None:
            return ()
        return (val,)
        

class _readonly_dict_base(object):
    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default
    def has_key(self, name):
        return self.get(name) is not None

    def values(self):
        return map(self.__getitem__, self.keys())
    def items(self):
        return map(lambda name: (name, self[name]), self.keys())

    def iterkeys(self):		return iter(self.keys())
    def itervalues(self):	return iter(self.values())
    def iteritems(self):	return iter(self.items())
    def __len__(self):		return len(self.keys())
    __iter__ = iterkeys

class _Post_inputs(_readonly_dict_base):
    def __init__(self, post):
        self.post = post

    def keys(self):
        return libxine.xine_post_list_inputs(self.post.this)
    
    def __getitem__(self, name):
        post = self.post
        try:
            input = libxine.xine_post_input(post.this, name)
        except Error:
            raise KeyError, "no input named '%s'" % name
        return PostInput(post, input)

class _Post_outputs(_readonly_dict_base):
    def __init__(self, post):
        self.post = post

    def keys(self):
        return libxine.xine_post_list_outputs(self.post.this)
    
    def __getitem__(self, name):
        post = self.post
        try:
            output = libxine.xine_post_output(post.this, name)
        except Error:
            raise KeyError, "no output named '%s'" % name
        return PostOutput(post, output)

class Post(object):
    """A xine post-plugin.

    Example Usage:

        To initialize and wire up the goom visualization filter:

    	    >>> goom = Post(stream, 'goom',
                            audio_target=stream.ao, video_target=stream.vo)
            >>> stream.audio_source.wire(goom.inputs['audio in'])

        When finished, to unwire the goom:

            >>> stream.audio_source.wire(stream.ao)
    """
    # Destination of the outputs (if wired)
    _dest = {}
    
    def __init__(self, xine_or_stream, name,
                 inputs=0, audio_target=[], video_target=[]):


        audio_target = _tuplize(audio_target)
        video_target = _tuplize(video_target)

        try:
            self.xine = xine_or_stream.xine # xine_or_stream is stream
        except AttributeError:
            self.xine = xine_or_stream
            
        self.this = libxine.xine_post_init(self.xine.this, name, inputs,
                                           map(lambda s: s.this, audio_target),
                                           map(lambda s: s.this, video_target))
        self.rep = cstruct.xine_post_t(self.this)
        
        def isvideo(port):
            return port.type == constants.XINE_POST_DATA_VIDEO
        def isaudio(port):
            return port.type == constants.XINE_POST_DATA_AUDIO

        outputs = self.outputs.values()
        video_outputs = filter(isvideo, outputs)
        audio_outputs = filter(isaudio, outputs)

        self._dest = {}
        for out, port in ( map(None, video_outputs, video_target) 
                           + map(None, audio_outputs, audio_target) ):
            if out and port:
                self._dest[out.name] = port

                
    def __del__(self):
        if hasattr(self, 'this'):
            libxine.xine_post_dispose(self.xine.this, self.this)
        print "Post deleted"

    type = property(
        lambda s: constwrap.XINE_POST_TYPE(s.rep.type),
        doc="The type of this plugin")

    def __get_audio_input(self):
        return map(lambda ptr: xine.AudioPort(self.xine, ptr),
                   self.rep.audio_input)
    audio_input = property(
        __get_audio_input,
        doc="""A list of the audio input ports provied by this plugin.

        The values in this list are 'AudioPort's.  You can hand these to
        other post plugin's outputs or pass them to the initialization
        of streams.
        """)

    def __get_video_input(self):
        return map(lambda ptr: xine.VideoPort(self.xine, ptr),
                   self.rep.audio_input)
    video_input = property(
        __get_audio_input,
        doc="""A list of the video input ports provied by this plugin.

        The values in this list are 'VideoPort's.  You can hand these to
        other post plugin's outputs or pass them to the initialization
        of streams.
        """)
    

    inputs = property(_Post_inputs,
        doc="""Input ports.

        This is a readonly dict (whose keys are the port names, and whose
        values are 'PostInputs') of the input ports of this Post plugin.
        You use these for rewiring post-plugins.
        """)

    outputs = property(_Post_outputs,
        doc="""Output ports.

        This is a readonly dict (whose keys are the port names, and whose
        values are 'PostOutputs') of the output ports of this Post plugin.
        You use these for rewiring post-plugins.
        """)

class PostInput(cstruct.xine_post_in_t):
    def __init__(self, post, this):
        self.post = post
        cstruct.xine_post_in_t.__init__(self, this)
        self.__super = cstruct.super(PostInput, self)

    type = property(lambda s: constwrap.XINE_POST_DATA(s.__super.type))

class PostOutput(cstruct.xine_post_out_t):
    def __init__(self, post, this):
        self.post = post                # can be stream, too
        cstruct.xine_post_out_t.__init__(self, this)
        self.__super = cstruct.super(PostOutput, self)

    type = property(lambda s: constwrap.XINE_POST_DATA(s.__super.type))

    def wire(self, target):
        if target is None:
            libxine.xine_post_wire(self.this, "NULL")
        elif isinstance(target, PostInput):
            libxine.xine_post_wire(self.this, target.this)
        elif isinstance(target, xine.VideoPort):
            libxine.xine_post_wire_video_port(self.this, target.this)
        elif isinstance(target, xine.AudioPort):
            libxine.xine_post_wire_audio_port(self.this, target.this)
        else:
            raise ValueError, "don't know how to wire to target type"

        self.post._dest[self.name] = target
