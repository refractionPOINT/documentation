# LimaCharlie CLI

LimaCharlie CLI Extension allows you to issue [LimaCharlie CLI commands](sdk-overview.md) using extension requests.

Repo - <https://github.com/refractionPOINT/python-limacharlie>

You may use a rule to trigger a LimaCharlie CLI event. For example the following rule response actions:

```yaml
- action: extension request
  extension action: run
  extension name: limacharlie-cli
  extension request:
    command_line: '{{ "limacharlie configs push --dry-run --oid" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```
