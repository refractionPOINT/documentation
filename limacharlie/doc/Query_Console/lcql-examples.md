# LCQL Examples

LimaCharlie Query Language (LCQL) lets you write well-structured queries to search across telemetry within LimaCharlie. The following examples can help you perform targeted searches or hunts across your telemetry, as well as modify them to build your own. Example queries are sorted by *source*, however can be adjusted for your environment.

Got a Unique Query?

If you've written a unique query or have one you'd like to share with the community, please join us in the [LimaCharlie Community](https://community.limacharlie.io)!

## General Queries

Search *all* event types across *all* Windows sytems for a particular string showing up in *any* field.
`-24h | plat == windows | * | event/* contains 'psexec'`

## GitHub Telemetry

GitHub logs can be an excellent source of telemetry to identify potential repository or account abuse or misuse. When ingested properly, GitHub log data can be observed via `plat == github`.

### GitHub Protected Branch Override

Show me all the GitHub branch protection override (force pushing to repo without all approvals) in the past 12h that came from a user outside the United States, with the repo, user and number of infractions.

`-12h | plat == github | protected_branch.policy_override | event/public_repo is false and event/actor_location/country_code is not "us" | event/repo as repo event/actor as actor COUNT(event) as count GROUP BY(repo actor)`

which could result in:

```
| actor    |   count | repo                               |
|----------|---------|------------------------------------|
| mXXXXXXa |      11 | acmeCorpCodeRep/customers          |
| aXXXXXXb |      11 | acmeCorpCodeRep/analysis           |
| cXXXXXXd |       3 | acmeCorpCodeRep/devops             |
```

## Network Telemetry

Network details recorded on endpoints, such as new connections or DNS requests, allow for combined insight. We can also query this data for aggregate details, and display data in an easily-consumed manner.

### Domain Count

Show me all domains resolved by Windows hosts that contain "google" in the last 10 minutes and the number of times each was resolved.

`-10m | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains 'google' | event/DOMAIN_NAME as domain COUNT(event) as count GROUP BY(domain)`

which could result in:

```
|   count | domain                     |
|---------|----------------------------|
|      14 | logging.googleapis.com     |
|      36 | logging-alv.googleapis.com |
```

### Domain Prevalence

Show me all domains resolved by Windows hosts that contain "google" in the last 10 minutes and the number of unique Sensors that have resolved them.

`-10m | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains 'google' | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as count GROUP BY(domain)`

which could result in:

```
|   count | domain                     |
|---------|----------------------------|
|       4 | logging.googleapis.com     |
|       3 | logging-alv.googleapis.com |
```

## Process Activity

### Unsigned Binaries

Grouped and counted.
`-24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/FILE_IS_SIGNED != 1 | event/FILE_PATH as Path event/HASH as Hash event/ORIGINAL_FILE_NAME as OriginalFileName COUNT_UNIQUE(Hash) as Count GROUP BY(Path Hash OriginalFileName)`

### Process Command Line Args

`-1h | plat == windows | NEW_PROCESS EXISTING_PROCESS | event/COMMAND_LINE contains "psexec" | event/FILE_PATH as path event/COMMAND_LINE as cli routing/hostname as host`

### Stack Children by Parent

`-12h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "cmd.exe" | event/PARENT/FILE_PATH as parent event/FILE_PATH as child COUNT_UNIQUE(event) as count GROUP BY(parent child)`

## Windows Event Log (WEL)

When ingested with EDR telemetry, or as a separate Adapter, `WEL` type events are easily searchable via LimaCharlie. Sample queries are organized alphabetically, with threat/technique details provided where applicable.

### %COMSPEC% in Service Path

`-12h | plat == windows | WEL | event/EVENT/System/EventID == "7045" and event/EVENT/EventData/ImagePath contains "COMSPEC"`

### Overpass-the-Hash

`-12h | plat == windows | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/LogonType == "9" and event/EVENT/EventData/AuthenticationPackageName == "Negotiate" and event/EVENT/EventData/LogonProcess == "seclogo"`

### Taskkill from a Non-System Account

*Requires process auditing to be enabled*

`-12h | plat == windows | WEL | event/EVENT/System/EventID == "4688" and event/EVENT/EventData/NewProcessName contains "taskkill" and event/EVENT/EventData/SubjectUserName not ends with "!"`

### Logons by Specific LogonType

`-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" AND event/EVENT/EventData/LogonType == "10"`

### Stack/Count All LogonTypes by User

`-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" | event/EVENT/EventData/LogonType AS LogonType event/EVENT/EventData/TargetUserName as UserName COUNT_UNIQUE(event) as Count GROUP BY(UserName LogonType)`

### Failed Logons

`-1h | plat==windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/IpAddress as SrcIP event/EVENT/EventData/LogonType as LogonType event/EVENT/EventData/TargetUserName as Username event/EVENT/EventData/WorkstationName as SrcHostname`

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Endpoint Detection & Response

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.
