#
#  Copyright (c) 2019-present Cumulocity GmbH, Duesseldorf, Germany and/or its affiliates and/or their licensors.
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

__pysys_title__ = r'Logger: to check the basic working of the block'
__pysys_purpose__ = r''

import json
from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def preInjectBlock(self, corr):                                    
		self._injectEPLOnce(corr, [self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['Base64']])  
		self._injectEPLOnce(corr, [self.project.testRootDir+'/utils/DeviceServiceMock.mon'])

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/', arguments=["--config", f"{self.project.SOURCE}/blocks/Python/plugin.yaml"])
		
		self.modelId1 = self.createTestModel('apamax.analyticsbuilder.samples.Logger', {
			'loggerTag': 'implicitBlock',
			'logLevel': 'INFO',
		})
		self.modelId2 = self.createTestModel('apamax.analyticsbuilder.samples.Logger', {
			'loggerTag': 'explicitTrueBlock',
			'logLevel': 'INFO',
			'disableOutput': 'true',
		})
		self.modelId3 = self.createTestModel('apamax.analyticsbuilder.samples.Logger', {
			'loggerTag': 'explicitFalseBlock',
			'logLevel': 'INFO',
			'disableOutput': 'false',
		})
		
	
		self.sendEventStrings(self.correlator,
							  self.timestamp(1),
							  self.inputEvent('input', 5, id = self.modelId1),
							  self.timestamp(2),
							  self.inputEvent('input', "12345", id = self.modelId1),
							  self.inputEvent('input', "12345", id = self.modelId2),
							  self.inputEvent('input', "12345", id = self.modelId3),
							  self.timestamp(3),
							  )


	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(errorIgnores=['Unknown dynamicChain', 'CumulocityRestAPIMonitor', 'CumulocityRequestInterface', 'Notifications2Subscriber'])
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId1 + '\" with PRODUCTION mode has started')
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId2 + '\" with PRODUCTION mode has started')
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId3 + '\" with PRODUCTION mode has started')
	
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr=r'INFO.*\[implicitBlock\] any\(float,5\) \(\{\}\)')
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr=r'INFO.*\[implicitBlock\] any\(string,"12345"\) \(\{\}\)')
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr=r'INFO.*\[explicitTrueBlock\] any\(string,"12345"\) \(\{\}\)', contains=False)
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr=r'INFO.*\[explicitFalseBlock\] any\(string,"12345"\) \(\{\}\)')
