#
#  Copyright (c) 2019-present Cumulocity GmbH, Duesseldorf, Germany and/or its affiliates and/or their licensors.
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

__pysys_title__ = r'JSON Encoder/Decoder: to check the basic working of the block'
__pysys_purpose__ = r''

import json
from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def preInjectBlock(self, corr):                                    
		self._injectEPLOnce(corr, [self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['TolerateAPI', 'cumulocity/Cumulocity_Rest_API', 'Notifications2.0Events', 'Notifications2.0Subscriptions', 'MQTTServiceEvents']])  
		self._injectEPLOnce(corr, [self.project.testRootDir+'/utils/MQTTServiceMock.mon'])

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/', arguments=["--config", f"{self.project.SOURCE}/blocks/Python/plugin.yaml"])
		
		self.encoderModel = self.createTestModel('apamax.analyticsbuilder.samples.JSONEncoder', {	})
		self.decoderModel = self.createTestModel('apamax.analyticsbuilder.samples.JSONDecoder', {	})
		self.object = {'foo':3.14, 'bar':[42, 666]}
		self.json = json.dumps(self.object)
		
		self.sendEventStrings(self.correlator,
							  self.timestamp(1),
							  self.inputEvent('json', True, id = self.encoderModel, properties=self.object),
							  self.timestamp(2),
							  self.inputEvent('string', self.json, id = self.decoderModel),
							  self.timestamp(3),
							  )


	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(errorIgnores=['Unknown dynamicChain', 'CumulocityRestAPIMonitor', 'CumulocityRequestInterface', 'Notifications2Subscriber'])
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.decoderModel + '\" with PRODUCTION mode has started')
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.encoderModel + '\" with PRODUCTION mode has started')
	
		# Verify the decoder produces the expected output
		decoderOutput = self.allOutputFromBlock(self.decoderModel)
		self.assertThat("properties == expectedProperties", properties=decoderOutput[0]['properties'], expectedProperties=self.object)
		self.assertThat("value == True", value=decoderOutput[0]['value'])

		# Verify the encoder produces the expected output
		encoderOutput = self.allOutputFromBlock(self.encoderModel)
		parsedOutput = json.loads(encoderOutput[0]['value'])
		self.assertThat("parsedOutput == expectedOutput", parsedOutput=parsedOutput, expectedOutput=self.object)
