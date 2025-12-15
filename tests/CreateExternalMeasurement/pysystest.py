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
		self._injectEPLOnce(corr, [self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['Base64']])  
		self._injectEPLOnce(corr, [self.project.testRootDir+'/utils/DeviceServiceMock.mon'])
		self._injectEPLOnce(corr, [self.project.testRootDir+'/utils/ExternalMeasurementMock.mon'])

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/', arguments=["--config", f"{self.project.SOURCE}/blocks/ONNX/","--config", f"{self.project.SOURCE}/blocks/Python/"])
		
		self.modelId = self.createTestModel('apamax.analyticsbuilder.samples.CreateExternalMeasurement', {
			'externalIdType': 'c8y_Serial',
			'createMissingDevice': True,
		}, id="model1")
		
		self.sendEventStrings(self.correlator,
								self.timestamp(1),
								self.inputEvent('measurement', 10., id=self.modelId, properties={
									'type':'c8y_Temperature',
									'fragment':'c8y_Temperature',
									'series':'temp',
									'externalId':'ABC123456'
								}),
								self.timestamp(2),
								self.inputEvent('measurement', 12., id=self.modelId, properties={
									'type':'c8y_Temperature',
									'fragment':'c8y_Temperature',
									'series':'temp',
									'externalId':'ABC123456'
								}),
								self.timestamp(3),
								)

	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(errorIgnores=['Unknown dynamicChain', 'CumulocityRestAPIMonitor', 'CumulocityRequestInterface', 'Notifications2Subscriber'])
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')

	
