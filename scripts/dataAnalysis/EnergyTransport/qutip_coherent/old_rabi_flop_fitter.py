"""
Fitter for Carrier and Sideband Rabi Flopping to extract Temperature.####
"""
import numpy as np
from scipy.special.orthogonal import eval_genlaguerre as laguer
from scipy import optimize
from matplotlib import pyplot
import labrad
from labrad import types as T, units as U

#optimization
class Parameter:
    def __init__(self, value):
            self.value = value

    def set(self, value):
            self.value = value

    def __call__(self):
            return self.value
def fit(function, parameters, y, x = None):
    def f(params):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return y - function(x)

    if x is None: x = np.arange(y.shape[0])
    p = [param() for param in parameters]
    return optimize.leastsq(f, p)

#class for computing rabi flop time evolution
class rabi_flop():
    def __init__(self, trap_frequency, projection_angle, sideband_order, nmax = 5000, ionnumber = 1, amumass = 40, wavelength = T.Value(729, 'nm')):
        self.ionnumber = ionnumber
        self.trap_frequency = trap_frequency['Hz']
        self.wavelength = wavelength['m']
        self.mass = amumass * U.amu['kg']
        self.projection_angle = projection_angle
        self.sideband_order = sideband_order #0 for carrier, 1 for 1st sideband etc
        self.n = np.arange(0, nmax +1) #how many vibrational states to consider
        self.eta = self.lamb_dicke() / np.sqrt(ionnumber)
        self.rabi_coupling = self.rabi_coupling()
        print self.eta
        
    def rabi_coupling(self):
        order = self.sideband_order
        eta = self.eta
        n = self.n
        print 'eta', eta
        print order
        #lists of the generalized laguere polynomails of the corresponding order evaluated at eta**2
        L = np.array([laguer(i, order, eta**2) for i in n])
        print L
        if self.sideband_order == 0:
            omega = L * np.exp(-1./2*eta**2)
        elif self.sideband_order == 1:
            omega = L* np.exp(-1./2*eta**2)*eta**(1)*(1/(n+1.))**0.5
        elif self.sideband_order == 2:
            omega = L* np.exp(-1./2*eta**2)*eta**(2)*(1/((n+1.)*(n+2)))**0.5 
        elif self.sideband_order == 3:
            omega = L* np.exp(-1./2*eta**2)*eta**(3)*(1/((n+1.)*(n+2)*(n+3)))**0.5 
        elif self.sideband_order == 4:
            omega = np.exp(-1./2*eta**2)*eta**(4)*(1/((n+1.)*(n+2)*(n+3)*(n+4)))**0.5
        else:
            raise NotImplementedError("Can't do that high of sideband order")
        omega = np.abs(omega)
        return omega
        
    def lamb_dicke(self):
        '''computes the lamb dicke parameter
        @var theta: laser projection angle in degrees
        @var wavelength: laser wavelength in meters
        @var frequency: trap frequency in Hz
        '''
        theta = self.projection_angle
        mass = self.mass
        wavelength = self.wavelength
        frequency = self.trap_frequency
#         hbar = U.hbar['J*s']
        k = 2.*np.pi/wavelength
        eta = k*np.sqrt(U.hbar/(2*mass*2*np.pi*frequency))*np.abs(np.sin(theta*2.*np.pi / 360.0))
        return eta
        
    def compute_state_evolution(self, nbar, delta, T_Rabi, t):
        '''returns the state evolution for temperature nbar, detuning delta, rabi frequency T_Rabi for times t'''
        n = self.n
        if 5 * nbar > self.n.max():
            print 'WARNING, trying to calculate nbar that is high compared to the precomputed energy levels' 
        omega = self.rabi_coupling
        #level population probability for a given nbar, see Leibfried 2003 (57)
        ones = np.ones_like(t)
        p = ((float(nbar)/(nbar+1.))**n)/(nbar+1.) 
        result = np.outer(p*omega/np.sqrt(omega**2+delta**2), ones) * (np.sin( np.outer( np.sqrt(omega**2+delta**2)*np.pi/T_Rabi, t ))**2)
        result = np.sum(result, axis = 0)
        return result

cxn = labrad.connect('192.168.169.197')
dv = cxn.data_vault

pump_eff = 1.0
offset_time = 0
#heating times in mus
info = ('Carrier', 0, 0.0, ('2013Aug26','1331_55'), {})
nbar = Parameter(3); delta = 0; T_Rabi = Parameter(20.0);

trap_frequency = T.Value(3.0, 'MHz') #Hz
projection_angle = 45 #degrees
sideband_order = 0
flop = rabi_flop(trap_frequency = trap_frequency, projection_angle = projection_angle, sideband_order = sideband_order)

def f(x): 
    evolution = flop.compute_state_evolution( nbar(), delta, T_Rabi(), x  )
    return evolution


#plots the data for all waiting times while averaging the probabilities
fig = pyplot.figure()
title,order, wait_time,dataset,kwargs = info 
date,datasetName = dataset
dv.cd( ['','Experiments','RabiFlopping',date,datasetName] )
dv.open(1)  
times,prob = dv.get().asarray.transpose()
tmin,tmax = times.min(), times.max()
detailed_times = np.linspace(tmin, tmax, 1000) 
evolution = flop.compute_state_evolution( nbar(), delta, T_Rabi(), detailed_times - offset_time )
pyplot.plot(detailed_times , evolution,  '--k', label = 'guess')

fitting_region = np.where(times <= 30)

p,success = fit(f, [nbar, T_Rabi], y = prob[fitting_region], x = times[fitting_region] - offset_time)
print 'fit for nbar is', nbar()
print 'fit to T rabi is ', T_Rabi()
evolution = flop.compute_state_evolution( nbar(), delta, T_Rabi(), detailed_times - offset_time )
pyplot.plot(detailed_times , evolution,  'b', label = 'fit')

pyplot.plot(times, prob, '--o', label = 'heating {} ms'.format(wait_time))

pyplot.hold(True)
pyplot.legend()
pyplot.title(title)
pyplot.xlabel('time (us)')
pyplot.ylabel('D state occupation probability')
pyplot.text(max(times)*0.70,0.68, 'detuning = {0}'.format(delta))
pyplot.text(max(times)*0.70,0.73, 'nbar = {:.0f}'.format(nbar()))
pyplot.text(max(times)*0.70,0.78, 'Rabi Time = {:.1f} us'.format(10**6 * T_Rabi()))
pyplot.ylim([0,1])
pyplot.legend()
pyplot.show()