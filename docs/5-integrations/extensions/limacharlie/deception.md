# Deception

!!! warning "Early release"
    Deception has not been validated on a broad set of real hosts and identity tenants yet. Statements below that depend on real endpoint or log-source behavior are marked **not verified**. Read [Known limitations](deception/limitations.md) before relying on it as a primary control.

Deception plants unique decoys on your endpoints through the LimaCharlie sensor: credential files, service and MCP configuration files, notes naming decoy hostnames, and notes holding phantom accounts (cloud-account form in this release). Nothing legitimate has a reason to touch a decoy, so a decoy that is read or used is a high-fidelity signal. With the default rules enabled, a real hit that is not a deletion becomes a priority 10 detection, and, if `ext-cases` is subscribed, opens a critical case. A hit can also isolate the host if you opt in, and only when the evidence is an event the decoy's own sensor reported (never a network address). Deletion hits are priority 5, and test hits never open a case. The rules are yours to edit.

It is built mainly to catch AI-driven attackers early. An AI agent that lands on a host reads every credential file it finds, tries every key and follows every breadcrumb, usually within minutes. A human attacker who goes through the same files trips the same decoys.

## What it does

Every decoy raises alerts on one or both of two things:

- **Read.** The decoy file was opened, modified, or deleted. The sensor reports this.
- **Use.** A secret inside the decoy was used. Every secret carries its own destination, and the destination is LimaCharlie's: a decoy Kubernetes config points at a fake API server, a decoy AWS profile points its endpoint at a fake AWS API, a decoy `.env` names fake internal services. Phantom accounts are usernames that exist nowhere, so a sign-in attempt with one shows up in logs you already send to LimaCharlie.

Each secret in each decoy is generated per decoy and per host. A hit therefore names the machine the secret was planted on, even when the secret is used from somewhere else.

Nothing about a decoy is the same in every organization. Decoy file names, the names written inside the files, and what the fake services answer (server and tool names, bucket names, identities, pages) are derived per organization from a secret that only LimaCharlie holds, so seeing one decoy in one environment does not let an attacker recognize the decoys of another. The fake services also behave like the real ones over time: a decoy login session expires on the lifetime the fake service advertises, and an expired session is still attributed to the decoy.

Deception is self-serve. It never creates accounts, mailboxes, cloud keys, or DNS records in your systems, and it never subscribes your organization to another extension or changes a sensor's mode on your behalf.

## How it works

1. You subscribe to the extension and describe what you want in its configuration record: **templates** (what each decoy looks like) and **policies** (which templates go on which sensors, and what to do on a hit). The default [template library](deception/decoys.md#default-template-library) is built into the extension and ships with each release. Nothing in it is placed until you copy a template into your own configuration, and the copy is yours to edit.
2. `deploy` places decoys through sensor tasking. A decoy counts as covered only after the extension checks the file's hash on the host. A task acknowledgement alone is not proof. A folder with a generated name that the host does not have is created by the extension and removed again with its last decoy (see [File names and paths](deception/decoys.md#file-names-and-paths)).
3. Decoy reads reach the cloud through rules the extension writes in other extensions' configurations (Exfil watch rules, Integrity FIM rules) and its own rules. Decoy use reaches the cloud through a public LimaCharlie-operated collector, or through the sign-in logs you already send.
4. Every candidate event is checked against a registry of the decoys the extension planted. Only a confirmed match becomes a `deception_hit` event. Everything else is dropped.
5. The default detection rules turn `deception_hit` events into detections, and, if you opted in, a guarded isolation of the host.

See [Decoys and coverage](deception/decoys.md), [Configuration](deception/configuration.md), [Requests](deception/requests.md), [Detections, cases and response](deception/detections.md), [Operations](deception/operations.md) and [Known limitations](deception/limitations.md).

## The web app

The **Deception** page of your organization in the web app is the way to manage Deception without the command line. It reads and writes the same configuration record and sends the same requests described on these pages, with the same permissions (see [Permissions](deception/operations.md#permissions)).

| Tab | What it does |
| --- | --- |
| Overview | A four-step setup checklist (subscribe what the decoys rely on, choose templates and a policy, place decoys, prove it works), the number of active alert paths and covered sensors, what needs attention, and the latest hits. |
| Hits | Every hit the extension recorded, newest first, over the last 24 hours, 7 days, 30 days or 90 days. Filter by layer, template, host and classification. A hit shows what happened, the evidence, the case it opened and, where the [guards](deception/detections.md#isolation) allow it, **Isolate host** and **Tag host**. |
| Decoys | Every decoy, with filters for state, policy, template, kind and host, and **Verify**, **Rotate** and **Remove**. Test decoys are hidden unless you ask. |
| Coverage | Each alert path (a template on a layer) with its status and what is missing or broken, and **Test fire** with the latest result of every path. |
| Policies | Your policies and templates: add, edit, enable, disable and delete them. A template viewer and editor edit a template as a form or as its JSON, the **Template Library** copies the built-in templates into your configuration, and the whole record can be edited as JSON. |

**Deploy** in the page header shows a preview of what a deploy would do (hosts targeted, decoys to place and retire, shipped rules that are missing or differ) and starts it when you confirm. **Uninstall Deception** in the menu next to it runs the [uninstall](deception/operations.md#uninstalling-before-you-unsubscribe) and shows its status. If your configuration record is disabled, the page says so and offers **Enable configuration**.

## Threat model

Deception is designed to detect an attacker who has a foothold on an endpoint and goes looking for credentials and infrastructure. It assumes:

- The attacker reads files on the host: credential files, config backups, notes, runbooks. AI agents do this systematically, and so do people.
- The attacker then tries what they find: a token against a URL, a kubeconfig against `kubectl`, a username and password against a login page or the identity provider.
- The attacker does not know which files are decoys. File names, the names inside files and the fake services' answers are generated per organization, so the defaults are not a public list of names to skip. Decoys are never placed at a tool's default path (such as `~/.kube/config` or `~/.aws/credentials`), because a normal tool would read them and raise false alerts. They sit at non-default paths that look like leftover copies, which no tool loads unless told to.

What it does not do:

- **It does not prevent anything.** It tells you early. Isolation is an opt-in response, not a guarantee.
- **It is not a defense against an attacker who ignores credential files.** A hit needs the attacker to touch a decoy.
- **It does not hide from someone with read access to your LimaCharlie organization.** Detections, the files on disk, and placement events let an insider with that access learn some decoys. Generated decoy instances and their secrets are kept out of customer-readable configuration, and no request ever returns a secret value, but the residual risk exists.
- **It does not catch a decoy secret used somewhere LimaCharlie cannot see.** For example, an AWS decoy whose keys are copied to another machine without its config file will talk to real AWS, where the keys are invalid and nothing is reported. The read of the file on the original host is still caught.

## What this release covers

Deception ships a deliberately narrow, complete scope:

- **Available:** credential and configuration file decoys, fake MCP and service endpoints, decoy hostnames under LimaCharlie-operated decoy domains, and phantom cloud accounts (UPN form) watched through Entra ID or Okta sign-in logs.
- **Not available in this release, on every layer:** fake Active Directory accounts, and decoy hostnames under your own internal domain. Their templates stay in the library and your configuration still accepts them, but they report as unavailable in `plan`, `coverage` and `test_fire`, and nothing is planted, collected or forwarded for them.
- **Deferred:** an alert when a phantom account signs in **successfully**. Failed sign-ins against a phantom account still alert.

See [Known limitations](deception/limitations.md).

## Requirements

Deception works with what your organization already sends. The extension checks these before it plans a decoy and tells you exactly what is missing, instead of planting a decoy nobody is watching.

| For | You need |
| --- | --- |
| Placing any file decoy | The `ext-artifact` extension subscribed, and a LimaCharlie sensor on the host in a supported mode (see [Sensor modes](deception/decoys.md#sensor-modes-and-what-they-cost)) |
| Read, modify and delete alerts | `ext-exfil` (read) and `ext-integrity` (modify and delete) subscribed, sensors with the file collectors on, and, on Windows, a sensor that reports file events: 5.3.16 or later on the 5.3 line, or 5.4.3 or later (see [Sensor versions](deception/decoys.md#sensor-versions-windows)) |
| Use alerts for credential files, MCP configs, and registry-form hostnames | Nothing else. The destination is LimaCharlie's collector. |
| Phantom accounts, UPN form | The Entra ID adapter with the `sign_ins` source (Entra ID P1 or P2), or the Okta adapter |
| Phantom accounts, AD form | **Not available in this release.** See [Known limitations](deception/limitations.md#not-built). |
| Hostnames under your internal domain | **Not available in this release.** See [Known limitations](deception/limitations.md#not-built). |
| Cases for hits | The `ext-cases` extension, if you want hits to open cases |

The extension never subscribes these for you. `deploy` and `coverage` name any that are missing.

## Enabling the extension

Subscribe to `ext-deception` from the Add-ons marketplace, selecting the organization.

On subscribe, the extension:

- creates a webhook adapter named `ext-deception` in the organization. Confirmed hits arrive through it as `deception_hit` events.
- writes its own plumbing rules in `dr-service` (names start with `ext-deception-`) and installs the default detection rules in your `dr-general` hive (names start with `deception-`). A default rule is installed only when missing. An edited rule is never overwritten.
- places nothing. No decoy goes on any host until you write and enable a policy that selects templates. After that, decoys are placed by `deploy`, by the daily run on matching sensors that lack them, and when a new sensor connects to a policy that sets `setup_on_new_sensors`.
- does not enable your configuration record. The extension never writes it. See [Enabling the configuration record](deception/configuration.md#enabling-the-configuration-record).

Then subscribe the extensions your decoys depend on (`ext-artifact`, `ext-exfil`, `ext-integrity`, and optionally `ext-cases`).

## Quick start

1. Read the available kinds and the default library:

    ```bash
    limacharlie extension request --name ext-deception --action list_kinds --oid "$OID"
    ```

2. Copy the templates you want from the `library` array in the answer into the `templates` list of your `ext-deception` extension configuration, and add a policy that selects them. A minimal configuration:

    ```yaml
    schema_version: 1
    templates:
      - schema_version: 1
        kind: file
        kind_version: 1
        name: kubeconfig-backup
        tags: [credentials]
        enabled: true
        spec: {}   # replace with the spec from the library entry
    policies:
      - schema_version: 1
        name: linux-servers
        enabled: true
        targeting:
          platforms: [linux]
          tags: [prod]
        templates:
          select_tags: [credentials]
        setup_on_new_sensors: true
        responses:
          isolate: false
    ```

    `spec: {}` above is a placeholder: copy the full `spec` of the library entry. See [Configuration](deception/configuration.md). In the web app, **Policies** > **Template Library** does the copy for you.

    ```bash
    limacharlie extension config-set --name ext-deception --input-file deception.yaml --oid "$OID"
    ```

    A record saved this way is disabled until you enable it, and requests that read your policies refuse with "the ext-deception configuration is disabled" meanwhile. Enable it once:

    ```bash
    limacharlie hive enable --hive-name extension_config --key ext-deception --oid "$OID"
    ```

3. See what `deploy` would do, then do it:

    ```bash
    limacharlie extension request --name ext-deception --action plan --oid "$OID"
    limacharlie extension request --name ext-deception --action deploy --oid "$OID"
    ```

4. Check what is covered, and check the synthetic detection path (`test_fire` does not prove your real-alert rules, cases or isolation, and its results are final about an hour after the run starts; see [Test-fire](deception/detections.md#test-fire)):

    ```bash
    limacharlie extension request --name ext-deception --action coverage --oid "$OID"
    limacharlie extension request --name ext-deception --action test_fire --oid "$OID"
    ```

Before you unsubscribe, run [`uninstall`](deception/operations.md#uninstalling-before-you-unsubscribe), then check it with `uninstall_status` until it reports `safe_to_unsubscribe`.
