# CLI Extension

The `limacharlie-cli` extension allows you to run [LimaCharlie CLI commands](sdk-overview.md#command-line-interface) from within D&R rule response actions. This is useful for automating infrastructure changes (syncing configs, managing rules, etc.) in response to detections.

!!! note
    This page documents the `limacharlie-cli` **extension** for use in D&R rules. For the CLI tool itself, see the [Command Line Interface](sdk-overview.md#command-line-interface) section of the SDK Overview.

## Usage

Trigger a CLI command as a D&R rule response action using `extension request`:

```yaml
- action: extension request
  extension action: run
  extension name: limacharlie-cli
  extension request:
    command_line: '{{ "limacharlie sync push --dry-run --oid YOUR_OID --config /path/to/config.yaml" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

Field descriptions:

* `command_line`: the full CLI command to execute.
* `credentials`: a reference to stored credentials in the [secrets manager](../7-administration/access/secrets.md), used to authenticate the CLI command.
