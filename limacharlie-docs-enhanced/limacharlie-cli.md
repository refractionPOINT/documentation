LimaCharlie CLI Extension allows you to issue [LimaCharlie CLI commands](/v2/docs/limacharlie-sdk) using extension requests.

Repo - <https://github.com/refractionPOINT/python-limacharlie>

You may use a  rule to trigger a LimaCharlie CLI event. For example the following rule response actions:

```
- action: extension request
  extension action: run
  extension name: limacharlie-cli
  extension request:
    command_line: '{{ "limacharlie configs push --dry-run --oid" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

Command-line Interface

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.
