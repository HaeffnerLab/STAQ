from sqip_rate_from_flops import *
import os

#parameters inserted into calculation
trap_freq = 1.1*1e6 #in Hz
nbar = 10 #guess for nbar
excitation_scaling=1 #change this if OP not working
plot_flops=True #set to true to plot the flops
theta=11.5 #the0 angle of the laser with the trap axis
time_2pi=150 #guess for 2pi time in microseconds

etas = [calc_eta(trap_freq,theta)]
delta={}
current_dir=os.getcwd()
#data without ramping
file_loc = current_dir #+ "/2017_08_22 heating rates/"
file_ext = ''#"00001 - Rabi Flopping 2017Aug22_"
data_dict = {} #keys are the wait time in


data_dict[0] = ['2044_51']
data_dict[10] = ['2046_53']


(times,nbarlist,nbarerrs) = fit_rabi_flops(file_loc,file_ext,data_dict,trap_freq,plot_flops,excitation_scaling,time_2pi,nbar,etas,delta)
print (times,nbarlist,nbarerrs)

pyplot.figure()
print times
print nbarlist
print nbarerrs
rate,stderr = plot_heating_rate(times,nbarlist,nbarerrs,'{} MHz'.format(trap_freq)) #linear fit of nbar
print "{0:.2f}".format(rate) + ' +- ' + "{0:.2f}".format(stderr) + ' n/ms for {} MHz'.format(trap_freq) #prints out heating rate
pyplot.title("{0:.2f}".format(rate) + ' +- ' + "{0:.2f}".format(stderr)+"quanta/ms")
pyplot.legend()
pyplot.show()
