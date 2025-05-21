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
		self._injectEPLOnce(corr, [self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['TolerateAPI', 'cumulocity/Cumulocity_Rest_API', 'Notifications2.0Events', 'Notifications2.0Subscriptions', 'MQTTServiceEvents', 'MQTTServiceSubscription', 'MQTTServiceEvents']])  

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/', arguments=["--config", f"{self.project.SOURCE}/blocks/Python/plugin.yaml"])
		
		self.modelId = self.createTestModel('apamax.analyticsbuilder.samples.Logger', {
			'loggerTag': 'thisBlock',
			'logLevel': 'INFO',
		})
		
		self.sendEventStrings(self.correlator,
							  self.timestamp(1),
							  self.inputEvent('input', 5, id = self.modelId),
							  self.timestamp(2),
							  self.inputEvent('input', "12345", id = self.modelId),
							  self.timestamp(3),
							  )


	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(errorIgnores=['Unknown dynamicChain', 'CumulocityRestAPIMonitor', 'CumulocityRequestInterface', 'Notifications2Subscriber'])
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
	
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr=r'INFO.*\[thisBlock\] any\(float,5\) \(\{\}\)')
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr=r'INFO.*\[thisBlock\] any\(string,"12345"\) \(\{\}\)')
