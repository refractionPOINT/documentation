# Adapters Release Notes

Release notes for the adapters that bring third-party telemetry into LimaCharlie. For the latest releases of every component, see the [release notes overview](index.md).

!!! tip "Subscribe"
    Get each release as it ships with the [Adapters RSS feed](https://docs.limacharlie.io/10-release-notes/adapters.xml).

## 2026-10-28

### Adapters 1.32.51

#### New Features

- New Windows build for Windows 7 SP1 and Windows Server 2008 R2 (x64), available at [https://downloads.limacharlie.io/adapter/windows/legacy64](https://downloads.limacharlie.io/adapter/windows/legacy64). The standard Windows adapter requires Windows 10 or Windows Server 2016 or later, because current Go releases no longer run on older Windows. The legacy build is the same adapter, built with a community fork of Go that restores Windows 7 support, and is provided on a best-effort basis. See [Adapter Deployment](../2-sensors-deployment/adapters/deployment.md#windows).

---

## 2026-10-27

### Adapters 1.32.50

#### Improvements

- Adapter logs no longer flood the host when a connection keeps failing, for example on a TLS error or an unreachable API. The first occurrence of a message is printed as before. Repeats within a minute are folded into one `last message repeated N more time(s)` line carrying the latest text. Each level is rate limited per adapter, and every line held back is counted and reported, so no error goes unseen. Set the environment variable `USP_LOG_NO_DEDUP=1` to print every line unchanged.
- Syslog over TLS: a sender failing the TLS handshake is reported once per connection as `tls handshake with <address> failed`, naming the sender. A client that connects but never completes the handshake is dropped after 30 seconds. Load balancer and probe health checks that connect and close are not reported.
- Slack, Cato and Google Cloud Pub/Sub adapters now wait longer after each consecutive failure, up to 5 minutes, instead of retrying every few seconds.

#### Bug Fixes

- Slack: the adapter no longer stops when the API is unreachable, and a failed page no longer skips the pages after it. A page that keeps failing is retried from where it stopped, then given up on after 5 attempts with an error.
- Cato: the adapter no longer exits after 11 failed requests, no longer crashes when a query keeps failing, and stops promptly when closed.
- Okta: the adapter follows every page of results and keeps its place through retries and rate limits.
- Microsoft Defender, Entra ID and Azure Event Hubs: collection keeps making progress through vendor retries and paginated results instead of stalling or skipping pages.

---

## 2025-07-10

### LC Adapters v1.30.11

Integration with Cylance, Proofpoint Tap, and Wiz. Big and special thanks to community contributors [shortstack](https://github.com/shortstack) and RagingRedRiot.

!!! note
    These adapters are supported in the downloadable Adapter, but not yet rolled out to the web app as "cloud adapter."

---

## 2025-05-08

### LC Adapter v1.30.1

Adding Sublime adapter. Audit logs from Sublime can be ingested cloud-to-cloud via the API.

---

## 2025-03-28

### Adapters

SentinelOne adapter: connects to SentinelOne MGMT API and sends alerts, threats, and other events of interest to LimaCharlie.

---

## 2025-03-06

### Adapter v1.27.2

Added support for ZenDesk.
