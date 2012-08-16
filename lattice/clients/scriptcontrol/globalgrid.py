from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks

class GlobalGrid(QtGui.QTableWidget):
    def __init__(self, parent, experimentPath):
        QtGui.QTableWidget.__init__(self)
        self.parent = parent
        self.experimentPath = experimentPath
        self.setupGlobalGrid()
        self.setupGlobalParameterListener()

    @inlineCallbacks
    def setupGlobalGrid(self):
#        self.globalGrid = QtGui.QGridLayout()
#        self.globalGrid.setSpacing(5)
        
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setColumnCount(2)

        self.checkBoxParameterDict = {}
        self.parameterCheckBoxDict = {}
                
        self.doubleSpinBoxParameterDict = {}
        self.parameterDoubleSpinBoxDict = {}
        
        self.globalParameterDict = {}
        
        self.lineEditParameterDict = {}
        self.parameterLineEditDict = {}                  
        
        
        numParams = 0
        path = self.experimentPath
        for i in range(len(self.experimentPath)):
            path = path[:-1]
            paramNames = yield self.parent.server.get_parameter_names(path)
            numParams += len(paramNames)
            for paramName in paramNames:
                self.globalParameterDict[paramName] = path + [paramName]
        
        self.setRowCount(numParams)
        
#            gridRow = 0
#            gridCol = 0

        Row = 0
        for parameter in self.globalParameterDict.keys():
            item = QtGui.QTableWidgetItem(parameter)
            self.setItem(Row, 1, item)
            # create a label and spin box, add it to the grid
            value = yield self.parent.server.get_parameter(self.globalParameterDict[parameter])
            widget = self.parent.typeCheckerWidget(value)
            widgetType = type(widget)
            if (widgetType == QtGui.QCheckBox):
                self.checkBoxParameterDict[widget] = parameter
                self.parameterCheckBoxDict[parameter] = widget
                widget.stateChanged.connect(self.updateCheckBoxStateToSemaphore)   
                self.setCellWidget(Row, 0, widget)        
            elif (widgetType == QtGui.QDoubleSpinBox):
                self.doubleSpinBoxParameterDict[widget] = parameter
                self.parameterDoubleSpinBoxDict[parameter] = widget 
                widget.valueChanged.connect(self.updateSpinBoxValueToSemaphore)
#                self.connect(widget, QtCore.SIGNAL('valueChanged(double)'), self.updateSpinBoxValueToSemaphore)
                self.setCellWidget(Row, 0, widget)
            elif(widgetType == QtGui.QLineEdit):
                self.lineEditParameterDict[widget] = parameter
                self.parameterLineEditDict[parameter] = widget
                widget.editingFinished.connect(self.updateLineEditValueToSemaphore)                  
#                self.connect(widget, QtCore.SIGNAL('editingFinished()'), self.updateLineEditValueToSemaphore)
                self.setCellWidget(Row, 0, widget)            
#            if (type(widget) == QtGui.QDoubleSpinBox):
#                self.doubleSpinBoxParameterDict[widget] = parameter
#                self.parameterDoubleSpinBoxDict[parameter] = widget 
#                
#                self.connect(widget, QtCore.SIGNAL('valueChanged(double)'), self.updateSpinBoxValueToSemaphore)
#                self.setCellWidget(Row, 0, widget)
#            elif(type(widget) == QtGui.QLineEdit):
#                self.lineEditParameterDict[widget] = parameter
#                self.parameterLineEditDict[parameter] = widget                  
#                
#                self.connect(widget, QtCore.SIGNAL('editingFinished()'), self.updateLineEditValueToSemaphore)
#
#                self.setCellWidget(Row, 0, widget)


#            try:
#                if (len(value) == 3):
#                    doubleSpinBox = QtGui.QDoubleSpinBox()
#                    doubleSpinBox.setRange(value[0], value[1])
#                    doubleSpinBox.setValue(value[2])
#                    doubleSpinBox.setSingleStep(.1)
#                    doubleSpinBox.setKeyboardTracking(False)
#                    self.connect(doubleSpinBox, QtCore.SIGNAL('valueChanged(double)'), self.updateValueToSemaphore)
#                    
#                    self.doubleSpinBoxParameterDict[doubleSpinBox] = parameter
#                    self.parameterDoubleSpinBoxDict[parameter] = doubleSpinBox
#                    
#                    self.setCellWidget(Row, 0, doubleSpinBox)
#                else:
#                    raise
#            
##            self.globalGrid.addWidget(label, gridRow, gridCol, QtCore.Qt.AlignCenter)
##            self.globalGrid.addWidget(doubleSpinBox, gridRow, gridCol + 1, QtCore.Qt.AlignCenter)
#
#            except:
#                lineEdit = QtGui.QLineEdit(readOnly=True)
#                #value = value[2:]
#                try:
#                    for i in range(len(value)):
#                        value[i] = value[i].value
#                except:
#                    pass # boolean!
#                lineEdit.setText(str(value))
#                        
#                self.lineEditParameterDict[lineEdit] = parameter
#                self.parameterLineEditDict[parameter] = lineEdit                  
#                
#                self.connect(lineEdit, QtCore.SIGNAL('editingFinished()'), self.updateLineEditValueToSemaphore)
#
#                self.setCellWidget(Row, 0, lineEdit)


            
            Row += 1
            
#            gridCol += 2
#            if (gridCol == 6):
#                gridCol = 0
#                gridRow += 1
        
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
#        self.setLayout(self.globalGrid)    


    @inlineCallbacks
    def setupGlobalParameterListener(self):
        context = self.parent.cxn.context()
        yield self.parent.cxn.semaphore.signal__parameter_change(33333, context = context)
        yield self.parent.cxn.semaphore.addListener(listener = self.updateGlobalParameter, source = None, ID = 33333, context = context)    

    def updateGlobalParameter(self, x, y):
        # need type checking here!
        if (y[0][-1] in self.parameterDoubleSpinBoxDict.keys()):
            if (len(y[1]) == 3):
                self.parameterDoubleSpinBoxDict[y[0][-1]].setValue(y[1][2])        
#        self.parameterDoubleSpinBoxDict[y[0]].setValue(y[1])

    @inlineCallbacks
    def updateCheckBoxStateToSemaphore(self, evt):
        yield self.parent.server.set_parameter(self.globalParameterDict[self.checkBoxParameterDict[self.sender()]], bool(evt))
    
    @inlineCallbacks
    def updateSpinBoxValueToSemaphore(self, parameterValue):
        yield self.parent.server.set_parameter(self.globalParameterDict[self.doubleSpinBoxParameterDict[self.sender()]], [self.sender().minimum(), self.sender().maximum(), parameterValue])

    @inlineCallbacks
    def updateLineEditValueToSemaphore(self):
        from labrad import types as T
        # two types....tuples [(value, unit)] or tuples of strings and values [(string, (value, unit))]
        value = eval(str(self.sender().text()))
        typeSecondElement = type(value[0][1])
        # normal list of labrad values
        if (typeSecondElement == str):
            # build a list of labrad values
            for i in range(len(value)):
                value[i] = T.Value(value[i][0], value[i][1])
        elif (typeSecondElement == tuple):
            for i in range(len(value)):
                value[i] = (value[i][0], T.Value(value[i][1][0], value[i][1][1]))
        yield self.parent.server.set_parameter(self.globalParameterDict[self.lineEditParameterDict[self.sender()]], value)
