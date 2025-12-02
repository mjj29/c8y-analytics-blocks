#!/usr/bin/env python3
import onnx
from onnx import helper, TensorProto

def generate_add_model(path):
    x = helper.make_tensor_value_info("x", TensorProto.FLOAT, [1])
    y = helper.make_tensor_value_info("y", TensorProto.FLOAT, [1])
    z = helper.make_tensor_value_info("z", TensorProto.FLOAT, [1])

    node = helper.make_node("Add", ["x", "y"], ["z"])
    graph = helper.make_graph([node], "add_graph", [x, y], [z])

    model = helper.make_model(
        graph,
        producer_name="demo",
        opset_imports=[helper.make_opsetid("", 11)]
    )

    # force IR to something supported by your runtime
    model.ir_version = 6   # IR version used around opset 11

    onnx.save(model, path)


generate_add_model("add.onnx")
