from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class DopplerCooling(pulse_sequence):
   
    #def addDDS(self, channel, start, duration, frequency, amplitude, phase = WithUnit(0, 'deg'), profile = 0):
    def sequence(self):
        p = self.parameters.DopplerCooling

        repump_duration = p.doppler_cooling_duration + p.doppler_cooling_repump_additional
        self.addDDS ('397dp',self.start, p.doppler_cooling_duration, p.doppler_cooling_frequency_397, p.doppler_cooling_amplitude_397)
        self.addDDS ('866dp',self.start, repump_duration, p.doppler_cooling_frequency_866, p.doppler_cooling_amplitude_866)
        self.end = self.start + repump_duration
        
