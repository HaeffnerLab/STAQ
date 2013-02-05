from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence

class repump_d(pulse_sequence):
    
    @classmethod
    def required_parameters(cls):
        config = [
                  'repump_d_duration',
                  'repump_d_frequency_854',
                  'repump_d_amplitude_854',
                  ]
        return config
    
    def sequence(self):
        self.end = self.start + self.repump_d_duration
        pulse = ('854DP', self.start, self.repump_d_duration, self.repump_d_frequency_854, self.repump_d_amplitude_854)
        self.dds_pulses.append(pulse)