# c8y-analytics-blocks
Custom community supported blocks for Cumulocity Analytics Builder

This repo contains the following blocks

## Python expression block

This block allows expressions written in a restricted subset of python to be defined in an analytics builder model.

## Adding custom blocks as extensions

To use these blocks you should install the [Analytics Management](https://github.com/Cumulocity-IoT/cumulocity-analytics-management) plug-in to your Cumulocity environment, and then link it to this repository using the [https://github.com/mjj29/c8y-analytics-blocks/tree/main/blocks/](https://github.com/mjj29/c8y-analytics-blocks/tree/main/blocks/) directory.

This will allow you to select from the blocks in this repository

## Running tests

To run tests you will need an [Apama installation](https://download.cumulocity.com/Apama/) and a copy of the [Apama Analytics Builder Block SDK](https://github.com/Cumulocity-IoT/apama-analytics-builder-block-sdk). Source the apama_env from your Apama installation and export `ANALYTICS_BUILDER_SDK=/location/of/apama-analytics-builder-block-sdk`, then run `pysys run` in the `tests/` directory of this repository.
