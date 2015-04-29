class config(object):

    #list in the format (import_path, class_name)
    scripts = [
               ('lattice.scripts.experiments.FFT.fft_spectrum', 'fft_spectrum'), 
#                ('lattice.scripts.experiments.FFT.fft_peak_area', 'fft_peak_area'), 
#                ('lattice.scripts.experiments.FFT.fft_hv_scan', 'fft_hv_scan'), 
#                ('lattice.scripts.experiments.Misc.set_high_volt', 'set_high_volt'), 
               ('lattice.scripts.experiments.Misc.set_linetrigger_offset', 'set_linetrigger_offset'), 
               ('lattice.scripts.experiments.CavityScan.scan_cavity', 'scan_cavity'), 
               ('lattice.scripts.experiments.CavityScan.scan_cavity_397', 'scan_cavity_397'), 
               ('lattice.scripts.experiments.CavityScan.scan_cavity_866', 'scan_cavity_866'), 
#                ('lattice.scripts.experiments.Experiments729.excitation_729', 'excitation_729'), 
               ('lattice.scripts.experiments.Experiments729.spectrum', 'spectrum'), 
               ('lattice.scripts.experiments.Experiments729.rabi_flopping', 'rabi_flopping'), 
#                ('lattice.scripts.experiments.Experiments729.drift_tracker', 'drift_tracker'), 
#                ('lattice.scripts.experiments.Experiments729.excitation_ramsey', 'excitation_ramsey'), 
               ('lattice.scripts.experiments.Experiments729.ramsey_scangap', 'ramsey_scangap'), 
               ('lattice.scripts.experiments.Experiments729.ramsey_scanphase', 'ramsey_scanphase'), 
#                ('lattice.scripts.experiments.Experiments729.excitation_rabi_tomography', 'excitation_rabi_tomography'), 
               ('lattice.scripts.experiments.Experiments729.rabi_tomography', 'rabi_tomography'), 
               ('lattice.scripts.experiments.BareLineScan.BareLineScanRed', 'bare_line_scan_red'), 
               ('lattice.scripts.experiments.BareLineScan.BareLineScan', 'bare_line_scan'),
               ('lattice.scripts.experiments.AO_calibration.AO_calibration', 'AO_calibration'), 
               ('lattice.scripts.experiments.Experiments729.drift_tracker_ramsey', 'drift_tracker_ramsey'), 
               ('lattice.scripts.experiments.Camera.reference_image', 'reference_camera_image'), 
               ('lattice.scripts.experiments.Lifetime_P.lifetime_p', 'lifetime_p'), 
               ('lattice.scripts.experiments.Experiments729.rabi_flop_scannable', 'rabi_flopping_scannable'), 
               ('lattice.scripts.experiments.Experiments729.ramsey_2ions_scangap_parity', 'ramsey_2ions_scangap_parity'),
               ('lattice.scripts.experiments.Experiments729.rabi_flopping_2ions', 'rabi_flopping_2ions'),
               ('lattice.scripts.experiments.Experiments729.Parity_LLI_scan_gap', 'Parity_LLI_scan_gap'),
               ('lattice.scripts.experiments.Experiments729.Parity_LLI_scan_phase', 'Parity_LLI_scan_phase'),
               ('lattice.scripts.experiments.Experiments729.Sideband_tracker', 'Sideband_tracker'),
               ('lattice.scripts.experiments.Experiments729.Parity_LLI_phase_tracker', 'Parity_LLI_phase_tracker'),
               ('lattice.scripts.experiments.Experiments729.Parity_LLI_monitor', 'Parity_LLI_monitor'),
               ('lattice.scripts.experiments.Experiments729.Parity_LLI_2_point_monitor', 'Parity_LLI_2_point_monitor'),
               ('lattice.scripts.experiments.Experiments729.rabi_power_flopping_2ions', 'Rabi_power_flopping_2ions'),
               ('lattice.scripts.experiments.Experiments729.Parity_LLI_rabi_power_fitter', 'Parity_LLI_rabi_power_fitter'),
#                ('lattice.scripts.experiments.Experiments729.blue_heat_rabi_flopping', 'blue_heat_rabi_flopping'), 
#                ('lattice.scripts.experiments.Experiments729.blue_heat_spectrum', 'blue_heat_spectrum'), 
#                ('lattice.scripts.experiments.Experiments729.blue_heat_scan_delay', 'blue_heat_scan_delay'), 
#                ('lattice.scripts.experiments.Experiments729.blue_heat_scan_pulse_freq', 'blue_heat_scan_pulse_freq'), 
#                ('lattice.scripts.experiments.Experiments729.blue_heat_scan_pulse_freq_ramsey', 'blue_heat_scan_pulse_freq_ramsey'), 
#                ('lattice.scripts.experiments.Experiments729.blue_heat_scan_pulse_phase_ramsey', 'blue_heat_scan_pulse_phase_ramsey'),
               ('lattice.scripts.experiments.Experiments729.dephasing_scan_duration', 'dephase_scan_duration'),
               ('lattice.scripts.experiments.Experiments729.dephasing_scan_phase', 'dephase_scan_phase'),
               ('lattice.scripts.experiments.Experiments729.dephasing_scan_phase', 'dephase_scan_phase'),
               ('lattice.scripts.experiments.Experiments729.dephasing_scan_duration_Phase', 'dephase_scan_duration'),
               ]
    #dictionary in the format class_name : list of non-conflicting class names
    allowed_concurrent = {
    }
