import libpry
class TestXine(libpry.AutoTree):
    def setUpAll(self):
        import sys
        import os

        sys.path.append(os.getcwd() + '/src/cython/')
        
        import xine
        self.Xine = xine.libxine()
        self.Xine_Version = '1.1.16.3'
        #self.Xine.xInitThreads()
    def tearDownAll(self):
        self.Xine.xineCloseAudioDriver()
        #self.Xine.xineClose()
        #self.Xine.xineDispose()
        if self.Xine.dbg_xineNew():
            self.Xine.xineExit()

    def test_1_xineGetVersionString(self):
        assert self.Xine.xineGetVersionString() == self.Xine_Version
    def test_2_xineCheckVersion(self):
        Major,Minor,Sub,SubSub = self.Xine_Version.split('.')
        assert self.Xine.xineCheckVersion(int(Major),int(Minor),int(Sub)) == True
    def test_3_FAIL_xineCheckVersion(self):
        assert self.Xine.xineCheckVersion(9,9,9) == False
    def test_4_FAIL_dbg_xineNew(self):
        assert self.Xine.dbg_xineNew() == False
    def test_5_dbg_xineNew(self):
        self.Xine.xineNew()
        assert self.Xine.dbg_xineNew() == True
    def test_6_FAIL_dbg_xineOpenAudioDriver(self):
        assert self.Xine.dbg_xineOpenAudioDriver() == False
    def test_7_z_auto_dbg_xineOpenAudioDriver(self):
        self.Xine.xineInit()
        self.Xine.xineOpenAudioDriver("auto")
        assert self.Xine.dbg_xineOpenAudioDriver() == True
    def test_8_FAIL_dbg_xineStreamNew(self):
        assert self.Xine.dbg_xineStreamNew() == False
    def test_9_dbg_xineStreamNew(self):
        self.Xine.xineStreamNew()
        assert self.Xine.dbg_xineStreamNew() == True
    #def test_a10_FAIL_xineOpen(self):
    #    try:
    #        self.Xine.xineOpen("")
    #    except Exception,E:
    #        assert E == Exception('InputFailed')
    #        
    #def test_a11_FAIL_xinePlay(self):
    #    try:
    #        self.Xine.xinePlay(0,0)
    #    except Exception,E:
    #        assert E == Exception('NoDemuxPlugin')
        
    
    
tests = [
    TestXine()
]
