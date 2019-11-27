from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtGui
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import pickle


class Multipole_plot(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(Multipole_plot, self).__init__(parent)
        self.reactor = reactor
        self.setupLayout()
        self.connect()
        data_out = pickle.load( open( "MultipoleMatrix.p", "rb" ) )
        self.multipole_expansions = data_out['mat']
        self.name_dic =data_out['name_dic']
        
    
    def setupLayout(self):
        #setup the layout and make all the widgets
        self.setWindowTitle('Connected Layout Widget')
        #create a horizontal layout
        layout = QtGui.QHBoxLayout()
        
        #buttons for submitting
        self.submit = QtGui.QPushButton('Calc ')
        self.textedit = QtGui.QTextEdit()
        self.textedit.setReadOnly(True)
        #add all the button to the layout
        
        layout.addWidget(self.submit)
        layout.addWidget(self.textedit)
        

        #Canvas and Toolbar
        self.figure = plt.figure(figsize=(7.5,5))    
        self.canvas = FigureCanvas(self.figure)     
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    @inlineCallbacks
    def connect(self):
        #make an asynchronous connection to LabRAD
        from labrad.wrappers import connectAsync
        from labrad.errors import Error
        self.Error = Error
        cxn = yield connectAsync()
        self.dac = cxn.dac_server
        self.registry = cxn.registry
        self.submit.pressed.connect(self.on_submit)
    
    @inlineCallbacks
    def on_submit(self):
        '''
        when the submit button is pressed, submit the value to the registry
        '''
        Vdac = yield self.dac.get_analog_voltages()
        Vcalc = np.zeros(len(Vdac))
        self.textedit.setText('')
        for i  in range(len(Vdac)):
            Vcalc[self.name_dic[Vdac[i][0]]]=Vdac[i][1]
            text =Vdac[i][0] +  ':   {:2.3f} Volt'.format(Vdac[i][1]) 
            self.textedit.append(text)
        
        # ploting on the canvas
        plt.cla()

        Multipule_name = ['c', 
                  'Ez', '-Ex', '-Ey', 
                  r'$U2 = z^2-(x^2+y^2)/2$', 'U5 = -6zx', 'U4 = -6yz', r'$U1 = 6(x^2-y^2)$', 'U3= 12xy' ]
        coeffs_solution1 =  np.dot(self.multipole_expansions,Vcalc)
        y_pos =range(len(coeffs_solution1))
        ax = self.figure.add_subplot(111)
        plt.bar(y_pos,coeffs_solution1)
        plt.grid(which ='both')
    #     plt.ylim(-1,1)
        plt.xticks(y_pos, Multipule_name)
        ax.tick_params(axis="x", labelsize=8, labelrotation=-45)
                      
    
        self.canvas.draw()

        
    def closeEvent(self, x):
        #stop the reactor when closing the widget
        self.reactor.stop()

if __name__=="__main__":
    #join Qt and twisted event loops
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = Multipole_plot(reactor)
    widget.show()
    reactor.run()