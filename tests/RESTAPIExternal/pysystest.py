#
#  Copyright (c) 2019-present Cumulocity GmbH, Duesseldorf, Germany and/or its affiliates and/or their licensors.
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

__pysys_title__ = r'REST API: check against external servers'
__pysys_purpose__ = r''

import json
from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def preInjectBlock(self, corr):
		self._injectEPLOnce(corr, [self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['TolerateAPI', 'cumulocity/Cumulocity_Rest_API', 'Notifications2.0Events', 'Notifications2.0Subscriptions', 'MQTTServiceEvents', 'MQTTServiceSubscription', 'MQTTServiceEvents']])  

	def execute(self):

		self.skipTest("Manual verification only")
		
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/', arguments=["--config", f"{self.project.SOURCE}/blocks/Python/plugin.yaml"])
		
		self.weatherModel = self.createTestModel('apamax.analyticsbuilder.samples.RESTAPI', {
			'period': 2.,
			'httpMethod': 'GET',
			'URI': 'http://api.open-meteo.com/v1/forecast?latitude=35.6895&longitude=139.6917&current_weather=true&hourly=cloud_cover_low,cloud_cover_mid,cloud_cover_high&daily=sunshine_duration&timezone=Europe%2FLondon&forecast_days=2',
			'authMethod': 'NONE'
		})
		self.octopusModel = self.createTestModel('apamax.analyticsbuilder.samples.RESTAPI', {
			'httpMethod': 'GET',
			'period': 2.,
			'URI': 'https://api.octopus.energy/v1/products/AGILE-24-10-01/',
			'authMethod': 'NONE'
		})
		self.myEnergiModel = self.createTestModel('apamax.analyticsbuilder.samples.RESTAPI', {
			'httpMethod': 'GET',
			'period': 2.,
			'URI': 'https://s18.myenergi.net/cgi-jstatus-Z',
			'authMethod': 'HTTP_DIGEST',
			'username': '',
			'password': '',
		})
		self.sunsynkModel = self.createTestModel('apamax.analyticsbuilder.samples.RESTAPI', {
			'period': 2.,
			'httpMethod': 'GET',
			'URI': 'https://api.sunsynk.net/api/v1/inverter/battery/2208309020/realtime?sn=2208309020&lan=en',
			'authMethod': 'BEARER',
		})
		self.sunsynkTokenModel = self.createTestModel('apamax.analyticsbuilder.samples.RESTAPI', {
			'period': 2.,
			'httpMethod': 'POST',
			'URI': 'https://api.sunsynk.net/oauth/token',
			'authMethod': 'NONE',
		})

		self.sendEventStrings(self.correlator,
							  self.inputEvent('pass', 							'', id=self.sunsynkModel),
							  self.inputEvent('body', '{"username":"", "password":"", "grant_type":"password", "client_id":"csp-web", "areaCode":"sunsynk","source":"sunsynk"}', id=self.sunsynkTokenModel),
							  self.timestamp(2),
							  self.timestamp(3),
							  )
		self.wait(5)

	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(errorIgnores=['Unknown dynamicChain', 'CumulocityRestAPIMonitor', 'CumulocityRequestInterface', 'Notifications2Subscriber'])
		
