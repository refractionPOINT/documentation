---
description: What LimaCharlie products do together for an MSSP. Each chain names the mechanism that connects the products, what you configure, and what is not supported.
---

# What the Products Do Together

Part of [Recommended Deployment for MSSPs](index.md).

Running several security products from different vendors gives you several consoles, several alert queues and several copies of the same asset list. Running them in one LimaCharlie tenant gives you one event stream, one rule language, one queue and one directory of people and machines. This page lists what that buys you, product pair by product pair.

Each chain below says what connects the products, and what you have to set up. "Ships" means it works once the products are subscribed, or after one toggle. "You configure" means a rule, policy or record you write. Chains that need glue name the glue. Chains that do not exist are listed at the end, so you do not sell them.

## The four joins

Most chains are one of these four joins plus a product.

### 1. One detection pipeline

Each product in this guide writes its output into the tenant as ordinary events from a sensor or an adapter:

| Product | Events |
| --- | --- |
| Endpoint agent | Process, network, file, DNS and other [EDR events](../../8-reference/edr-events.md) |
| Adapters | One sensor per source (or per device), with the source's events |
| Email Security | Each mailbox is a sensor: `EMAIL_MESSAGE`, `EMAIL_VERDICT`, `EMAIL_ACTION`, `EMAIL_USER_REPORT` |
| Cloud Security | `cloud_finding.created`, `.closed`, `.still_open` on its adapter |
| Vulnerability Reporting | `vuln_finding.created`, `.closed`, `.kev_match`, `.state_changed` on its adapter |
| Application Control | `APP_CONTROL_DENIED` and related events on the endpoint |
| Host Posture (coming soon) | `config_finding` events on its adapter |
| Deception (coming soon) | `deception_hit` (decoys) and `deception_drop_hit` (tokens) events on its adapter |

So one D&R language detects on all of it, your Outputs can carry any of it to your SIEM, and the detections your rules raise land in one Cases queue.

### 2. One IOC index

Email Security indexes sender and link domains, attachment hashes and file names, IP addresses from the headers, and the mailbox address and UPN in the same indicator index the endpoint agent and adapters use. One IOC search for a domain, a hash or an IP lists the sensors that observed it, with first and last seen times: the mailboxes that received it and the endpoints whose telemetry contains it. A search for a UPN finds the mailbox and the identity adapters that saw that person. Run it with `limacharlie ioc search --info locations`, then query those sensors' events to compare times. A match shows where an indicator appeared, not that someone clicked or ran something. See [Using the CLI with frontier models](../../6-developer-guide/frontier-models.md).

### 3. Entities: one directory of people and machines

[Entities](../../cloud-security/entity-pivot.md) resolves identifiers from LimaCharlie sensors, Cloud Security's identity and device providers, asset inventory sources and mailboxes into User and Host entities. The User card shows flagged mail, detections and live state of the machines that person owns, and open cloud findings, on one page.

Entities needs Cloud Security. It also needs a source of **ownership** to tie a person to a machine: a device source that names the owner's email, such as Intune, Google Workspace devices, or an asset inventory source such as an EDR console or your IdP. The endpoint agent alone tells you who was active or logged on, not who owns the machine.

### 4. Pivots in rules and outputs

The [`pivot` operator and template functions](../../cloud-security/rule-pivots.md) ask Entities a question from inside a D&R rule or an Output: from a sensor ID to its owner's email, or from an email to the sensors that person owns. In a D&R rule you can also pivot from an IP in a firewall log to the sensor behind it; outputs refuse address pivots. Only confirmed links are followed; an ambiguous answer is an error, never a guess. A lookup that cannot answer in time returns nothing, so treat an empty value as unknown. Pivots need Cloud Security, and saving a rule that uses one needs `cloudsec.get`.

This example, from the pivot reference, puts the machine's owner on a detection:

```yaml
respond:
  - action: report
    name: encoded-powershell
    metadata:
      owner: '{{ pivot "sensor_id" .routing.sid "owner.email" }}'
```

## Chains that ship

### Endpoint agent and Cloud Security: runtime meets posture

- Cloud Security matches each live sensor to the cloud VM, node or container it runs on, using the provider's IDs, never names. The graph gets a `runs_on` edge, and a finding on a matched resource carries `runtime_sids`: the LimaCharlie sensors running on it. See [Findings](../../cloud-security/findings.md) and [Graph](../../cloud-security/graph.md).
- Your endpoints feed the merged asset inventory automatically through the native `limacharlie` source. See [CAASM](../../cloud-security/caasm.md).
- **You configure:** a coverage expectation in CAASM. Then a running VM with no live sensor becomes a finding, and so does a device your IdP sees with no EDR. For Globex, that is the list of AWS instances Northwind has not covered yet, kept current without anyone running a report. See [Declare expected coverage](../../cloud-security/caasm.md#declare-expected-coverage).

### Email Security, endpoints and identity: one search for an incident

Because of the shared IOC index, a confirmed phish turns into a few searches: who else received it, which endpoints saw the link's domain or the attachment's hash, and where the recipient signed in afterwards. The [message pivots](../../email-security/messages.md#the-two-ioc-pivots) answer who else received it across every mailbox. The IOC search lists the endpoints whose telemetry contains the domain or hash, and the UPN search finds the identity adapters that saw the recipient. An analyst or an AI agent then reads those events to decide whether anyone clicked. Nothing has to be configured.

### Email Security, Cloud Security and a device source: mail to person to laptop

With Cloud Security connected to the customer's Microsoft 365 or Google Workspace, and a device source that names owners, a mailbox resolves to a person and the laptops they own. The User card shows the phish they received next to detections on their machines. A rule on mail events can pivot from `event/mailbox/upn` to the person's `owned.sensor_id` or `owned.hostname` and put it in the detection. See [Entities](../../cloud-security/entity-pivot.md).

### Products and Cases: one queue

A detection from any product can become a case. Several products ship the rules for it:

- **Cloud Security**: one toggle installs rules that open a case on each high or critical finding the feed emits, resolve it when the finding closes, and reopen it if it was closed while the finding is still open. See [Findings and Cases automation](../../cloud-security/automation.md#findings-cases-automation).
- **Email Security**: the [Cases detection pack](../../email-security/groups.md#opt-in-cases-detection-pack) keys its detections to the message group, so the flagged copies of one phish share a case.
- **Application Control**: four managed alert rules, off by default. See [Managed alerts](../../5-integrations/extensions/limacharlie/app-control.md#managed-alerts).
- **Deception** and **Host Posture** (coming soon) ship rules too.

Case events go to the organization's webhook adapter once you add one, so a D&R rule on a new case can start an AI agent or a playbook. See [Cases](../../5-integrations/extensions/limacharlie/cases.md#webhook-notifications).

### Endpoint tags and every endpoint product: one targeting key

The same sensor tags select the App Control policy, the Vulnerability Reporting risk weight (`lc:asset:*`), Exfil and Integrity rules, and, once launched, Host Posture rule scope and Deception policy targeting. Tags come from the installation key, the API, or a D&R `add tag` action with an optional time to live.

The strongest example: once the reserved lockdown policy exists in the organization, a D&R rule on an endpoint event adds `appctl-lockdown`, and App Control locks a Windows or macOS host down on its next sync, while it stays reachable for your investigation. See [Automate lockdown with D&R](../../5-integrations/extensions/limacharlie/app-control.md#automate-lockdown-with-dr). The trigger has to be an event from the endpoint itself, so the tag lands on the right sensor.

### Lookups and every rule engine: one threat-intel record

One `lookup` record, fed by the [Lookup Manager](../../5-integrations/extensions/limacharlie/lookup-manager.md) or written by your team, is read by EDR and adapter D&R rules, by Email Security's `threat_feeds` policy and `dr-mail` rules, and by rules on Cloud Security finding events. Add a domain once and links to it are flagged in mail and alerted on at the endpoint. See [IOC feeds](../../email-security/ioc-feeds.md).

### Application Control audit mode and the allow list

In audit mode, every program a policy would block is an `APP_CONTROL_DENIED` event marked not enforced. Report them, group them by signer and path, and the allow rules you write from that list are the customer's real software, not a guess. The **Block with Application Control** action, offered on hashes in events, detections and the sensor's file view, writes a deny rule from the same console. See [Reading would-be blocks](../../5-integrations/extensions/limacharlie/app-control.md#reading-would-be-blocks) and [Blocking a file from the console](../../5-integrations/extensions/limacharlie/app-control.md#blocking-a-file-from-the-console).

### Endpoint agent, BinLib and YARA

The first time the sensor sees a binary at a path, [BinLib](../../5-integrations/extensions/limacharlie/binlib.md) records it. `find_hosts` lists the sensors where matching binaries were seen, and a D&R rule can send acquired files to a BinLib YARA scan with rules from YARA Manager. `find_hosts` runs as the person or agent asking, so a D&R rule cannot call it.

### Deception, endpoints and Cases (coming soon)

Decoys are placed through the endpoint agent on sensors that a policy selects by tag. Read and modify alerts ride on Exfil and Integrity rules that Deception writes for you, only on hosts that hold a decoy. A live decoy hit becomes a priority-10 detection, and Cases files it under the endpoint that held the decoy, not under the Deception adapter. A policy can also isolate that endpoint, with guards against scanners and a rate limit.

### Host Posture and Cloud Security (coming soon)

When a tenant has both, each failing Host Posture rule shows up in Cloud Security as one finding that rolls up every failing host, next to the cloud misconfigurations. Host configuration and cloud configuration land in one worklist with one ranking.

### Investigation Engine and everything (coming soon)

The Investigation Engine reads mail, Entities, endpoint telemetry, identity sign-ins, cloud findings, App Control observations and vulnerabilities in one run. Its phishing templates check, for each recipient of a flagged message, whether the person's own laptops or signed-in Chrome profile looked up the link's landing domain after delivery, and label the answer clicked, possible, not clicked or unknown. That label is the engine's reading of the telemetry, not proof of a click. With no owner, no sensor or no telemetry, the answer is unknown, never "not clicked". Containment of the mail and the machine follows the tenant's investigation policy. Like Entities, it needs an ownership source.

### AI on top of all of it

The public API and the `limacharlie` CLI reach every product in this guide, and the MCP server exposes a set of tools for agents, so one AI agent can read mail, findings, detections and telemetry in the same session. A D&R rule with `start ai agent` starts it from an event, a detection or a case event. The agent can call playbooks for the deterministic steps. See [AI as a main user](ai.md).

## Chains that need glue

These work with a rule or a playbook you write. The glue is named in each one.

### A malicious email, then act on the recipient's laptop

No shipped rule does this. Response actions act on the event's own sensor, which for a mail event is the mailbox, so `isolate network` or `add tag` on a mail rule would not reach the laptop.

The glue: a rule on `EMAIL_VERDICT` pivots from `event/mailbox/upn` to `owned.sensor_id`, puts the sensor IDs in the detection, and calls a [playbook](../../5-integrations/extensions/limacharlie/playbook.md). The playbook checks each sensor against your response policy, then acts on it through the API: tag it, isolate it, or queue a collection with [Reliable Tasking](../../5-integrations/extensions/limacharlie/reliable-tasking.md), which takes one sensor ID, tag or selector per request. It needs Cloud Security and an ownership source. See [Acting on the pivoted sensor](../../cloud-security/rule-pivots.md#acting-on-the-pivoted-sensor).

### A cloud finding, then act on the VM's sensor

A `cloud_finding.created` event carries the finding, with `event/finding/runtime_sids` when Cloud Security matched sensors to the resource. A rule on it calls a playbook that checks those sensors and acts on each one: a Reliable Tasking request for a collection or scan, or an API call to tag it. With no `runtime_sids`, leave it to an analyst. A plain `task` or `add tag` in the rule would act on the Cloud Security adapter's sensor instead.

### Counting signals about one person across products

Stateful rules and sensor variables work per sensor, and the mailbox, the identity adapter and the laptop are different sensors. What does work across sensors is [suppression](../../8-reference/response-actions.md#suppression) with `is_global: true`: two rules, one on `EMAIL_VERDICT` and one on an Okta sign-in failure, with the same period, the same count settings and a key that renders to the same string for the same person, share one count in the organization. Normalize the mailbox and sign-in identifiers so they match. That gives you "three signals about this person in an hour". It counts; it does not check order.

### Vulnerabilities into Cases or tickets

`vuln_finding.*` events are on the event stream, but no rule ships for them. Write a D&R rule that reports the ones you act on, or route them with an Output filtered by event type.

### Adapter records into the asset inventory

Adapter telemetry does not feed CAASM by itself. Push records with `limacharlie cloudsec caasm ingest` or a D&R feeder rule. The native `limacharlie`, Google Workspace and Intune sources need no glue. See [Pushing records in](../../cloud-security/caasm.md#pushing-records-in).

## What is not supported

Do not build a service on these. They are listed because each is a reasonable thing to expect.

- **One D&R rule that follows a sequence across sensors.** "A phish was delivered, then that user's laptop ran a new binary" or "then that user signed in" cannot be one rule, because stateful logic is per sensor. Use the IOC search, Entities, pivots, global suppression counting, an AI agent, or the Investigation Engine once it launches.
- **Mailbox to laptop without an ownership source.** Pivots and the Investigation Engine follow confirmed ownership only, and the endpoint agent alone does not provide it.
- **Entities or pivots without Cloud Security.**
- **A join between Vulnerability Reporting and BinLib.** They are separate inventories: installed packages and observed binaries. An analyst or agent can use both.
- **Cloud Security custom posture rules that use lookups, tags or sensor context.** Their operator allowlist excludes them.
- **Cases that extract indicators from detections by themselves.** People, agents and the API attach entities to cases.
- **App Control allow lists built from general process telemetry.** Observations come from App Control's own audit and enforcement events.
- **Host Posture cases filed under the host** (coming soon). They group under the Host Posture adapter, with the host in the event.
- **AI triage as a built-in Deception response** (coming soon). Start an agent from your own rule on Deception detections instead.
