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
		self._injectEPLOnce(corr, [self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['DeviceService','Base64']])  
		self._injectEPLOnce(corr, [self.project.testRootDir+'/utils/DeviceServiceMock.mon'])

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/', arguments=["--config", f"{self.project.SOURCE}/blocks/Python/plugin.yaml"])
		
		self.modelId = self.createTestModel('apamax.analyticsbuilder.samples.Python', {
			'label': 'Python Test Model',
			'pythonFunction':"""import base64
def onInput(inputs, context):
    # Decode the incoming message
    raw = inputs[0].value
    message = base64.b64decode(raw).decode("utf-8")
    context.logger.info("Received message: "+ message)

    # Encode the outgoing message
    response = base64.b64encode(b"Response from Cumulocity").decode("utf-8")
    return [response]
"""
		})
		
		self.sendEventStrings(self.correlator,
								self.timestamp(1),
								self.inputEvent('value1', 'SGVsbG8gV29ybGQ=', id = self.modelId, properties={'value1': 'value'}),
								self.timestamp(2.5),
							  )


	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(errorIgnores=['Unknown dynamicChain', 'CumulocityRestAPIMonitor', 'CumulocityRequestInterface', 'Notifications2Subscriber'])
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Processing inputs')
		
		# Verifying the result - output from the block.
		self.assertBlockOutput('result1', [4.5, 5])
		self.assertBlockOutput('result2', [4.5, -5])
		self.assertBlockOutput('result4', [2, 3])

		self.assertThat("output == expected",
						expected=[{'value1': 'value', 'value2': 'value'}, {'value1': 'value', 'value2': 'value'}],
						output=[x['properties'] for x in self.allOutputFromBlock(self.modelId) if x['outputId']=='result3'])
