# CLI Extension

The `limacharlie-cli` extension lets you run [LimaCharlie CLI commands](sdk-overview.md) from D&R rule response actions. Use it to automate changes to your infrastructure in response to detections, for example to sync configurations or to manage rules.

!!! note
    This page documents the `limacharlie-cli` **extension** for use in D&R rules. For the CLI tool itself, see the [Command Line Interface](sdk-overview.md) page.

## Usage

To trigger a CLI command as a D&R rule response action, use `extension request`:

```yaml
- action: extension request
  extension action: run
  extension name: limacharlie-cli
  extension request:
    command_line: '{{ "limacharlie sync push --dry-run --oid YOUR_OID --config /path/to/config.yaml" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

Field descriptions:

- `command_line`: the full CLI command to run.
- `credentials`: a reference to credentials that are stored in the [secrets manager](../7-administration/config-hive/secrets.md). The CLI command uses them to authenticate.
