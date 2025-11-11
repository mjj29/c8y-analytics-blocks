# c8y-analytics-blocks
Custom community supported blocks for Cumulocity Analytics Builder

This repo contains the following blocks

## Python function block

This block allows function written in a restricted subset of python to be defined in an analytics builder model.

For example:

```python
	import math
	def onInput(inputs, context):
		context.setState("counter", context.getState("counter", 0.) + 1.)
		(a, b) = (inputs[0].value, inputs[1].value)
		if a and b:
			return [
				math.fabs(a - b),
				a - b,
				context.getState("counter"),
				Value(True, {'value1': inputs[0].properties['value1'], 'value2': inputs[1].properties['value2']}),
			]
		else:
			return None
```

## Smart Function block

This block allows JS Smart Functions to be defined in an analytics builder model. It requires a Streaming Analytics microservice of at least version 26.252.0.

For example:

```javascript
export function onInput(inputs, context) {
	console.log("Processing inputs");
	context.setState("counter", context.getState("counter", 0) + 1);
	const [a, b] = [inputs[0].value, inputs[1].value];
	if (a != null && b != null) {
		return [
			Math.abs(a - b),
			a - b,
			context.getState("counter"),
			{value: a - b, properties: { ...inputs[0].properties, ...inputs[1].properties }}
		];
	}
	return null;
}
```

The TypeScript API for Smart Functions can be seen in [SmartFunction.ts](docs/SmartFunction.ts)

## JSON encoder/decoder blocks

These blocks convert between a string value in encoded JSON form, to a decoded value sent in the output properties

## Logger block

This block will take an input and log it to the log file

## Property Mapper block

This block will take the input value and properties and allow you to map the fields to the output value and output properties

## Device Simulator block

This block simulates a device producing arbitrary-format data by periodically generating the provided string into the model

## Inbound Device Message block

This block receives messages from MQTT service. The block outputs a single string containing the payload of the message. It may need to be decoded by a JSON decoder block and/or a Python expression block.

## Create External Measurement block

This block allows creation of measurements using external device IDs rather than internal Managed Object IDs, and can automatically create devices for missing external IDs.

## Adding custom blocks as extensions

To use these blocks you should install the [Analytics Management](https://github.com/Cumulocity-IoT/cumulocity-analytics-management) plug-in to your Cumulocity environment, and then link it to this repository using the [https://github.com/mjj29/c8y-analytics-blocks/tree/main/blocks/](https://github.com/mjj29/c8y-analytics-blocks/tree/main/blocks/) directory.

This will allow you to select from the blocks in this repository

## Running tests

To run tests you will need an [Apama installation](https://download.cumulocity.com/Apama/) and a copy of the [Apama Analytics Builder Block SDK](https://github.com/Cumulocity-IoT/apama-analytics-builder-block-sdk). Source the apama_env from your Apama installation and export `ANALYTICS_BUILDER_SDK=/location/of/apama-analytics-builder-block-sdk`, then run `pysys run` in the `tests/` directory of this repository.
