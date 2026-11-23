# Testing Outputs

The easiest way to test if the outputs are configured correctly is to set the stream to `Audit` which will send auditing events about activity around the management of the platform in the cloud. You can then edit the same output or make any other change on the platform, which will trigger an audit event to be sent.

After you have confirmed that the output configurations works, you can switch the data stream from `Audit` to the one you are looking to use.

If you are running into an error configuring an output, the error details will be listed in the Platform Logs section under Errors, with the key that looks like `output/OUTPUT_NAME`.

If an output fails, it gets disabled temporarily to avoid spam. Records that arrive while it is disabled are dropped. LimaCharlie retries it at the next configuration refresh, normally within about an hour. Changing its configuration can bring it back sooner, once the change takes effect. See [Output Delivery Guarantees](delivery.md) for what happens on a failure.
