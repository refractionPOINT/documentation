# Testing Outputs

The easiest way to test if the outputs are configured correctly is to set the stream to `Audit` which will send auditing events about activity around the management of the platform in the cloud. You can then edit the same output or make any other change on the platform, which will trigger an audit event to be sent.

After you have confirmed that the output configurations works, you can switch the data stream from `Audit` to the one you are looking to use.

For output delivery errors, check Platform Logs, under Errors, for the key `output/OUTPUT_NAME`. Configuration validation errors are shown in the API or web app response.

If an output fails, it gets disabled temporarily to avoid spam. It will be re-enabled automatically after a while, or you can force it to be re-enabled by updating the configuration.
