# SDK Documentation

Programmatic access to LimaCharlie through the official SDKs.

## Available SDKs

### [Python SDK](python-sdk.md)

The Python SDK gives a complete interface for security automation, data analysis, and rapid prototyping. It also includes the [command line interface](../sdk-overview.md).

```bash
pip install limacharlie
```

- Repo — <https://github.com/refractionPOINT/python-limacharlie>

### [Python SDK v4](python-sdk-v4.md) (Deprecated)

The previous major version of the Python SDK. It is deprecated and will be removed in a future release. It stays available for users that maintain existing v4 integrations. Use the v5 [Python SDK](python-sdk.md) for new code.

```bash
pip install "limacharlie<5"
```

- Repo (v4 branch) — <https://github.com/refractionPOINT/python-limacharlie/tree/v4>

### [Go SDK](go-sdk.md)

The Go SDK is a type-safe client library. Use it to build security automation, integrations, and custom tools.

```bash
go get github.com/refractionPOINT/go-limacharlie/limacharlie
```

- Repo — <https://github.com/refractionPOINT/go-limacharlie>

## Authentication

Both SDKs support multiple authentication methods:

1. **API Key**: Organization-level API key (`oid` + `api_key`)
2. **Environment Variables**: Auto-load from `LC_OID` and `LC_API_KEY`
3. **Config File**: Credentials stored in `~/.limacharlie` with named environments

See the individual SDK pages for detailed authentication examples.

## Resources

- [REST API Documentation](https://api.limacharlie.io/static/swagger/)
- [Community Forum](https://community.limacharlie.com/)
