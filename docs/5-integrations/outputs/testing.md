# Testing Outputs

To test if an output is configured correctly, set the stream to `Audit`. This stream sends audit events about the management of the platform in the cloud. Then edit the same output, or make another change on the platform. The change triggers an audit event.

After you confirm that the output configuration works, change the data stream from `Audit` to the stream that you want to use.

If an error occurs when you configure an output, the error details are in the Platform Logs section under Errors. The key looks like `outputs/OUTPUT_NAME`.

If an output fails, the cloud disables it temporarily to stop spam. The cloud enables the output again after some time. You can also update the configuration to enable the output again.
