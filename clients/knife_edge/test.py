from PyQt4 import QtGui
import matplotlib
from matplotlib.figure import Figure
from twisted.internet.defer import inlineCallbacks , returnValue
from twisted.internet.threads import deferToThread
import time


class test(QtGui.QWidget):
    def __init__(self, reactor, cxn = None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        # Initialize
        self.reactor = reactor
        self.cxn = cxn
        self.power = 0
        self.connect_labrad()
        print " done"
        self.getParams()
        print self.power
    
   
     
    @inlineCallbacks
    # Attempt to connect ot the pulser server 
    def connect_labrad(self):
        if self.cxn is None:
            print "connecting"
            from common.clients import connection
            self.cxn = connection.connection()
            yield self.cxn.connect()
        print "connection established"
        self.context = yield self.cxn.context()
        self.powerHead = yield self.cxn.get_server('parametervault')
        
    @inlineCallbacks
    # Attempt to connect ot the pulser server 
    def getParams(self):
        print "inside function"
        self.power =yield self.parametervault.get_all_parameters()

        returnValue( self.power  )
            
    


    def closeEvent(self, x):
        self.reactor.stop()  
    
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from common.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = test(reactor)
    widget.show()
    reactor.run()
