# c8y-analytics-blocks
Custom community supported blocks for Cumulocity Analytics Builder

This repo contains the following blocks

## Python function block
This block has been moved to https://github.com/Cumulocity-IoT/analytics-builder-blocks-contrib
## Smart Function block
This block has been added to the product
## JSON encoder/decoder blocks

These blocks convert between a string value in encoded JSON form, to a decoded value sent in the output properties

## AI Agent block
This block has been added to the product
## ONNX block
This block has been added to the product
## Logger block
This block has been added to the product
## Rate Quash Block
This block has been added to the product as the RateLimiter block
## Property Mapper block

This block will take the input value and properties and allow you to map the fields to the output value and output properties

## Device Simulator block

This block simulates a device producing arbitrary-format data by periodically generating the provided string into the model

## Inbound Device Message block
This block has been moved to https://github.com/Cumulocity-IoT/analytics-builder-blocks-contrib
## Outbound Device Message block

This block sends messages to device connectivity services such as the MQTT service. The block takes the message payload as a base64-encoded string. It requires a Streaming Analytics microservice of at least version 26.263.0.

## Create External Measurement block

This block allows creation of measurements using external device IDs rather than internal Managed Object IDs, and can automatically create devices for missing external IDs.

## Adding custom blocks as extensions

To use these blocks you should install the [Analytics Management](https://github.com/Cumulocity-IoT/cumulocity-analytics-management) plug-in to your Cumulocity environment, and then link it to this repository using the [https://github.com/mjj29/c8y-analytics-blocks/tree/main/blocks/](https://github.com/mjj29/c8y-analytics-blocks/tree/main/blocks/) directory.

This will allow you to select from the blocks in this repository

## Running tests

To run tests you will need an [Apama installation](https://download.cumulocity.com/Apama/) and a copy of the [Apama Analytics Builder Block SDK](https://github.com/Cumulocity-IoT/apama-analytics-builder-block-sdk). Source the apama_env from your Apama installation and export `ANALYTICS_BUILDER_SDK=/location/of/apama-analytics-builder-block-sdk`, then run `pysys run` in the `tests/` directory of this repository.
