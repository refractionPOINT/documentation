# Adapter Deployment

Adapters can be deployed in one of two ways:

- **On-prem**, Adapters utilize the LC Adapter binary to ingest a data source and forward it to LimaCharlie.
- **Cloud-to-cloud**, connects the LimaCharlie cloud directly with your cloud source and automatically ingests data.

Which Adapter Do I Use for Cloud Data?

You can use on-prem adapters to forward cloud data, or you could acquire the same data with a cloud-to-cloud connection. So, which one to use?

The answer lies in _how_ you want to send your data to LimaCharlie. Are you OK with configuring a connector from our platform, or would you rather use a bastion box in between? Either way works for us!

The data ingested from adapters is parsed/mapped into JSON by LimaCharlie, according to the parameters you provided, unless using a pre-defined format.

## Adapter Binaries

Software-based, or "on-prem" adapters are available in the following formats:

### POSIX-compliant

- [AIX ppc64](https://downloads.limacharlie.io/adapter/aix/ppc64)
- [Linux (Generic) 64-bit](https://downloads.limacharlie.io/adapter/linux/64)
- [Linux (Generic) arm](https://downloads.limacharlie.io/adapter/linux/arm)
- [Linux (Generic) arm64](https://downloads.limacharlie.io/adapter/linux/arm64)
- [FreeBSD 64-bit](https://downloads.limacharlie.io/adapter/freebsd/64)
- [OpenBSD 64-bit](https://downloads.limacharlie.io/adapter/openbsd/64)
- [NetBSD 64-bit](https://downloads.limacharlie.io/adapter/netbsd/64)
- [Solaris 64-bit](https://downloads.limacharlie.io/adapter/solaris/64)

### macOS

- [macOS x64](https://downloads.limacharlie.io/adapter/mac/64)
- [macOS arm64](https://downloads.limacharlie.io/adapter/mac/arm64)

### Windows

- [Windows x64](https://downloads.limacharlie.io/adapter/windows/64): Windows 10 or Windows Server 2016 and later.
- [Windows x64 (legacy)](https://downloads.limacharlie.io/adapter/windows/legacy64): Windows 7 SP1 and Windows Server 2008 R2, best-effort.

!!! note "Windows 7 and Windows Server 2008 R2"
    The standard Windows adapter is built with a current Go release, and Go supports Windows 10 and Windows Server 2016 or later only. The legacy build is the same adapter, built with [go-legacy-win7](https://github.com/thongtech/go-legacy-win7), a community fork of Go that tracks upstream releases and restores Windows 7 support. It is not maintained by the Go team, so it is provided on a best-effort basis. Windows Server 2008 (not R2) is not supported by either build.

    Microsoft no longer ships security updates for these Windows versions. Where possible, forward their event logs to a supported host, for example with Windows Event Forwarding, and run the standard adapter there.

### Docker

- <https://hub.docker.com/r/refractionpoint/lc-adapter>

Another platform?

If you need support for a specific platform, or require more information about supported platforms, please [let us know](https://www.limacharlie.io/contact).

## On-Prem + Cloud Management

An on-prem adapter can read its configuration from LimaCharlie instead of a local file. You keep the configuration in an External Adapter record, start the adapter with only your Organization ID and the record's GUID, and change it later from the web app, CLI or Infrastructure as Code. The adapter applies a change within about a minute, without anyone logging in to the host.

```bash
./lc_adapter cloud conf_guid=<RECORD GUID> oid=<ORG ID>
```

See [Cloud-Managed Adapters](cloud-managed.md) for when to use it, how to set it up and how to keep the GUID safe.
