# AI Triage

!!! warning "Private beta"
    Email Security is in **private beta**. It is not generally available, and
    access is enabled per organization — if the `ext-email-security` extension
    is not in your catalog, this product is not turned on for you yet.

    While it is in beta, expect the surface described here to move: commands,
    fields and event shapes may change between releases, and they may change in
    ways that are not backwards compatible. Pin a CLI version if you script
    against it, and re-read this page after upgrading.

    Talk to us before relying on it in production.

Email Security produces an explainable verdict for every message. AI triage is the
optional second pass: an agent that reads the message the way an analyst would, looks up
what else it can find, and writes a conclusion with the evidence behind it.

Nothing on this page is installed for you. It is a set of worked examples you adapt —
the agent's playbook, what it is allowed to do, and when it runs are all decisions that
belong to you, and they differ enough between organizations that a default would be
wrong more often than right.

## How it works

Triage is an ordinary [AI Session](../9-ai-sessions/index.md) driving the LimaCharlie
CLI. There is no email-specific AI integration to configure:

- The agent is an `ai_agent` Hive record — the same kind used everywhere else.
- It reaches Email Security through `limacharlie mailsec ...`, the same commands you
  use.
- A D&R rule starts it, using the standard `start ai agent` response action.
- Budgets, turn limits and model selection are the session's, enforced by AI Sessions.

That choice is deliberate. Because the agent is a normal API client, you can bring your
own model or provider, run the same playbook by hand to see what it does, and reason
about its access with the tools you already use for every other integration.

!!! important "What the agent may do is a permission, not a setting"
    There is no triage "mode". The agent authenticates with an API key, and that key
    either carries `mailsec.act` or it does not.

    A read-only triage agent — one that investigates and reports but never touches
    mail — is simply an agent whose key lacks `mailsec.act`. The API refuses the action;
    the agent cannot talk its way past it. **Do not rely on the prompt for this.** A
    prompt is a request, not a control.

## Before you start

1. The org is subscribed to `ext-email-security` and has at least one connected mail
   provider.
2. You have an AI provider credential (Anthropic, Bedrock, Vertex, OpenAI, …). See
   [AI Sessions providers](../9-ai-sessions/providers.md).
3. You have decided whether this agent may act. That is the first real decision, and
   the rest of the page assumes you have made it.

## Step 1 — Create the API key the agent will use

The key's permissions are the agent's ceiling. Start read-only; you can widen later.

=== "Investigate only (recommended to start)"

    ```bash
    limacharlie api-key create --oid $OID \
      --name mailsec-triage \
      --permissions "mailsec.get,org.get"
    ```

    The agent can read the queue, the message drawer, campaigns, sender profiles and
    the audit trail. If it tries to quarantine anything the API returns 403.

=== "Investigate and remediate"

    ```bash
    limacharlie api-key create --oid $OID \
      --name mailsec-triage \
      --permissions "mailsec.get,mailsec.act,org.get"
    ```

    Adds live remediation. Every action still passes through the same choke point as a
    human's: your `alert_only` / `enforce` mode applies, and an audit row is written
    naming the agent as the actor.

Add `mailsec.get.eml` only if you want the agent to read raw message bytes. That
permission is separate because it takes the original mail out of your tenant, and every
use is written to the access audit with a justification.

Store the key as a secret so the agent record can reference it rather than embed it:

```bash
echo '{"secret": "<the-api-key-value>"}' | \
  limacharlie hive set --hive-name secret --key mailsec-triage-key --oid $OID --enabled
```

## Step 2 — Write the agent

An `ai_agent` record holds the playbook and the session's limits. This example is a
starting point — the prompt is the part you should expect to edit.

```bash
cat > triage-agent.json <<'EOF'
{
  "prompt": "You are an email security analyst triaging a single message. You have the LimaCharlie CLI.\n\nStart with:\n    limacharlie mailsec message get <msg_uuid> --output yaml\n\nThat returns the index row and the parsed message model: sender, recipients, subject, links, attachments, authentication results (SPF/DKIM/DMARC), delivery hops, and the verdict the scoring engine already reached with the signals that fired.\n\nUseful follow-ups, roughly in order of value:\n    limacharlie mailsec message similar <msg_uuid>      who else received this\n    limacharlie mailsec sender get <address-or-domain>  has this sender written before\n    limacharlie mailsec campaign get <campaign_id>      the wider attack, if clustered\n    limacharlie mailsec message list --link-domain <d>  who else got mail linking there\n\nDecide three things:\n1. Is this malicious, suspicious, graymail, benign, or genuinely unclear?\n2. WHY, in terms a responder can verify. Name the evidence: the authentication result, the lookalike domain and what it imitates, the attachment type, the sender's history or lack of one.\n3. How far it reached: how many mailboxes, and whether it clusters into a campaign.\n\nRules for your conclusion:\n- Say what the evidence supports and no more. 'The sending domain was registered four days ago and DMARC failed' is useful. 'This is a targeted APT campaign' is not, unless you can point at what shows it.\n- If you cannot tell, say so and escalate. An honest 'unclear, needs a human, here is what I checked' is a good outcome. A confident wrong verdict is what destroys trust in the whole product.\n- A message a HUMAN reported deserves more care than its score suggests. Someone chose to report it; that is evidence in itself.\n- Never claim you performed an action you did not perform.\n\nIf your key carries mailsec.act you may remediate:\n    limacharlie mailsec message action <msg_uuid> --action quarantine_message --reason \"...\"\n    limacharlie mailsec campaign action <campaign_id> --action quarantine_message --confirm <campaign_id>\nOnly when the evidence is clear-cut. Campaign actions preview unless you pass --confirm; read the preview first. If your key lacks the permission the API will refuse you: that is the organization's decision, not an error to work around. Report your verdict and stop.\n\nFinish with a short structured summary: verdict, the evidence, reach, and what you did or recommend.",

  "name": "Email triage: {{ .msg_uuid }}",
  "debounce_key": "mailsec-triage-{{ .msg_uuid }}",

  "max_turns": 20,
  "max_budget_usd": 0.50,
  "one_shot": true,

  "plugins": ["lc-essentials"],

  "lc_api_key_secret": "hive://secret/mailsec-triage-key",
  "anthropic_secret": "hive://secret/anthropic-key"
}
EOF

limacharlie hive set --hive-name ai_agent --key mailsec-triage \
  --oid $OID --input-file triage-agent.json --enabled
```

What each of the non-obvious fields buys you:

| Field | Why it is there |
|---|---|
| `debounce_key` | One session per message. A redelivered notification or a second rule firing on the same message queues behind the first instead of paying twice to reach the same conclusion. |
| `max_budget_usd` | A per-session ceiling, enforced by AI Sessions. This is the real cost control — there is no separate Email Security budget to keep in sync. |
| `one_shot` | The session ends when the task is done rather than idling. |
| `plugins` | `lc-essentials` is what puts the `limacharlie` CLI in the session. Without it the agent has no way to reach anything. |
| `lc_api_key_secret` | The key from Step 1 — the agent's permission ceiling. |

## Step 3 — Decide when it runs

The agent does nothing until something starts it. These are two rules worth having, and
they answer different questions, so keep them separate — you may well want one without
the other.

### On a suspicious message

```bash
cat > triage-suspicious.json <<'EOF'
{
  "detect": {
    "target": "log",
    "event": "EMAIL_MESSAGE",
    "op": "is",
    "path": "event/verdict/verdict",
    "value": "suspicious"
  },
  "respond": [{
    "action": "start ai agent",
    "definition": "mailsec-triage",
    "debounce_key": "mailsec-triage-{{ .msg_uuid }}",
    "data": { "msg_uuid": "event/msg_uuid" }
  }]
}
EOF

limacharlie hive set --hive-name dr-general --key mailsec-triage-suspicious \
  --oid $OID --input-file triage-suspicious.json --enabled
```

`suspicious` rather than `malicious` is the interesting choice. A malicious verdict is
already actionable and your automations handle it. The value of triage is the band where
the score did **not** settle the question — which is also the band that produces the
analyst toil.

### On a user report

```bash
cat > triage-report.json <<'EOF'
{
  "detect": {
    "target": "log",
    "event": "EMAIL_USER_REPORT",
    "op": "exists",
    "path": "event/report_id"
  },
  "respond": [{
    "action": "start ai agent",
    "definition": "mailsec-triage",
    "debounce_key": "mailsec-triage-report-{{ .report_id }}",
    "data": {
      "msg_uuid": "event/original_msg_uuid",
      "report_id": "event/report_id"
    }
  }]
}
EOF

limacharlie hive set --hive-name dr-general --key mailsec-triage-user-report \
  --oid $OID --input-file triage-report.json --enabled
```

Note there is **no verdict filter** here. Someone took the trouble to report a message,
which is evidence the scorer did not have. Filtering these by score would discard the
signal exactly when it disagrees with you — the only time it is interesting.

!!! warning "A report can arrive without an original"
    `original_msg_uuid` is empty when the reported message was never indexed — the mail
    predates the connection, or landed in a mailbox outside your scope. The report is
    still real and still queued. If your prompt assumes an original exists, say what the
    agent should do when it does not: read the forwarded copy and say the original was
    not found.

## Step 4 — Try it by hand first

Run the playbook yourself against a real message before letting a rule fire it. It takes
a minute and it is the difference between finding out now and finding out from a bill:

```bash
limacharlie mailsec message list --verdict suspicious --limit 5 --oid $OID --output yaml
limacharlie mailsec message get <msg_uuid> --oid $OID --output yaml
limacharlie mailsec message similar <msg_uuid> --oid $OID --output yaml
```

If those give you what you would want an analyst to see, the agent will have it too. If
they do not, fix the prompt before wiring the trigger — a session that has to guess is a
session that will assert.

## Controlling cost

Everything here is the session's, not Email Security's:

- `max_budget_usd` caps one run.
- `max_turns` caps how long it can go round.
- `debounce_key` stops duplicate work on the same message.
- The trigger rule is what controls **volume**. Widening it from `suspicious` to every
  message is the single largest cost decision on this page.

To see what you are actually spending, use the AI Sessions
[cost tracking](../9-ai-sessions/cost-tracking.md) surface. Email Security does not
meter this separately — one budget in one place, rather than two that can disagree.

## Turning it off

Disable the trigger rules. The agent record can stay; it costs nothing when nothing
starts it.

```bash
limacharlie hive set --hive-name dr-general --key mailsec-triage-suspicious \
  --oid $OID --input-file triage-suspicious.json --disabled
```

## What the agent writes back

A triage verdict is recorded like any other, with `mode: ai` and the rationale attached,
so the queue shows what was decided and why. The
explainability contract applies to the agent exactly as it does to the scoring engine: a
verdict a responder cannot check is not a verdict they can act on.
