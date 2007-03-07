#!/usr/bin/env python

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

import pyxine
import sys
sys.stdout = sys.stderr

xine = pyxine.Xine(cfg_filename="/tmp/junk-xine.cfg")
s = xine.stream_new()
s.verbosity = 1

print "Config:"
for k in xine.config:
    print "%s: %s" % (k, xine.config[k])

print "Browsable Plugins", xine.get_browsable_input_plugin_ids()
print "Autoplay Plugins", xine.get_autoplay_input_plugin_ids()
print "Post Plugins", xine.list_post_plugins()
print "Audio Output Plugins", xine.list_audio_output_plugins()
print "Video Output Plugins", xine.list_video_output_plugins()

xine.config.save("/tmp/junk-xine.cfg")

