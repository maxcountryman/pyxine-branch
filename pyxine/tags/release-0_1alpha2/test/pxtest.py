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
    
import sys, os, os.path, inspect, unittest, weakref

the_xine = None
the_stream = None

def srcdir(obj=None):
    f = inspect.getfile(obj or inspect.currentframe())
    return os.path.dirname(os.path.abspath(f))

testdir = srcdir()

try:
    import pyxine
except ImportError:
    sys.path.insert(0, os.path.join(testdir, '../build/lib'))
    import pyxine

if __name__.endswith('pxtest'):
    sys.stderr.write("Using pyxine from %s\n" % srcdir(pyxine))

class TestCase(unittest.TestCase):

    def getXine(self):
        global the_xine
        if not the_xine:
            the_xine = pyxine.Xine({'misc.memcpy_method': 'glibc'})
        return weakref.proxy(the_xine)

    def getStream(self):
        global the_stream
        if not the_stream:
            the_stream = self.getXine().stream_new()
        return weakref.proxy(the_stream)

    def delStream(self):
        global the_stream
        print "Deleting the_stream"
        del the_stream
        the_stream = None

    def delXine(self):
        global the_xine
        self.delStream()
        the_xine = None

    
    def getTestMRL(self):
        return 'file:' + os.path.join(testdir, "wonderful_strange.mp3")

class AllTestLoader(unittest.TestLoader):

    def __init__(self, testLoader=unittest.defaultTestLoader):
        self.testLoader = testLoader
        
    def loadTestsFromModule(self, module):
        suite = unittest.TestSuite()
        dir = self.get_dir(module)
        for mod in self.all_test_modules(dir):
            suite.addTest(self.testLoader.loadTestsFromModule(mod))
        return suite
        
    def loadTestsFromNames(self, names, module):
        suite = unittest.TestSuite()
        dir = self.get_dir(module)
        for mod in self.all_test_modules(dir):
            try:
                suite.addTest(self.testLoader.loadTestsFromNames(names, mod))
            except AttributeError:
                pass
        if suite.countTestCases() == 0:
            raise RuntimeError, "No tests found for %s" % names
        return suite

    def get_dir(self, module):
        try:
            return os.path.dirname(inspect.getfile(module)) or '.'
        except TypeError:
            # Punt...
            return testdir

    def all_test_modules(self, dir):
        test_src = filter(lambda f: f.endswith('_test.py'),
                          os.listdir(dir))
        test_src.sort()

        return map(lambda f: __import__(f[:-3], globals(), locals(), []),
                   test_src)
    

if __name__ == '__main__':
    unittest.main(testLoader = AllTestLoader())
