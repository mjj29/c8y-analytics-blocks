#
#  Copyright (c) 2025-present Cumulocity GmbH, Duesseldorf, Germany and/or its affiliates and/or their licensors.
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

__pysys_title__ = r'AIAgent block: to check the basic working of the block'
__pysys_purpose__ = r''

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def preInjectBlock(self, corr):
		self._injectEPLOnce(corr, [self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['Base64']])  
		self._injectEPLOnce(corr, [self.project.testRootDir+'/utils/DeviceServiceMock.mon'])
		self._injectEPLOnce(corr, [self.project.testRootDir+'/utils/AIAgentMock.mon'])

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/', arguments=["--config", f"{self.project.SOURCE}/blocks/ONNX/onnx-plugin.yaml", "--config", f"{self.project.SOURCE}/blocks/Python/python-plugin.yaml"])
		
		self.modelId = self.createTestModel('apamax.analyticsbuilder.samples.AIAgent', {
			'agentName':'testAgent',
			'promptTemplate':'The sum of {value1} and {value2} is',
		})
		
		self.sendEventStrings(self.correlator,
								self.timestamp(1),
								self.inputEvent('value1', "12.25", id = self.modelId),
								self.inputEvent('value2', "7.75", id = self.modelId),
								self.timestamp(2),
							  )

		self.correlator.waitForLogGrep('AI Agent request (succeeded|failed)')
		self.correlator.waitForLogGrep('Handling AI Agent Mock Response')


	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(errorIgnores=['Unknown dynamicChain', 'CumulocityRestAPIMonitor', 'CumulocityRequestInterface', 'Notifications2Subscriber'], warnIgnores=['Host not found'])
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		
		# Verifying the result - output from the block.
		self.assertBlockOutput('result', ["20"])
