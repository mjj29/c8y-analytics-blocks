#
#  Copyright (c) 2019-present Cumulocity GmbH, Duesseldorf, Germany and/or its affiliates and/or their licensors.
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

__pysys_title__ = r'Device Simulator: to check the basic working of the block'
__pysys_purpose__ = r''

import json
from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def preInjectBlock(self, corr):                                    
		self._injectEPLOnce(corr, [self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['Base64']])  
		self._injectEPLOnce(corr, [self.project.testRootDir+'/utils/DeviceServiceMock.mon'])

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/', arguments=["--config", f"{self.project.SOURCE}/blocks/ONNX/onnx-plugin.yaml","--config", f"{self.project.SOURCE}/blocks/Python/python-plugin.yaml"])
		
		self.modelId = self.createTestModel('apamax.analyticsbuilder.samples.DeviceSimulator', {
			'period': 2.,
			'testData': json.dumps({"a":[1,2,3]}),
		})
		
		self.sendEventStrings(self.correlator,
							  self.timestamp(1),
							  self.timestamp(2),
							  self.timestamp(3),
							  self.timestamp(4),
							  self.timestamp(5),
							  )


	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(errorIgnores=['Unknown dynamicChain', 'CumulocityRestAPIMonitor', 'CumulocityRequestInterface', 'Notifications2Subscriber'])
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
	
		self.assertBlockOutput('value', ['{"a": [1, 2, 3]}','{"a": [1, 2, 3]}'])

