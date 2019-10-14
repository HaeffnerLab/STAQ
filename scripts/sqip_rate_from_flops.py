#import matplotlib
#matplotlib.use('Qt4Agg')
# from simple_analysis.get_data import *
from sqip_rabi_flop_fitter import *
#from nbar_rabi import *
import scipy.optimize as op
import lmfit
from matplotlib import pyplot
# from U2freqcalc import freq_from_U2

#this is for cycling colors so you can plot in multiple colors and coordinate data points and fits
from itertools import cycle
cycol = cycle('bgrcmk').next 

hbar = 1.0546e-34
m = 39.96*1.66e-27

def import_data(filename):
	t,p = np.loadtxt(filename,unpack=True, delimiter=',')
	return t,p

def calc_eta(trap_freq,theta):
        theta = np.deg2rad(theta)
        return 2*np.pi/729.e-9*np.sqrt(hbar/(2*m*2*np.pi*trap_freq))*np.cos(theta)

def compute_approx_thermal(nbars,time_2pi,etas,t):
        omega = np.pi/time_2pi
        scaling = sum([etas[i]**2*nbars[i] for i in range(len(nbars))])
        Qfunc = [np.exp(2j*omega*x)/(1+1j*omega*x*scaling) for x in t]
        return [0.5*(1-np.real(x)) for x in Qfunc]

def plot_heating_rate(times,data,err,label=''):
        mycolor = cycol()
        pyplot.errorbar(times, data,yerr=err,fmt='o',color=mycolor)
        pyplot.ylabel(r'$\bar{n}$', fontsize=18)
        pyplot.xlabel('time (ms)',fontsize=18)
        def f(x,rate,offset):
                return rate*x+offset
        popt,pcov = op.curve_fit(f,times,data,p0=[1,20],sigma=err)
        #variance = cov_matrix[0][0]
        perr = np.sqrt(np.diag(pcov))
        rate = popt[0]
        offset = popt[1]
        #print popt
        #print perr
        #stderr = np.sqrt(variance)
        stderr = perr[0]
        #print "{0:.2f}".format(rate) + ' +- ' + "{0:.2f}".format(stderr) + ' n/ms'
        #print str(rate*1000.)+' n/s'
        times = np.sort(times)
        pyplot.plot(times, rate*times+offset,label=label,color=mycolor)
        #pyplot.title('heating rate of ' + "{0:.2f}".format(rate) + ' +- ' + "{0:.2f}".format(stderr) + ' n/ms for trap freq ' + str(int(trap_freq/1000)) + ' kHz')
        return rate,stderr

def fit_rabi_flops(file_loc,file_ext,data_dict,trap_freq,plot_flops,excitation_scaling,time_2pi,nbar,etas,delta):
        nbarlist = []
        nbarerrs = []
        pitimes = []
        pitimeserr = []
        deltas = []
        deltaserr = []
        # if plot_flops:
                # pyplot.figure()
        #this part does the rabi flop fitting for each data set
        times = np.sort(data_dict.keys())
        eta = etas[0]
        for key in times:
                #import data and calculate errors based on 100 experiments
                t,p = import_data(file_loc + str(data_dict[key][0]) + ".dir/" + file_ext + str(data_dict[key][0]) + ".csv")
                p[0] = 0.001 #there is something wrong with the first entry and this solves it?
                perr = [np.sqrt(x*(1-x)/100.) for x in p]
                #model for Rabi flops, use 0 for sidebands, +-1 etc for sidebands..
                te = rabi_flop_time_evolution(0,eta,nmax=2500) #if you get the error that the hilbert space is too small, then increase nmax
                params = lmfit.Parameters()
                params.add('delta',value = 0.0,vary=False)
                #params.add('delta',value = delta ,vary=True,min=0.01,max=0.04)
                params.add('nbar',value = nbar,min=0.0,max=200.0)

                if key == 0:
                        params.add('time_2pi',value = time_2pi,vary=True)
                else:
                        params.add('time_2pi',value = time_2pi,vary=False)
                        
##                params.add('nbar1',value = nbar,min=0.0,max=100.0,vary=True)
##                params.add('nbar2',value = nbar,min=0.0,max=100.0,vary=True)
##
                
                def rabi_fit_thermal(params,t,data,err):
                        model = te.compute_evolution_thermal(params['nbar'].value, params['delta'].value, params['time_2pi'].value, t,excitation_scaling=excitation_scaling)
                        resid = model-data
                        weighted = [np.sqrt(resid[x]**2/err[x]**2) for x in range(len(err))]
                        return weighted

                def rabi_fit_approx(params,t,data,err):
                        #print params['nbar2'].value                      
                        model = compute_approx_thermal([params['nbar1'].value,params['nbar2'].value], params['time_2pi'].value,etas,t)
                        resid = model-data
                        weighted = [np.sqrt(resid[x]**2/err[x]**2) for x in range(len(err))]
                        return weighted

                if len(etas)<2:
                        result = lmfit.minimize(rabi_fit_thermal,params,args = (t,p,perr))
                        params = result.params
                        if key == 0:
                                time_2pi = params['time_2pi'].value
                        fit_values = te.compute_evolution_thermal(params['nbar'].value, params['delta'].value, params['time_2pi'].value, t)
                        nbarlist=np.append(nbarlist,params['nbar'].value)
                        nbarerrs=np.append(nbarerrs,params['nbar'].stderr)

                else:
                        result = lmfit.minimize(rabi_fit_approx,params,args = (t,p,perr))
                        params = result.params
                        if key == 0:
                                time_2pi = params['time_2pi'].value
                        fit_values = compute_approx_thermal([params['nbar1'].value,params['nbar2'].value], params['time_2pi'].value,etas,t)
                        nbarlist=np.append(nbarlist,params['nbar1'].value)
                        nbarerrs=np.append(nbarerrs,params['nbar1'].stderr)
                        print nbarerrs

                #print "nbar fit for " + str(key) + "   " + str(params['nbar'].value) + " +- " + str(params['nbar'].stderr)
                #print "reduced chisquared: " + str(result.redchi)
                #print str(key) + "   " + str(params['time_2pi'].value) + " +- " + str(params['time_2pi'].stderr)         

                pitimes = np.append(pitimes,params['time_2pi'].value/2.0)
                pitimeserr = np.append(pitimeserr,params['time_2pi'].stderr/2.0)
                deltas = np.append(deltas,params['delta'].value)
                deltaserr = np.append(deltaserr,params['delta'].stderr)
                
                if plot_flops:
                        pyplot.figure()
                        mycolor = cycol()
                        pyplot.plot(t,p,'-o',label = 'data ' + str(key),color=mycolor)
                        pyplot.plot(t,fit_values,'r',label = 'fitted '+ str(key),color=mycolor)
                        pyplot.title('flops for trap freq ' + str(int(trap_freq/1000)) + ' kHz')
                        pyplot.legend()
        return (times,nbarlist,nbarerrs)
 
###parameters inserted into calculation
##trap_freq = 518000.0
##nbar = 50 #guess for nbar
##excitation_scaling=1.0 #change this if OP not working
##plot_flops=True #set to true to plot the flops
##theta=45
##time_2pi=19 #in microseconds
###etas = [calc_eta(trap_freq,theta),calc_eta(4000000.0,45)]#this needs to be calculated properly?? don't know if this is right? 
##etas = [calc_eta(trap_freq,theta)]
##
###data for U2 = 2 with ramping on
##file_loc = "/Users/crystalnoel/Dropbox/Grad School/SQIP/05292017_heatingrates/2017May29_withramping.dir/"
##file_ext = "00001 - Rabi Flopping 2017May29_"
##data_dict = {}
##data_dict[0.0] = ['1136_31']
##data_dict[2.0] = ['1137_28']
##data_dict[4.0] = ['1138_34'] 
##data_dict[5.0] = ['1139_48']
##data_dict[0.001] = ['1141_23']
##data_dict[1.0] = ['1142_22'] 
##
##(timeswithramp,nbarlistwithramp,nbarerrswithramp) = fit_rabi_flops(data_dict,trap_freq,plot_flops,excitation_scaling,time_2pi,nbar,etas)
##
##
##
#####data for ramping -- acutally ramping wasnt on oops
####file_loc = "/Users/crystalnoel/Dropbox/Grad School/SQIP/05242017_heatingrates/2017May24_ramping.dir/"
####file_ext = "00001 - Rabi Flopping 2017May24_"
####data_dict = {}
####data_dict[0.0] = ['1208_02']
####data_dict[2.0] = ['1219_55']
####data_dict[4.0] = ['1213_46'] 
####data_dict[3.0] = ['1210_42']
#####data_dict[1.0] = ['1216_58'] #idk why but this won't fit
####
####(timesnoramp,nbarlistnoramp,nbarerrsnoramp) = fit_rabi_flops(data_dict,trap_freq,plot_flops,excitation_scaling,time_2pi,nbar,etas)
####
##
###data without ramping
##file_loc = "/Users/crystalnoel/Dropbox/Grad School/SQIP/05242017_heatingrates/2017May24.dir/"
##file_ext = "00001 - Rabi Flopping 2017May24_"
##data_dict = {}
##data_dict[0.0] = ['1150_43']
##data_dict[2.0] = ['1153_38']
###data_dict[4.0] = ['1156_29'] #too noisy to fit
##data_dict[3.0] = ['1159_42']
##data_dict[1.0] = ['1202_44']
##
##(timesnoramp,nbarlistnoramp,nbarerrsnoramp) = fit_rabi_flops(data_dict,trap_freq,plot_flops,excitation_scaling,time_2pi,nbar,etas)
##
##pyplot.figure()
##plot_heating_rate(timesnoramp,nbarlistnoramp,nbarerrsnoramp,'No ramping')
##plot_heating_rate(timeswithramp,nbarlistwithramp,nbarerrswithramp,'Ramping on')
##pyplot.legend()
##pyplot.show()
