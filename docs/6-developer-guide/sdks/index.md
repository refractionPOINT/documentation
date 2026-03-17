# SDK Documentation

Programmatic access to LimaCharlie via official SDKs.

## Available SDKs

### [Python SDK](python-sdk.md)

The Python SDK offers a full-featured interface for security automation, data analysis, and rapid prototyping. It also includes the [command line interface](../sdk-overview.md).

```bash
pip install limacharlie
```

* Repo — <https://github.com/refractionPOINT/python-limacharlie>

### [Go SDK](go-sdk.md)

The Go SDK provides a type-safe client library for building security automation, integrations, and custom tools.

```bash
go get github.com/refractionPOINT/go-limacharlie/limacharlie
```

* Repo — <https://github.com/refractionPOINT/go-limacharlie>

## Authentication

Both SDKs support multiple authentication methods:

1. **API Key**: Organization-level API key (`oid` + `api_key`)
2. **Environment Variables**: Auto-load from `LC_OID` and `LC_API_KEY`
3. **Config File**: Credentials stored in `~/.limacharlie` with named environments

See the individual SDK pages for detailed authentication examples.

## Resources

- [REST API Documentation](https://api.limacharlie.io/static/swagger/)
- [Community Slack](https://slack.limacharlie.io)
