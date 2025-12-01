from apama.eplplugin import EPLAction, EPLPluginBase, Event
import onnxruntime as ort
import numpy as np
import json

class ONNXBlockPlugin(EPLPluginBase):

	def __init__(self,init):
		super(ONNXBlockPlugin,self).__init__(init)

	@EPLAction("action<string> returns chunk")
	def initState(self, modelFile):
		if ".." in modelFile:
			raise Exception("Invalid model filename")
		session = ort.InferenceSession(self.getConfig()["MODEL_DIR"] + "/" + modelFile)
		outputs = session.get_outputs()
		return {
			"session": session,
			"input_info": session.get_inputs(),
			"output_names": [out.name for out in outputs]
		}

	@EPLAction("action<chunk, sequence<any>> returns sequence<any>")
	def execute(self, state, inputs):

		for i in range(len(state["input_info"])):
			# not all required inputs provided yet
			if not inputs[i]: return []

		feed = {}
		for i in range(len(state["input_info"])):
			py = inputs[i]
			if isinstance(py, bool):
				np_array = np.array([py], dtype=np.bool_)
			elif isinstance(py, int):
				np_array = np.array([py], dtype=np.int64)
			elif isinstance(py, float):
				np_array = np.array([py], dtype=np.float32)
			elif isinstance(py, str):
				# deserialize JSON string from py to numpy array
				py_list = json.loads(py)
				np_array = np.array(py_list, dtype=np.float32)
			else:
				raise Exception(f"Unsupported input type: {type(py)}")
			feed[state["input_info"][i].name] = np_array

		result = state["session"].run(state["output_names"], feed)

		return [arr[0].item() for arr in result]

