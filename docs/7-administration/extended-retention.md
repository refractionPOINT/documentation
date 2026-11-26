# Extended data retention

Every organization keeps its telemetry searchable for 12 months by default. Extended retention lets you raise that to 18, 24 or 36 months for an organization. Older data stays searchable the same way recent data does, in the Timeline, in Search (LCQL), and in the detection and audit views. There is no archive to restore from.

It is a setting on each organization, with four values: 12 (the default), 18, 24 or 36 months.

## What it covers

| Extended to the period you choose | Stays at 12 months |
| --- | --- |
| Telemetry events | [Artifacts](../5-integrations/extensions/limacharlie/artifact.md) |
| Detections | The object search that answers "where have I seen this indicator" |
| Audit logs | Usage and summary charts, such as the event type breakdown and the traffic charts |

To keep artifacts longer than a year, send the `log` stream, which carries artifacts, to an [Output](../5-integrations/outputs/index.md) as the files arrive.

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

You need both the `org.conf.set` and `billing.ctrl` permissions to change the retention period, including to lower it. `org.conf.set` alone is not enough. See [Permissions](../8-reference/permissions.md).

Going above 12 months needs a paid plan. An organization whose sensors all fit in its plan's free tier is refused. Lowering to 12 months is always allowed, whatever the plan.

**Raising it** applies immediately. From that moment, data that would have expired is kept. Data that already expired before you raised the setting is gone and does not come back. If the change is saved but cannot be applied right away, it applies within a day. The web app and the API both say so.

**Lowering it** takes effect 7 days after you make the change. During those 7 days the web app and the API show the change as pending, with the date it applies. You can cancel it by setting the value back to the period that is still applied. Until the change applies, you are billed at the old level. When it applies, LimaCharlie deletes data older than the new period, and that deletion cannot be undone.

## How to set it

### Web app

Open the organization, then **Organization Settings**, **General**, and the **Data retention** card. Pick a period and confirm. A pending reduction appears on the same card with its date, with a button to cancel it. The card also shows how much data you keep beyond 12 months.

### API

Set the period with a POST to the organization configuration endpoint. The value is one of `"12"`, `"18"`, `"24"` or `"36"`.

```text
POST /v1/configs/{oid}/retention_months
value=24
```

The response is the retention status described below. Any other value is rejected, and so is a value above 12 on an organization that does not meet the plan requirement.

A `503` response with `"saved": true` means the value is stored but could not be applied immediately. Do not send it again. It applies within a day.

Read the current state with a GET. This needs the `org.conf.get` permission.

```text
GET /v1/orgs/{oid}/retention
```

| Field | Meaning |
| --- | --- |
| `requested_months` | The period you asked for. |
| `applied_months` | The period in force now. |
| `pending_months` | The lower period waiting to apply, `0` if none. |
| `pending_until` | When the pending reduction applies, in Unix seconds, `0` if none. |
| `extended_bytes` | Bytes stored beyond 12 months. |
| `extended_as_of` | The day (`YYYY-MM-DD`) that figure was measured, empty if it has not been measured yet. |

### CLI

```bash
limacharlie org config-set --name retention_months --value 24 --oid <OID>
```

The command fails with the API's reason when the change is refused. `limacharlie org config-get --name retention_months` reads the value you set. To see the pending reduction and the extended data size, call the status endpoint above, for example with `limacharlie api`.

### Infrastructure as code

`retention_months` is an organization value, so `limacharlie sync` and [Git Sync](../5-integrations/extensions/limacharlie/git-sync.md) manage it with the other `org-value` entries:

```yaml
version: 3
org-value:
  retention_months: "24"
```

Quote the number. Turn on the organization values option when you pull or push (`--org-values` on the CLI, `sync_org_values` in Git Sync). The account or key that runs the sync needs `billing.ctrl` as well as `org.conf.set`, because a sync changes the value through the same checks as a manual change. A refused value shows up in the push errors and the push exits with a failure. Lowering it from Git starts the same 7-day delay.

A config that does not mention `retention_months` leaves the current value alone, even with a forced push, so a template written before this setting existed cannot shorten an organization's retention. To return to the default, set it to `"12"`.

## See also

- [Billing options](billing/options.md)
- [Estimating data ingestion](billing/data-estimation.md)
- [Query limits and performance](../4-data-queries/query-limits-and-performance.md)
- [Permissions](../8-reference/permissions.md)
