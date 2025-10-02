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
			'label': 'Python Test Model',
			'pythonFunction':"""import math, operator, json
def onInput(inputs, context):
	context.logger.info("Processing inputs: " + str([i.value for i in inputs]))
	(a, b) = (inputs[0].value, inputs[1].value)
	context.logger.info("a: " + str(a) + ", b: " + str(b))
	context.setState("counter", context.getState("counter", 0.) + 1.)
	context.logger.info("counter incremented")
	if a and b:
		context.logger.info("Both inputs are valid numbers")
		context.logger.info("json="+str(json)+"json.dumps="+str(json.dumps))
		return [
			math.fabs(a-b),
			operator.sub(a, b),
			Value(True, {'value1': inputs[0].properties['value1'], 'value2': inputs[1].properties['value2']}),
			Value(context.getState("counter")),
			json.dumps(inputs[0].properties)
		]
	else:
		context.logger.info("One or both inputs are not valid numbers")
		return None
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
		self.assertBlockOutput('result4', [2, 3])

		self.assertThat("output == expected",
						expected=[{'value1': 'value', 'value2': 'value'}, {'value1': 'value', 'value2': 'value'}],
						output=[x['properties'] for x in self.allOutputFromBlock(self.modelId) if x['outputId']=='result3'])
