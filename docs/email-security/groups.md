# Message Groups & Cases

--8<-- "includes/email-security-beta.md"

A message group represents one email delivered to several recipients, including
per-recipient personalization. Open
**Email Security → Messages** and choose **Groups** in the **Messages | Groups**
switch to triage the copies together. Groups is the default when no view has been
chosen for the organization. A campaign relates similar messages and may contain
several groups. Group membership is stricter than campaign similarity.

## Identity and the queue

The organization-scoped `group_id` combines the normalized Message-ID, sender
SMTP address, normalized subject, From/sender display names, the sets of
registrable Reply-To and link domains, and the SHA-256 digests of attachments.
For links to IP addresses or hosts with no registrable parent, the normalized
host value participates instead. Relative paths without a host contribute no
link domain. Different IP destinations stay separate; equivalent IPv6 spellings
and host capitalization do not split copies.
Inline raster images displayed in the body are excluded; inline PDFs, SVGs and
other files remain attachments for identity purposes.

Copies can share a group despite personalized greetings or footers, tracking and
unsubscribe URL paths, queries or fragments, Reply-To local-part tokens, different
HTML presentation and recipient-specific delivery headers. A copy reusing the
same Message-ID, sender and subject with a different link-domain or attachment
set stays separate. Group membership does not establish that every copy has the
same body, engine verdict or disposition; inspect instances and the remediation
preview before acting.

Missing or invalid Message-ID or sender, or incomplete identity inputs, produce
an individual message identity. Unrelated parser warnings do not split copies
when all identity inputs are complete. The current identity version applies only
to newly ingested messages. Existing stored group IDs remain unchanged, so older
and newer groups can coexist for the same send; no historical regrouping occurs.

The default queue shows groups needing triage: malicious or suspicious copies,
medium-or-higher rule severity, or user-reported mail. An analyst benign revision
removes that copy's severity-only triage contribution while preserving its
historical severity. Dispositions benign, graymail and simulation dismiss that
copy's triage contribution; malicious and spam flag it. The historical user-report
indicator stays visible. Other undismissed copies keep the group in the queue.
**Include unflagged groups** includes the remaining groups.

Groups contain retained recipient copies from the past 35 days, consistent with
the group drawer and remediation preview.

The shared [Messages filters](messages.md#the-queue) apply in both views, including
mailbox, sender, free text, placement, direction, lane, score and IOC pivots.
Switching views keeps the filters and their badges. Unsupported combinations show
an error instead
of silently removing a filter. When a filtered page comes back empty while more
results remain, the queue shows **Still searching** and keeps loading, and after
twenty empty pages in a row offers **Keep searching** rather than claiming that
nothing matched.

Each row describes the whole group: subject and sender, representative
message, worst verdict and severity, recipient and copy counts, disposition
summary, and first and last seen. When the response includes a matching-copy
count, the row also shows **N of M copies match**. Its absence does not mean that
every copy matched.

Both views apply the same filters on the server: literal text search,
mailbox, sender address or root domain, campaign, link domain, attachment SHA-256,
placement state, direction, minimum score, lane, verdict, severity, disposition
(including `none`), user-reported state and time. Omitted user-reported state leaves
that dimension unrestricted. Alternatives within one filter use OR; different
filters use AND **on one recipient copy**. For example, mailbox A plus malicious
returns a group only if A's copy is malicious, even when another copy is malicious.
The default flagged-group gate remains separate: **Include unflagged groups** removes it.

Filtered ordering uses the newest **matching** copy's time. Summary badges and
counts still describe the whole group, so a matching copy's verdict or disposition
can differ from the aggregate. The group drawer and remediation preview include
all copies, including recipients outside the list filters.

The list uses bounded index reads and opaque cursors. A filtered cursor pins a
snapshot for 50 minutes; restart pagination after it expires or after changing
filters. Short or empty pages can still carry a `next_cursor`: continue until it
is empty. If a canonical matching-copy lookup exceeds its bound, the explicit
`group_filter_too_broad` error asks for narrower filters. Search and lane have the
same supported combinations as message lists; unsupported combinations are
refused, never ignored. Exact `matched_copies` counts are omitted because counting
large fan-outs per row would exceed the predictable page cost.

The drawer shows first and last seen, message and recipient counts, maximum
verdict and severity, placement and disposition counts, a representative message
and campaign association when unambiguous. Queue summaries show their `as_of`
time; the drawer reads a consistent current snapshot. A missing severity remains
unknown. Instances are paged: continue until there is no next cursor rather than
assuming the first page contains every recipient.

## Preview, confirm and track

Select groups in the queue to prepare remediation or disposition previews. The
console accepts up to 50 groups per batch; each group has its own durable job and
can contain more than 20,000 copies. Review the prepared jobs before confirming
the batch. Preparation failures can be retried without recreating the successful
previews. A failed or uncertain confirmation requires reviewing the job status;
the console does not confirm automatically.

!!! warning "Group actions cover all copies"
    A mailbox, sender or other queue filter narrows which groups appear. Group
    remediation and disposition still cover **every copy of each selected
    group at the preview snapshot**, including copies that did not match the
    filter. Inspect the preview before confirming.

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

Microsoft may accept quarantine or restore before completing it. The group job
stays running while that provider result is pending; acceptance does not increase
its succeeded or failed counts. Continue polling the same job instead of creating
another intent. Each recipient has up to 90 minutes from its first recorded
pending result to reach a terminal provider outcome. An unconfirmed result after
that window counts as failed, even if Microsoft later completes the action.
Inspect the provider state before retrying such a member.

The console can resume a job from its URL. Paused browser polling does not cancel
the durable server job; refresh its status. See [Bulk Remediation](remediation.md)
for individual and campaign scopes.

Group disposition uses the same preview and confirmation flow, requiring both
`mailsec.act` and `mailsec.set`. Choose malicious, spam, graymail, benign or
simulation, or clear the existing disposition, with an optional note of at most
1,024 characters. Confirmation uses the frozen value and note and checks current
permission. It records the decision through the ordinary disposition path,
including history and disposition events, without changing engine verdicts or
running remediation automations. Newly delivered copies keep their own disposition.

## From the command line

```bash
limacharlie mailsec group list --severity high --severity critical --disposition none
limacharlie mailsec group list --all --since 2026-09-01T00:00:00Z
limacharlie mailsec group get <GROUP_ID>
limacharlie mailsec message list --group-id <GROUP_ID>
limacharlie mailsec group preview <GROUP_ID> --action quarantine_message --reason "Incident review"
limacharlie mailsec group preview <GROUP_ID> --action set_disposition --disposition benign --note "Reviewed"
limacharlie mailsec group status <JOB_ID>
limacharlie mailsec group confirm <JOB_ID> --confirmation <TOKEN>
```

Preview and confirm wait for the job by default; `--no-wait` returns it at once.
Reuse the printed `--preview-id` when retrying the same preview. A failed or
withheld recipient outcome exits non-zero. See [Command Line Interface](cli.md).

## Routes

All routes are under `/v1/mailsec/{oid}`. See [API Reference](api-reference.md)
for the shared conventions.

| Route | Does |
|---|---|
| `GET /groups` | The flagged triage queue, ordered by the newest matching copy. Accepts the same filters as Messages: `q`, `mailbox`, `sender_email`, `sender_root_domain`, `campaign_id`, `group_id`, `link_domain`, `attachment_sha256`, `state`, `direction`, `min_score`, `lane`, `verdict`, `severity`, `disposition` (including `none`), `user_reported`, `since`/`until` (matching-copy time, RFC 3339 or Unix seconds), plus `all=true`, `cursor`, `limit`. Repeated values OR within a filter; every active filter must match one copy. The cursor is bound to the filters and tenant. Follow short or empty pages while a cursor remains. Requires `mailsec.get` |
| `GET /groups/{group_id}` | One consistent aggregate of every indexed copy: first/last seen, counts, maximum verdict and severity, placement and disposition summaries, representative message and campaign. Requires `mailsec.get` |
| `GET /messages?group_id={group_id}` | The group's recipient copies, paged like any message list |
| `POST /groups/{group_id}/actions/preview` | Prepare a durable snapshot of every copy. Body: `preview_id` (caller UUID, reused on retry), `action` (a remediation action or `set_disposition`), optional `reason`, `text`, `force`; for `set_disposition`, `disposition` or `clear: true`, and optional `note`. Requires `mailsec.act`, plus `mailsec.set` for `set_disposition` |
| `GET /group-actions/{job_id}` | Preparation or execution progress: phase, snapshot time, counts of succeeded, skipped, withheld and failed. The `confirmation` token appears only once the manifest is complete. Requires `mailsec.get` |
| `POST /group-actions/{job_id}/confirm` | Execute the complete preview with `{"confirmation": ...}`, from the same authenticated actor that prepared it. Repeating it resumes the same job. Requires `mailsec.act` |

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

Copies classified benign, graymail or simulation are excluded from both triggers.
Closing a Case alone does not dismiss its messages. Set the group disposition
when dismissing a retained Case; future unclassified copies can still report and
reopen it.

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
