# Extended data retention

Every organization keeps its telemetry searchable for 12 months by default. Extended retention lets you raise that to 18, 24 or 36 months for an organization. Older data stays searchable the same way recent data does, in the Timeline, in Search (LCQL), and in the detection and audit views. There is no archive to restore from.

It is a setting on each organization, with four values: 12 (the default), 18, 24 or 36 months.

## What it covers

| Extended to the period you choose | Stays at 12 months |
| --- | --- |
| Telemetry events | [Artifacts](../5-integrations/extensions/limacharlie/artifact.md) |
| Detections | The object search that answers "where have I seen this indicator" |
| Audit logs | Usage and summary charts, such as the event type breakdown and the traffic charts |

To keep artifacts longer than a year, send the artifact stream to an [Output](../5-integrations/outputs/index.md) as the files arrive.

## Searching older data

A single search covers at most 1 year. To look at data from 20 months ago, search that period on its own, one year at a time. For example, to cover the last 24 months, run one search for the most recent 12 months and a second for the 12 months before that.

## Sensors you deleted

Data from a deleted sensor stays searchable until it ages out. Whether a search finds it depends on how you select sensors:

- An org-wide search with no sensor selector returns the deleted sensor's data.
- A query for a specific sensor ID returns it too.
- A search that selects by tag or platform does not include deleted sensors.

## Pricing

Extended retention needs a paid plan. It is billed per GB-month of data kept beyond the first 12 months. LimaCharlie measures the amount of extended data every day and adds it up on your monthly invoice. Data inside the first 12 months costs nothing extra, as before. See the [pricing page](https://limacharlie.io/pricing) for the current rate.

## Changing the setting

You need both the `org.conf.set` and `billing.ctrl` permissions to change the retention period. `org.conf.set` alone is not enough. See [Permissions](../8-reference/permissions.md).

**Raising it** applies immediately. From that moment, data that would have expired is kept. Data that already expired before you raised the setting is gone and does not come back.

**Lowering it** takes effect 7 days after you make the change. During those 7 days the web app and the API show the change as pending, with the date it applies. You can cancel it by setting the value back to the period that is still applied. Until the change applies, you are billed at the old level. When it applies, LimaCharlie deletes data older than the new period, and that deletion cannot be undone.

## How to set it

### Web app

Open the organization, then **Organization Settings** and **Data retention**. Pick a period and save. A pending reduction appears in the same section with its date.

### API and CLI

Read the current state:

```text
GET /v1/orgs/{oid}/retention
```

This needs `org.conf.get`. The response includes the period you requested, the period currently applied, a pending reduction and its date if there is one, and the amount of extended data stored.

Set the period with the organization configuration call, using the config name `retention_months` and one of `"12"`, `"18"`, `"24"` or `"36"`. With the CLI:

```bash
limacharlie org config-set --name retention_months --value 24 --oid <OID>
```

Any other value is rejected. Setting more than 12 on a free-tier organization is rejected as well.

### Infrastructure as code

`retention_months` is an organization value, so `limacharlie sync` and [Git Sync](../5-integrations/extensions/limacharlie/git-sync.md) manage it with the other `org-value` entries:

```yaml
version: 3
org-value:
  retention_months: "24"
```

Turn on the organization values option when you pull or push (`--org-values` on the CLI, `sync_org_values` in Git Sync). The account or key that runs the sync needs `billing.ctrl` as well as `org.conf.set`, because a sync changes the value through the same checks as a manual change. Lowering it from Git starts the same 7-day delay.

## See also

- [Billing options](billing/options.md)
- [Estimating data ingestion](billing/data-estimation.md)
- [Query limits and performance](../4-data-queries/query-limits-and-performance.md)
- [Permissions](../8-reference/permissions.md)
