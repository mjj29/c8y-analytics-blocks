/** Context provided to Smart Functions running in Streaming Analytics */
export interface StreamingAnalyticsContext
{
	/** Indicates that this is running in Streaming Analytics */
	readonly runtime: "streaming-analytics";
	/** Get state. State is partitioned to the model partition and is not shared between partitions. */
	getState(key: string, defaultValue?: any): any;

	/** Set state. State is partitioned to the model partition and is not shared between partitions. */
	setState(key: string, value: any): void;

	/** The parameters configured for this block, which may be templated. */
	readonly blockParameters: { [key: string]: any };
}

/** The input and output schema for Streaming Analytics Smart Functions. */
export interface BlockValue
{
	/** The main value of this input. */
	value: string | number | boolean;
	/** Additional properties associated with this input. */
	properties: { [key: string]: any };
}

/** Outputs may either by BlockValues or primitive types. */
export type BlockValueOrPrimitive = BlockValue | string | number | boolean;

declare global {
	/** Smart functions running in Streaming Analytics must implement this function. */
	export function onInput(inputs: BlockValue[], context: StreamingAnalyticsContext): BlockValueOrPrimitive[] | Promise<BlockValueOrPrimitive[]>;
}
