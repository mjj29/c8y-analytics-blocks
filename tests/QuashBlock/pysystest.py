#
#  Copyright (c) 2019-present Cumulocity GmbH, Duesseldorf, Germany and/or its affiliates and/or their licensors.
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

__pysys_title__ = r'Rate Quash block: to check the basic working of the block'
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
		
		self.modelId = self.createTestModel('apamax.analyticsbuilder.samples.QuashMessages', { "period": "2.0" })
		
		self.sendEventStrings(self.correlator,
							  self.timestamp(11),
							  self.inputEvent('input', 42, id = self.modelId),
							  self.timestamp(12),
							  self.inputEvent('input', 666, id = self.modelId),
							  self.timestamp(12.5),
							  self.inputEvent('input', 3.14, id = self.modelId),
							  self.timestamp(13.5),
							  self.inputEvent('input', 2.76, id = self.modelId),
							  self.timestamp(14),
							  )


	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(errorIgnores=['Unknown dynamicChain', 'CumulocityRestAPIMonitor', 'CumulocityRequestInterface', 'Notifications2Subscriber'])
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')

		self.assertBlockOutput('output', [42, 2.76])
		self.assertBlockOutput('squashed', [666, 3.14])
		self.assertBlockOutput('squashedCount', [1, 2])
