from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor
from twisted.internet.defer import returnValue

TIMEOUT = 1.0

class HPServer( SerialDeviceServer ):
    """Controls HP8648A Signal Generator"""

    name = '%LABRADNODE% HP Server'
    regKey = 'HPsiggen'
    port = None
    serNode = 'lattice-pc'
    timeout = TIMEOUT
    gpibaddr = 0
    
    @inlineCallbacks
    def initServer( self ):
        self.createDict()
        if not self.regKey or not self.serNode: raise SerialDeviceError( 'Must define regKey and serNode attributes' )
        port = yield self.getPortFromReg( self.regKey )
        self.port = port
        try:
            serStr = yield self.findSerial( self.serNode )
            self.initSerial( serStr, port )
        except SerialConnectionError, e:
            self.ser = None
            if e.code == 0:
                print 'Could not find serial server for node: %s' % self.serNode
                print 'Please start correct serial server'
            elif e.code == 1:
                print 'Error opening serial connection'
                print 'Check set up and restart serial server'
            else: raise
        
        self.ser.write(self.SetAddrStr(self.gpibaddr)) #set gpib address
        self.SetControllerWait(0) #turns off automatic listen after talk, necessary to stop line unterminated errors
        yield self.populateDict()
        print self.hpDict
        
    def createDict(self):
        d = {}
        d['state'] = None
        d['power'] = None
        d['freq'] = None
        d['powerrange'] = (-5.9,5.0)
        self.hpDict = d
    
    @inlineCallbacks
    def populateDict(self):
        state = yield self.GetState(-1) #using fake context of -1
        freq = yield self.GetFreq(-1)
        power = yield self.GetPower(-1)
        self.hpDict['state'] = float(state) 
        self.hpDict['power'] = float(power)
        self.hpDict['freq'] = float(freq)/10**6 #state in MhZ
    
    @setting(1, "Identify", returns='s')
    def Identify(self, c):
	'''Ask instrument to identify itself'''
        command = self.IdenStr()
    	self.ser.write(command)
    	self.ForceRead() #expect a reply from instrument
    	answer = yield self.ser.readline()
    	returnValue(answer[:-1])

    @setting(2, "GetFreq", returns='v')
    def GetFreq(self,c):
    	'''Returns current frequency'''
        if self.hpDict['freq'] is not None:
            answer = self.hpDict['freq']
        else:
        	command = self.FreqReqStr()
        	self.ser.write(command)
        	self.ForceRead() #expect a reply from instrument
        	answer = yield self.ser.readline()
    	returnValue(answer)

    @setting(3, "SetFreq", freq = 'v', returns = "")
    def SetFreq(self,c,freq):
    	'''Sets frequency, enter value in MHZ'''
    	command = self.FreqSetStr(freq)
    	self.ser.write(command)
        self.hpDict['freq'] = freq
      
    @setting(4, "GetState", returns='w')
    def GetState(self,c):
        '''Request current on/off state of instrument'''
    	if self.hpDict['state'] is not None:
            answer = int(self.hpDict['state'])
        else:
            command = self.StateReqStr()
            self.ser.write(command)
            self.ForceRead() #expect a reply from instrument
            answer = yield self.ser.readline()
            answer = int(answer)
    	returnValue(answer)
    
    @setting(5, "SetState", state= 'w', returns = "")
    def SetState(self,c, state):
    	'''Sets on/off (enter 1/0)'''
    	command = self.StateSetStr(state)
    	self.ser.write(command)
        self.hpDict['state'] = state
    
    @setting(6, "GetPower", returns = 'v')
    def GetPower(self,c):
    	''' Returns current power level in dBm'''
        if self.hpDict['power'] is not None:
            answer = self.hpDict['power']
        else:
        	command = self.PowerReqStr()
        	self.ser.write(command)
        	self.ForceRead() #expect a reply from instrument
        	answer = yield self.ser.readline()
    	returnValue(answer)
    
    @setting(7, "SetPower", level = 'v',returns = "")
    def SetPower(self,c, level):
    	'''Sets power level, enter power in dBm'''
        self.checkPower(level)
    	command = self.PowerSetStr(level)
    	self.ser.write(command)
        self.hpDict['power'] = level
    
    @setting(8, "Get Power Range", returns = "*v:")
    def GetPowerRange(self,c):
        return self.hpDict['powerrange']
    
    def checkPower(self, level):
        MIN,MAX = self.hpDict['powerrange']
        if not MIN <= level <= MAX:
            raise('Power Our of Range')
        
    #send message to controller to indicate whether or not (status = 1 or 0)
    #a response is expected from the instrument
    def SetControllerWait(self,status):
	command = self.WaitRespStr(status) #expect response from instrument
	self.ser.write(command)

    def ForceRead(self):
        command = self.ForceReadStr()
        self.ser.write(command)
  
    def IdenStr(self):
	return '*IDN?'+'\n'
	
    # string to request current frequency
    def FreqReqStr(self):
	return 'FREQ:CW?' + '\n'
	
    # string to set freq (in MHZ)
    def FreqSetStr(self,freq):
	return 'FREQ:CW '+ str(freq) +'MHZ'+'\n'
	  
    # string to request on/off?
    def StateReqStr(self):
	return 'OUTP:STAT?' + '\n'

    # string to set on/off (state is given by 0 or 1)
    def StateSetStr(self, state):
	if state == 1:
	    comstr = 'OUTP:STAT ON' + '\n'
	else:
	    comstr = 'OUTP:STAT OFF' + '\n'
	return comstr

    # string to request current power
    def PowerReqStr(self):
	return 'POW:AMPL?' + '\n'

    # string to set power (in dBm)
    def PowerSetStr(self,pwr):
	return 'POW:AMPL ' +str(pwr) + 'DBM' + '\n'

    # string to force read
    def ForceReadStr(self):
        return '++read eoi' + '\n'
	
    # string for prologix to request a response from instrument, wait can be 0 for listen / for talk
    def WaitRespStr(self, wait):
	return '++auto '+ str(wait) + '\n'
	  
    # string to set the addressing of the prologix
    def SetAddrStr(self, addr):
	return '++addr ' + str(addr) + '\n'

if __name__ == "__main__":
    from labrad import util
    util.runServer(HPServer())
