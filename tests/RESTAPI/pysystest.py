#
#  Copyright (c) 2019-present Cumulocity GmbH, Duesseldorf, Germany and/or its affiliates and/or their licensors.
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

__pysys_title__ = r'REST API: to check the basic working of the block'
__pysys_purpose__ = r''

import json
from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import time
from contextlib import contextmanager

class PySysTest(AnalyticsBuilderBaseTest):

	class SimpleHandler(BaseHTTPRequestHandler):
		def do_GET(self):
			self.send_response(200)
			self.send_header('Content-type', 'application/json')
			self.end_headers()
			response = json.dumps({"a": [1, 2, 3]})
			self.wfile.write(response.encode('utf-8'))

	@contextmanager
	def start_http_server(self, handler_class, port):
		httpd = HTTPServer(('localhost', port), handler_class)
		thread = threading.Thread(target=httpd.serve_forever)
		thread.daemon = True
		thread.start()
		try:
			yield httpd
		finally:
			httpd.shutdown()
			thread.join()

	def preInjectBlock(self, corr):
		self._injectEPLOnce(corr, [self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['TolerateAPI', 'cumulocity/Cumulocity_Rest_API', 'Notifications2.0Events', 'Notifications2.0Subscriptions', 'MQTTServiceEvents', 'MQTTServiceSubscription', 'MQTTServiceEvents']])  

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/', arguments=["--config", f"{self.project.SOURCE}/blocks/Python/plugin.yaml"])
		
		self.modelId = self.createTestModel('apamax.analyticsbuilder.samples.RESTAPI', {
			'period': 2.,
			'URI': 'http://localhost:8080/foo/bar',
			'authMethod': 'NONE'
		})

		with self.start_http_server(PySysTest.SimpleHandler, 8080) as server:
			self.log.info("HTTP server started at http://localhost:8080")
		
			self.sendEventStrings(self.correlator,
								  self.timestamp(2),
								  self.timestamp(3),
								  )

	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(errorIgnores=['Unknown dynamicChain', 'CumulocityRestAPIMonitor', 'CumulocityRequestInterface', 'Notifications2Subscriber'])
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
	
		output = self.allOutputFromBlock(self.modelId)
		print(str(output))
		self.validateOutput(output, 'value', 200, {"a": [1, 2, 3]})

	def validateOutput(self, output, outputId, value, properties):
		for o in output:
			if o['outputId'] == outputId:
				self.assertThat("value == expected", value=o['value'], expected=value)
				self.assertThat("properties == expected", properties=o['properties'], expected=properties)
				return
		self.abort(BLOCKED, "Output not found for outputId: " + outputId)
