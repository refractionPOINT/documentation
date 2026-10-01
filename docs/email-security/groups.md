# Message Groups & Cases

--8<-- "includes/email-security-beta.md"

A message group represents one email delivered to several recipients. Open
**Email Security → Groups**, or choose **Group by message** from Messages, to
triage the copies together. A campaign relates similar messages and may contain
several groups. Group membership is stricter than campaign similarity.

## Identity and the queue

The organization-scoped `group_id` combines the normalized Message-ID with the
sender, Reply-To, subject and message content. Reusing a legitimate Message-ID
with different content does not put the forged email into the legitimate group.
Recipient-specific delivery headers and supported Safe Links wrapping do not
create separate identities. Missing or truncated identity uses an individual
message identity. Other content changes, including personalized links, can split
copies into separate groups; inspect instances before applying remediation.

The default queue shows groups needing triage: malicious or suspicious copies,
medium-or-higher rule severity, or user-reported mail. An analyst benign revision
removes that copy's severity-only triage contribution while preserving its
historical severity. Other flagged copies or reports still keep the group in the
queue. **Show all groups** includes the remaining groups.

Filter by verdict, severity, disposition, user-reported state and time. Omitted
user-reported state leaves that dimension unrestricted. Filters combine across
dimensions and allow alternatives within one dimension. Message-specific filters
such as mailbox and free text are not carried into the Groups view.

The drawer shows first and last seen, message and recipient counts, maximum
verdict and severity, placement and disposition counts, a representative message
and campaign association when unambiguous. Queue summaries show their `as_of`
time; the drawer reads a consistent current snapshot. A missing severity remains
unknown. Instances are paged: continue until there is no next cursor rather than
assuming the first page contains every recipient.

## Preview, confirm and track

Group remediation prepares a durable snapshot of **every** member, including
all-hands messages with more than 20,000 recipients. Preparation may need several
passes. The preview shows its snapshot time, selected count, action and frozen
parameters. No confirmation is available until preparation finishes. Newly
arriving copies after the snapshot require a separate preview.

Confirm the complete preview to start execution. Confirmation is bound to the
organization, authenticated actor, group, action, parameters and manifest. A ready
preview expires 45 minutes after its snapshot; prepare a new preview rather than
confirming stale information. Confirming again after execution starts resumes the
same job and does not create another intent.

Execution processes bounded chunks and survives worker restarts. Track the job
until it reaches a terminal phase, and inspect **succeeded**, **skipped**,
**withheld** and **failed** counts. Withheld is not successful remediation. The
normal enforcement, exclusion and mailbox protection rules still apply; an
explicit force request requires the same deliberate consent as individual
remediation. Retention can remove a selected copy before execution, and provider
failures can leave a partial outcome. Review those outcomes before retrying.

The console can resume a job from its URL. Paused browser polling does not cancel
the durable server job; refresh its status. See [Bulk Remediation](remediation.md)
for individual and campaign scopes.

## Opt-in Cases detection pack

In **Email Security → Protection setup**, install the Cases pack after enabling
Cases. The pack creates ordinary `dr-general` rules with your credentials. It
only reports detections; it does not change verdicts, dispositions or placement.
Installation needs permission to call the extension and read/write detection
rules. Removal also needs detection-rule delete permission.

The pack reports:

- `EMAIL_ANALYSIS_COMPLETE` when the final verdict is malicious or suspicious,
  severity is at least medium, or the message was user-reported.
- `EMAIL_USER_REPORT` from a human reporter. Automated senders are excluded.

| Severity | Detection priority |
|---|---:|
| informational | 1 |
| low | 1 |
| medium | 3 |
| high | 6 |
| critical | 9 |
| unknown or missing | 1, with unknown severity retained |

Global suppression limits duplicates for the same group and severity across
mailbox sensors and both triggers for 30 days. A higher severity can report again
and raise the priority of the **same retained case**. Explicit case identity
keeps late detections together independently of ordinary time-based grouping and
reopens a closed case when necessary. A manually merged case follows its retained
merge target.

Deduplication lasts while that identity's case remains retained. Deliberate case
deletion, retention expiry, or a missing, cyclic or excessively long merge mapping
allows a fresh case; retired mappings carry an audit reason. A missing group uses
the immutable message identity rather than an empty organization-wide key.

Installation and repair show an outcome for each record. Repair adds missing
records without overwriting existing rules. Updates preserve disabled state,
customer tags and comments, and use conditional writes. A customer-owned record
at a reserved pack key is refused. Unavailable metadata stays unknown instead of
being treated as an absent rule. Removal targets only pack-owned records in the
pack's namespace.
