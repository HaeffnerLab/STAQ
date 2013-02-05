from script_status import script_semaphore
#from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import blockingCallFromThread
from twisted.internet import reactor
from numpy import linspace
import labrad
from labrad.units import WithUnit

class scan_info(object):
    '''
    holds informaton about the scan or measurement
    '''
    def __init__(self, scan_name):
        self.scan_name = scan_name
        self.status = script_semaphore()

class scan_method(scan_info):
    
    def __init__(self, scan_name, script_cls):
        super(scan_method, self).__init__(scan_name)
        self.script = script_cls()

    def execute(self, ident):
        '''
        Executes the scan method
        '''
        cxn = labrad.connect()
        context = cxn.context()
        try:
            self.script.initialize(cxn, ident)
            self.status.launch_confirmed()
            self.execute_scan(cxn, context)
            self.script.finalize()
        except Exception as e:
            print e
            self.status.error_finish_confirmed(e)
            cxn.disconnect()
        else:
            self.status.finish_confirmed()
            cxn.disconnect()
            return True
    
    #move this to script status
    def pause_or_stop(self):
        self.status.checking_for_pause()
        blockingCallFromThread(reactor, self.status.pause_lock.acquire)
        self.status.pause_lock.release()
        if self.status.should_stop:
            self.status.stop_confirmed()
            return True
    
    def execute_scan(self, cxn, context):
        '''
        implemented by the subclass
        '''

class single_run(scan_method):
    '''
    Used to perform a single measurement
    '''
    def __init__(self, scan_name, script):
        super(single_run,self).__init__(scan_name, script)
    
    def execute_scan(self, cxn, context):
        self.script.run()

class repeat_measurement(scan_method):
    '''
    Used to repeat a measurement multiple times
    '''
    def __init__(self, scan_name, script, repeatitions):
        self.repeatitions = repeatitions
        scan_name = self.name_format(scan_name)
        super(repeat_measurement,self).__init__(scan_name, script)

    def name_format(self, name):
        return 'Repeat {0} {1} times'.format(name, self.repeatitions)
    
    def execute_scan(self, cxn, context):
        dv = cxn.data_vault
        dv.cd(['','ScriptScanner'], True, context = context)
        for i in range(self.repeatitions):
            if self.pause_or_stop(): return
            self.script.run()
            self.status.set_percentage( (i + 1.0) / self.repeatitions)

class scan_measurement_1D(scan_method):
    '''
    Used to Scan a Parameter of a measurement
    '''
    def __init__(self, scan_name, script, parameter, minim, maxim, steps, units):
        scan_name = self.name_format(scan_name)
        super(scan_measurement_1D,self).__init__(scan_name, script)
        self.parameter = parameter
        self.scan_points = linspace(minim, maxim, steps)
        self.scan_points = [WithUnit(pt, units) for pt in self.scan_points ]
        
    def name_format(self, name):
        return 'Scanning {0} in {1}'.format(self.parameter, name)
    
    def execute_scan(self):
        for i in range(len(self.scan_points)):
            if self.pause_or_stop(): return
            self.script.set_parameter(self.parameter, self.scan_points[i])
            self.script.run()
            self.status.set_percentage( (i + 1.0) / len(self.scan_points))