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
		self._injectEPLOnce(corr, [self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['DeviceService','Base64']])  
		self._injectEPLOnce(corr, [self.project.testRootDir+'/utils/DeviceServiceMock.mon'])

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/', arguments=["--config", f"{self.project.SOURCE}/blocks/Python/plugin.yaml"])
		
		self.modelId = self.createTestModel('apamax.analyticsbuilder.samples.SmartFunction', {
			'label': 'JS Test Model',
			'param1': '42',
			'smartFunction':"""export function onInput(inputs, ctx) {
	console.log("Processing inputs");
	ctx.setState("count", ctx.getState("count", 0) + 1);
	if (inputs[0].value == null || inputs[1].value == null) {
		return null;
	} else {
		return [inputs[0].value - inputs[1].value, {value: inputs[0].value - inputs[1].value}, {value: Number(ctx.blockParameters.param1), properties: { 'param1':ctx.blockParameters.param1, 'param2':ctx.blockParameters.param2, ...inputs[0].properties, ...inputs[1].properties}}, ctx.getState("count")];
	}
}
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

		self.correlator.flush()
		self.correlator.delete(all=True)
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
