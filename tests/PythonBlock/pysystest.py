#
#  Copyright (c) 2019-present Cumulocity GmbH, Duesseldorf, Germany and/or its affiliates and/or their licensors.
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

__pysys_title__ = r'Python block: to check the basic working of the block'
__pysys_purpose__ = r''

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def preInjectBlock(self, corr):                                    
		self._injectEPLOnce(corr, [self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['TolerateAPI', 'cumulocity/Cumulocity_Rest_API', 'Notifications2.0Events', 'Notifications2.0Subscriptions', 'MQTTServiceEvents']])  
		self._injectEPLOnce(corr, [self.project.testRootDir+'/utils/MQTTServiceMock.mon'])

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/', arguments=["--config", f"{self.project.SOURCE}/blocks/Python/plugin.yaml"])
		
		self.modelId = self.createTestModel('apamax.analyticsbuilder.samples.Python', {
			'expression':"""
state["counter"] = state.get("counter", 0.) + 1.
if inputs[0].value and inputs[1].value:
	outputs[0].value = abs(inputs[0].value - inputs[1].value)
	outputs[1].value = inputs[0].value - inputs[1].value
	outputs[2].value = str({'value1': inputs[0].properties['value1'], 'value2': inputs[1].properties['value2']})
	outputs[3].value = state["counter"]
else:
	generate = False
"""
		})
		
		self.sendEventStrings(self.correlator,
								self.timestamp(1),
								self.inputEvent('value1', 12.25, id = self.modelId, properties={'value1': 'value'}),
								self.timestamp(2),
								self.inputEvent('value2', 7.75, id = self.modelId, properties={'value2': 'value'}),  #absolute Output at this point would be 4.5 (12.25-7.75)
								self.timestamp(2.1),
								self.inputEvent('value2', 17.25, id=self.modelId, properties={'value2': 'value'}),  #signed Output at this point would be -5 (12.25-17.25)
								self.timestamp(2.5),
							  )


	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(errorIgnores=['Unknown dynamicChain', 'CumulocityRestAPIMonitor', 'CumulocityRequestInterface', 'Notifications2Subscriber'])
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		
		# Verifying the result - output from the block.
		self.assertBlockOutput('result1', [4.5, 5])
		self.assertBlockOutput('result2', [4.5, -5])
		self.assertBlockOutput('result3', ["{'value1': 'value', 'value2': 'value'}", "{'value1': 'value', 'value2': 'value'}"])
		self.assertBlockOutput('result4', [2, 3])
