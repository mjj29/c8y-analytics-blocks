#
#  Copyright (c) 2019-present Cumulocity GmbH, Duesseldorf, Germany and/or its affiliates and/or their licensors.
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

__pysys_title__ = r'OutboundDeviceBlock: to check the basic working of the block'
__pysys_purpose__ = r''

import json
from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def _injectCumulocitySupport(self, corr):                                    
		AnalyticsBuilderBaseTest._injectCumulocitySupport(self, corr)
		self._injectEPLOnce(corr, [self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['DeviceService', 'Base64']])  
		self._injectEPLOnce(corr, [self.project.testRootDir+'/utils/DeviceServiceMock.mon'])

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/', arguments=["--config", f"{self.project.SOURCE}/blocks/Python/plugin.yaml"])
		
		self.modelId = self.createTestModel('apamax.analyticsbuilder.samples.DeviceOutput', {
			'transport': 'mqtt',
			'topic': 'topicName',
			'clientID': 'clientFoo',
		}, id="model1")
		
		self.sendEventStrings(self.correlator, 
								self.timestamp(1),
								self.inputEvent('value', 'SGVsbG8gV29ybGQ=', id=self.modelId, properties={'foo':'bar'}),
								self.timestamp(2))
		self.waitForSignal(self.analyticsBuilderCorrelator.logfile, expr="Received device message")

	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(errorIgnores=['Unknown dynamicChain', 'CumulocityRestAPIMonitor', 'CumulocityRequestInterface', 'Notifications2Subscriber'])
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')

		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Received device message: com.apama.cumulocity.devices.DeviceMessage."mqtt","clientFoo","topicName".*"foo":.*"bar".* decoded payload: Hello World')
	
