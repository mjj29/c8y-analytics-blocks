#
#  Copyright (c) 2019-present Cumulocity GmbH, Duesseldorf, Germany and/or its affiliates and/or their licensors.
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

__pysys_title__ = r'Property Mapper: to check the basic working of the block'
__pysys_purpose__ = r''

import json
from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def preInjectBlock(self, corr):                                    
		self._injectEPLOnce(corr, [self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['Base64']])  
		self._injectEPLOnce(corr, [self.project.testRootDir+'/utils/DeviceServiceMock.mon'])

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/', arguments=["--config", f"{self.project.SOURCE}/blocks/ONNX/","--config", f"{self.project.SOURCE}/blocks/Python/"])
		
		self.modelId = self.createTestModel('apamax.analyticsbuilder.samples.PropertyMapper', {
			'valueOutputMapping': 'data.value',
			'externalIdOutputMapping': 'data.clientId',
			'propertiesOutputMapping': """inputValue=value
foo=bar.baz
bar.baz=data.quux
""",
		})
		
		self.sendEventStrings(self.correlator,
							  self.timestamp(1),
							  self.inputEvent('input', 5, id = self.modelId, properties={
									'data': {
										'clientId': '1234',
										'value': 3.14,
										'quux': 'test',
									},
								  'bar': {
									  'baz': 42,
								  }
							  }),
							  self.timestamp(2),
							  )


	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(errorIgnores=['Unknown dynamicChain', 'CumulocityRestAPIMonitor', 'CumulocityRequestInterface', 'Notifications2Subscriber'])
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
	
		# Verify the encoder produces the expected output
		output = self.allOutputFromBlock(self.modelId)
		self.validateOutput(output, 'value', 3.14, {})
		self.validateOutput(output, 'externalId', '1234', {})
		self.validateOutput(output, 'properties', True, {'inputValue':5, 'foo':42, 'bar': {'baz':'test'}})

	def validateOutput(self, output, outputId, value, properties):
		for o in output:
			if o['outputId'] == outputId:
				self.assertThat("value == expected", value=o['value'], expected=value)
				self.assertThat("properties == expected", properties=o['properties'], expected=properties)
				return
		self.abort(BLOCKED, "Output not found for outputId: " + outputId)
