#
#  Copyright (c) 2019-present Cumulocity GmbH, Duesseldorf, Germany and/or its affiliates and/or their licensors.
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

__pysys_title__ = r'SmartFunction block: to check the basic working of the block'
__pysys_purpose__ = r''

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def preInjectBlock(self, corr):                                    
		self._injectEPLOnce(corr, [self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['Base64']])  
		self._injectEPLOnce(corr, [self.project.testRootDir+'/utils/DeviceServiceMock.mon'])

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/', arguments=["--config", f"{self.project.SOURCE}/blocks/Python/plugin.yaml"])
		
		self.modelId = self.createTestModel('apamax.analyticsbuilder.samples.SmartFunction', {
			'label': 'JS Test Model',
			'param1': '42',
			'smartFunction':"""export function onInput(inputs, context) {
    let message = Base64.decodeStr(inputs[0].value)
    console.log("Received message: " + message)
    return [Base64.encodeStr("Response from Cumulocity")];
}"""
		})
		
		self.sendEventStrings(self.correlator,
								self.timestamp(1),
								self.inputEvent('value1', "SGVsbG8gV29ybGQ=", id = self.modelId, properties={'value1': 'value'}),
								self.timestamp(2),
							  )

		self.correlator.flush()
		self.correlator.shutdown()


	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(errorIgnores=['Unknown dynamicChain', 'CumulocityRestAPIMonitor', 'CumulocityRequestInterface', 'Notifications2Subscriber'], warnIgnores=['Also deleting'])
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Processing inputs')
		
		# Verifying the result - output from the block.
		self.assertBlockOutput('result1', [4.5, -5.])
		self.assertBlockOutput('result2', [4.5, -5.])
		self.assertBlockOutput('result3', [42, 42])
		self.assertBlockOutput('result4', [2, 3])
		self.assertThat("output == expected",
						expected=[{'param1': '42', 'param2': None, 'value1': 'value', 'value2': 'value'}, {'param1': '42', 'param2': None, 'value1': 'value', 'value2': 'value'}],
						output=[x['properties'] for x in self.allOutputFromBlock(self.modelId) if x['outputId']=='result3'])
