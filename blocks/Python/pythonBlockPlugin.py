import collections, json, types, os, subprocess, importlib
import http.client
from apama.eplplugin import EPLAction, EPLPluginBase, Event
from RestrictedPython import compile_restricted, Eval, Guards, safe_builtins, limited_builtins, utility_builtins

class Context(object):
	def __init__(self, logger, state, blockParameters):
		self.logger = logger
		self._state = state
		self.blockParameters = [blockParameters['param1'], blockParameters['param2'], blockParameters['param3'], blockParameters['param4'], blockParameters['param5']]

	def getState(self, key, default=None):
		if key not in self._state:
			self._state[key] = default
		return self._state[key]

	def setState(self, key, value):
		self._state[key] = value

	def hasState(self, key):
		return key in self._state


class Value(object):
	def __init__(self, value, properties={}, timestamp=0.0):
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

	safe_modules = {
		"math": __import__("math"),
		"functools": __import__("functools"),
		"itertools": __import__("itertools"),
		"copy": __import__("copy"),
		"cmath": __import__("cmath"),
		"decimal": __import__("decimal"),
		"fractions": __import__("fractions"),
		"numbers": __import__("numbers"),
		"operator": __import__("operator"),
		"collections": __import__("collections"),
		"heapq": __import__("heapq"),
		"bisect": __import__("bisect"),
		"statistics": __import__("statistics"),
		"array": __import__("array"),
		"enum": __import__("enum"),
		"typing": __import__("typing"),
		"dataclasses": __import__("dataclasses"),
		"string": __import__("string"),
		"re": __import__("re"),
		"textwrap": __import__("textwrap"),
		"difflib": __import__("difflib"),
		"unicodedata": __import__("unicodedata"),
		"base64": __import__("base64"),
		"binascii": __import__("binascii"),
		"hashlib": __import__("hashlib"),
		"hmac": __import__("hmac"),
		"json": __import__("json"),
		"time": __import__("time"),
		"calendar": __import__("calendar"),
		"uuid": __import__("uuid"),
		"random": __import__("random"),
		"secrets": __import__("secrets"),
		"json": types.SimpleNamespace(loads=json.loads, dumps=json.dumps, JSONDecodeError=json.JSONDecodeError),
		"csv": __import__("csv"),
	}

	@staticmethod
	def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
		if name in PythonBlockPlugin.safe_modules:
			return PythonBlockPlugin.safe_modules[name]
		raise ImportError(f"Import of module '{name}' is not allowed in restricted python block")

	def install_requirements(self, requirements, requirementsDir, packages):
		os.makedirs(requirementsDir, exist_ok=True)
		with open(os.path.join(requirementsDir, "requirements.txt"), "w") as reqFile:
			reqFile.write(requirements)
		self.getLogger().info(f"Installing requirements for python function block")
		self.getLogger().debug(f"Requirements:\n{requirements}")
		try:
			subprocess.check_call(["/usr/bin/env", "python3", "-m", "pip", "install", "--target", requirementsDir, "-r", os.path.join(requirementsDir, "requirements.txt")], timeout=120)
		except Exception as e:
			self.getLogger().error(f"Failed to install package requirements: {e}")
		self.getLogger().info(f"Permitting additional packages for python function block: {packages}")
		importlib.invalidate_caches()
		for package in packages.strip().split(" "):
			package = package.strip()
			if not package:
				continue
			PythonBlockPlugin.safe_modules[package] = __import__(package)

	def __init__(self,init):
		super(PythonBlockPlugin,self).__init__(init)
		self.install_requirements(self.getConfig().get("requirements"), self.getConfig().get("requirementsDir"), self.getConfig().get("packages"))

	@EPLAction("action<> returns chunk")
	def createPythonState(self):
		return dict()

	@EPLAction("action<string> returns chunk")
	def validate(self, expression):
		bytecode = compile_restricted(expression, '<inline code>', 'exec')
		globals = dict(PythonBlockPlugin.safe_globals)
		exec(bytecode, globals)
		onInput = globals.get("onInput", None)
		if not callable(onInput):
			raise Exception("The provided code does not define a callable onInput function")
		return (onInput, globals)

	@EPLAction("action<chunk, chunk, apamax.analyticsbuilder.samples.Python_$Parameters, sequence<apama.analyticsbuilder.Value>> returns sequence<apama.analyticsbuilder.Value>")
	def execute(self, code, state, properties, inputs):
		(onInput, globals) = code
		result = onInput([Value(x.fields['value'], x.fields['properties'], x.fields['timestamp']) for x in inputs], Context(self.getLogger(), state, properties.fields))
		if result is None:
			return []
		else:
			return [Event("apama.analyticsbuilder.Value", x._asdict() if isinstance(x, Value) else {"value":x, "properties":{}, "timestamp":0.0}) for x in result]

PythonBlockPlugin.safe_globals = {
		"__builtins__": {**safe_builtins, **limited_builtins, **utility_builtins,
			"__name__": "restricted_python_block",
			"__metaclass__": type,
			"_getiter_": Eval.default_guarded_getiter,
			"_getitem_": Eval.default_guarded_getitem,
			"_iter_unpack_sequence": Guards.guarded_iter_unpack_sequence,
			"_unpack_sequence_": Guards.guarded_unpack_sequence,
			"Value": Value,
			"_write_": Guards.full_write_guard,
			"__import__": PythonBlockPlugin.safe_import,
		}
	}

