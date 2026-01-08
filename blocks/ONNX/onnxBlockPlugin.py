from apama.eplplugin import EPLAction, EPLPluginBase, Event
import json

class ONNXBlockPlugin(EPLPluginBase):

	def __init__(self,init):
		super(ONNXBlockPlugin,self).__init__(init)

	@EPLAction("action<string> returns string")
	def downloadModel(self, modelFile):
		import requests, os, zipfile

		if ".." in modelFile:
			raise Exception("Invalid model filename")

		if modelFile.endswith(".onnx"):
			onnx_name = modelFile
			zip_name = modelFile.replace(".onnx", ".zip")
		elif modelFile.endswith(".zip"):
			zip_name = modelFile
			onnx_name = modelFile.replace(".zip", ".onnx")
		else:
			zip_name = f"{modelFile}.zip"
			onnx_name = f"{modelFile}.onnx"

		if os.path.exists(os.path.join(self.getConfig()["MODEL_DIR"], onnx_name)):
			self.getLogger().info(f"Loading model {onnx_name} from local MODEL_DIR")
			# Model file exists locally, load directly
			onnx_path = os.path.join(self.getConfig()["MODEL_DIR"], onnx_name)
			return onnx_path
		else:
			self.getLogger().info(f"Model {onnx_name} not found locally, attempting to download from Cumulocity")

			# prepare Cumulocity API
			base_url = os.environ["C8Y_BASEURL"].rstrip("/")
			auth = (os.environ["C8Y_TENANT"]+"/"+os.environ["C8Y_USER"], os.environ["C8Y_PASSWORD"])

			# 1. Find the managed object with name = zip_name
			search_url = f"{base_url}/inventory/managedObjects?query=name eq '{zip_name}'"
			r = requests.get(search_url, auth=auth)
			r.raise_for_status()
			data = r.json()
			if "managedObjects" not in data or not data["managedObjects"]:
				raise Exception(f"Managed object {zip_name} not found in Cumulocity")
			mo = data["managedObjects"][0]
			mo_id = mo["id"]

			# 2. Download the binary
			bin_url = f"{base_url}/inventory/binaries/{mo_id}"
			r = requests.get(bin_url, auth=auth, stream=True)
			r.raise_for_status()

			# 3. Extract to unique temp folder inside MODEL_DIR
			model_dir = self.getConfig()["MODEL_DIR"]
			tmp_folder = model_dir+"/"+os.environ["C8Y_TENANT"]+"_"+modelFile.replace(".", "_")
			os.makedirs(tmp_folder, exist_ok=True)
			zip_path = os.path.join(tmp_folder, zip_name)
			with open(zip_path, "wb") as f:
				for chunk in r.iter_content(chunk_size=8192):
						f.write(chunk)

			with zipfile.ZipFile(zip_path, "r") as z:
				z.extractall(tmp_folder)

			# 4. Verify the main .onnx exists
			onnx_path = os.path.join(tmp_folder, onnx_name)
			if not os.path.exists(onnx_path):
				raise Exception(f"{onnx_name} not found inside downloaded zip")
			return onnx_path


	@EPLAction("action<string> returns chunk")
	def initState(self, modelPath):
		import onnxruntime as ort
		import numpy as np
		# 5. Load ONNX runtime session
		session = ort.InferenceSession(modelPath)
		outputs = session.get_outputs()

		return {
			"session": session,
			"input_info": session.get_inputs(),
			"output_names": [out.name for out in outputs]
		}

	@EPLAction("action<chunk, sequence<any>> returns sequence<any>")
	def execute(self, state, inputs):
		import onnxruntime as ort
		import numpy as np

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

