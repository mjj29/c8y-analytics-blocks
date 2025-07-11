#
#  Copyright (c) 2019-present Cumulocity GmbH, Duesseldorf, Germany and/or its affiliates and/or their licensors.
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

__pysys_title__ = r'InboundDeviceBlock: to check the basic working of the block'
__pysys_purpose__ = r''

import json
from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def _injectCumulocitySupport(self, corr):                                    
		AnalyticsBuilderBaseTest._injectCumulocitySupport(self, corr)
		self._injectEPLOnce(corr, [self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['TolerateAPI', 'cumulocity/Cumulocity_Rest_API', 'Notifications2.0Events', 'Notifications2.0Subscriptions', 'MQTTServiceEvents']])  
		self._injectEPLOnce(corr, [self.project.testRootDir+'/utils/MQTTServiceMock.mon'])
		self._injectEPLOnce(corr, [self.project.testRootDir+'/utils/MQTTServiceMock.mon'])

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/', arguments=["--config", f"{self.project.SOURCE}/blocks/Python/plugin.yaml"])
		
		self.modelId = self.createTestModel('apamax.analyticsbuilder.samples.DeviceInputText', {
			'topic': 'topicName',
		}, id="model1")
		
		self.modelId2 = self.createTestModel('apamax.analyticsbuilder.samples.DeviceInputText', {
			'topic': 'topicName',
		}, id="model2")

		self.waitForGrep('correlator.log', expr='DeviceInputText: Subscription created for topic')
		
		self.sendEventStrings(self.correlator, self.timestamp(1))
		self.correlator.sendEventStrings('com.apama.cumulocity.mqttservice.MQTTServiceMessage("topicName", {"foo": any(string, "bar")}, {"textData":any(string, "{\\"t\\": 72.0 }")})', channel="receivetopicName")
		self.sendEventStrings(self.correlator, self.timestamp(2))

	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(errorIgnores=['Unknown dynamicChain', 'CumulocityRestAPIMonitor', 'CumulocityRequestInterface', 'Notifications2Subscriber'])
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId2 + '\" with PRODUCTION mode has started')

		output = self.allOutputFromBlock(self.modelId)
		self.assertThat("output == '{\"t\": 72.0 }'", output=output[0]['value'])
		self.assertThat("output == {'foo': 'bar'}", output=output[0]['properties'])
		output2 = self.allOutputFromBlock(self.modelId2)
		self.assertThat("output == '{\"t\": 72.0 }'", output=output2[0]['value'])
		self.assertThat("output == {'foo': 'bar'}", output=output2[0]['properties'])
	
