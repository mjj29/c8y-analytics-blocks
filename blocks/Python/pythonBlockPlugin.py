import collections
from apama.eplplugin import EPLAction, EPLPluginBase, Event
from RestrictedPython import compile_restricted, Eval, Guards, safe_builtins, limited_builtins, utility_builtins

class Value(object):
	def __init__(self, value, properties, timestamp):
		self.value = value
		self.properties = properties
		self.timestamp = timestamp
		self._guarded_writes = True

	def _asdict(self):
		return {
			"value": self.value,
			"properties": self.properties,
			"timestamp": self.timestamp
		}

class PythonBlockPlugin(EPLPluginBase):
	safe_globals = {
		"__builtins__": {**safe_builtins, **limited_builtins, **utility_builtins,
			"__name__": "restricted_python_block",
			"__metaclass__": type,
			"_getiter_": Eval.default_guarded_getiter,
			"_getitem_": Eval.default_guarded_getitem,
			"_iter_unpack_sequence": Guards.guarded_iter_unpack_sequence,
			"Value": Value,
			"_write_": Guards.full_write_guard,
		}
	}

	def __init__(self,init):
		super(PythonBlockPlugin,self).__init__(init)

	@EPLAction("action<> returns chunk")
	def createPythonState(self):
		return dict()

	@EPLAction("action<string> returns chunk")
	def validate(self, expression):
		return compile_restricted(expression, '<inline code>', 'exec')

	@EPLAction("action<chunk, chunk, sequence<apama.analyticsbuilder.Value>> returns sequence<apama.analyticsbuilder.Value>")
	def execute(self, bytecode, state, inputs):
		locals = {
			"generate": True,
			"inputs": [Value(x.fields['value'], x.fields['properties'], x.fields['timestamp']) for x in inputs],
			"outputs": [Value(False, {}, 0.0) for _ in range(5)],
			"logger": self.getLogger(),
			"state": state
		}
		exec(bytecode, PythonBlockPlugin.safe_globals, locals)
		result = [Event("apama.analyticsbuilder.Value", {"value":locals["generate"], "properties":{}, "timestamp": 0.0})]+[Event("apama.analyticsbuilder.Value", x._asdict()) for x in locals["outputs"]]
		return result
