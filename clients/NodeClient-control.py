import labrad 
import numpy as np
import time

nodeDict = {
			'node_staq':[
								'Serial Server',
								'Data Vault',
								# #'DAC',
								# 'DAC Server',
								'Pulser',
								# #'Real Simple Grapher',
								'NormalPMTFlow',
								# 'ADCserver',
								# 'SD Tracker',
								'GPIB Device Manager', 
								'ScriptScanner',
								'ParameterVault',
								# # 'SHQ_222M_SERVER',
								# # 'Electrode Diagonalization',
								# # 'Crystallizer',
								# # 'Agilent 6030A Server',
								# # 'Agilent E3633A',
								# # 'Rigol DG4062 Server',
								# # 'Fitter',
								# # 'DDS_CW',
								# # 'Picomotor'
								],
			}
#connect to LabRAD


errors = False
try:
	cxn = labrad.connect()
except Exception:
	print 'Please start LabRAD Manager'
else:
	nodes = nodeDict.keys()
	if not len(nodes):
		print "No Nodes Running"
	for node in nodeDict.keys():
		#make sure all node servers are up
		if not node in cxn.servers: print '{} is not running'.format(node)
		else:
			print '\nWorking on {} \n '.format(node)
			cxn.servers[node].refresh_servers()
			#if node server is up, start all possible servers on it that are not already running
			# running_servers = np.array(cxn.servers[node].running_servers().asarray)
			running_servers = [server[0] for server in cxn.servers[node].running_servers()]
			for server in nodeDict[node]:
				if server in running_servers: 
					print server + ' is already running'
				else:
					print 'starting ' + server
					try:
						cxn.servers[node].start(server)
					except Exception as e:
						print 'ERROR with ' + server
print 'DONE'	
