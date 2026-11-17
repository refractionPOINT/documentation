# Deception

!!! warning "Early release"
    Deception has not been validated on a broad set of real hosts and identity tenants yet. Statements below that depend on real endpoint or log-source behavior are marked **not verified**. Read [Known limitations](deception/limitations.md) before relying on it as a primary control.

Deception plants unique decoys on your endpoints through the LimaCharlie sensor: credential files, service and MCP configuration files, notes naming decoy hostnames, and notes holding phantom accounts. Nothing legitimate has a reason to touch a decoy, so a decoy that is read or used is a high-fidelity signal. A hit becomes a priority 10 detection, opens a critical case, and can isolate the host.

It is built mainly to catch AI-driven attackers early. An AI agent that lands on a host reads every credential file it finds, tries every key and follows every breadcrumb, usually within minutes. A human attacker who goes through the same files trips the same decoys.

## What it does

Every decoy raises alerts on one or both of two things:

- **Read.** The decoy file was opened, modified, or deleted. The sensor reports this.
- **Use.** A secret inside the decoy was used. Every secret carries its own destination, and the destination is LimaCharlie's: a decoy Kubernetes config points at a fake API server, a decoy AWS profile points its endpoint at a fake AWS API, a decoy `.env` names fake internal services. Phantom accounts are usernames that exist nowhere, so a sign-in attempt with one shows up in logs you already send to LimaCharlie.

Each secret in each decoy is generated per decoy and per host. A hit therefore names the machine the secret was planted on, even when the secret is used from somewhere else.

Deception is self-serve. It never creates accounts, mailboxes, cloud keys, or DNS records in your systems, and it never subscribes your organization to another extension or changes a sensor's mode on your behalf.

## How it works

1. You subscribe to the extension and describe what you want in its configuration record: **templates** (what each decoy looks like) and **policies** (which templates go on which sensors, and what to do on a hit). LimaCharlie ships a default [template library](deception/decoys.md#default-template-library); nothing in it is placed until you copy a template into your own configuration.
2. `deploy` places decoys through sensor tasking. A decoy counts as covered only after the extension checks the file's hash on the host. A task acknowledgement alone is not proof.
3. Decoy reads reach the cloud through rules the extension writes in other extensions' configurations (Exfil watch rules, Integrity FIM rules) and its own rules. Decoy use reaches the cloud through a public LimaCharlie-operated collector, or through the sign-in logs you already send.
4. Every candidate event is checked against a registry of the decoys the extension planted. Only a confirmed match becomes a `deception_hit` event. Everything else is dropped.
5. The default detection rules turn `deception_hit` events into detections, and, if you opted in, a guarded isolation of the host.

See [Decoys and coverage](deception/decoys.md), [Configuration](deception/configuration.md), [Requests](deception/requests.md), [Detections, cases and response](deception/detections.md), [Operations](deception/operations.md) and [Known limitations](deception/limitations.md).

## Threat model

Deception is designed to detect an attacker who has a foothold on an endpoint and goes looking for credentials and infrastructure. It assumes:

- The attacker reads files on the host: credential files, config backups, notes, runbooks. AI agents do this systematically, and so do people.
- The attacker then tries what they find: a token against a URL, a kubeconfig against `kubectl`, a username and password against a login page or the identity provider.
- The attacker does not know which files are decoys. File names come from a vocabulary generated per organization, so the defaults are not a public list of names to skip. Decoys are never placed at a tool's default path (such as `~/.kube/config` or `~/.aws/credentials`), because a normal tool would read them and raise false alerts. They sit at non-default paths that look like leftover copies, which no tool loads unless told to.

What it does not do:

- **It does not prevent anything.** It tells you early. Isolation is an opt-in response, not a guarantee.
- **It is not a defense against an attacker who ignores credential files.** A hit needs the attacker to touch a decoy.
- **It does not hide from someone with read access to your LimaCharlie organization.** Detections, the files on disk, and placement events let an insider with that access learn some decoys. Generated decoy instances and their secrets are kept out of customer-readable configuration, and no request ever returns a secret value, but the residual risk exists.
- **It does not catch a decoy secret used somewhere LimaCharlie cannot see.** For example, an AWS decoy whose keys are copied to another machine without its config file will talk to real AWS, where the keys are invalid and nothing is reported. The read of the file on the original host is still caught.

## Requirements

Deception works with what your organization already sends. The extension checks these before it plans a decoy and tells you exactly what is missing, instead of planting a decoy nobody is watching.

| For | You need |
| --- | --- |
| Placing any file decoy | The `ext-artifact` extension subscribed, and a LimaCharlie sensor on the host in a supported mode (see [Sensor modes](deception/decoys.md#sensor-modes-and-what-they-cost)) |
| Read, modify and delete alerts | `ext-exfil` (read) and `ext-integrity` (modify and delete) subscribed, and sensors with the file collectors on |
| Use alerts for credential files, MCP configs, and registry-form hostnames | Nothing else. The destination is LimaCharlie's collector. |
| Phantom accounts, UPN form | The Entra ID adapter with the `sign_ins` source (Entra ID P1 or P2), or the Okta adapter |
| Phantom accounts, AD form | `ext-exfil` subscribed, a sensor on every domain controller, failure auditing on, and `dc_logon_collection` set in the policy |
| Hostnames under your internal domain | At least one Windows sensor |
| Cases for hits | The `ext-cases` extension, if you want hits to open cases |

The extension never subscribes these for you. `deploy` and `coverage` name any that are missing.

## Enabling the extension

Subscribe to `ext-deception` from the Add-ons marketplace, selecting the organization.

On subscribe, the extension:

- creates a webhook adapter named `ext-deception` in the organization. Confirmed hits arrive through it as `deception_hit` events.
- writes its own plumbing rules in `dr-service` (names start with `ext-deception-`) and installs the default detection rules in your `dr-general` hive (names start with `deception-`). A default rule is installed only when missing. An edited rule is never overwritten.
- places nothing. No decoy goes on any host until you write a policy and run `deploy`, or a new sensor connects to a policy that sets `setup_on_new_sensors`.

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

    `spec: {}` above is a placeholder: copy the full `spec` of the library entry. See [Configuration](deception/configuration.md).

    ```bash
    limacharlie extension config-set --name ext-deception --input-file deception.yaml --oid "$OID"
    ```

3. See what `deploy` would do, then do it:

    ```bash
    limacharlie extension request --name ext-deception --action plan --oid "$OID"
    limacharlie extension request --name ext-deception --action deploy --oid "$OID"
    ```

4. Check what is covered, and prove the alert paths work:

    ```bash
    limacharlie extension request --name ext-deception --action coverage --oid "$OID"
    limacharlie extension request --name ext-deception --action test_fire --oid "$OID"
    ```

Before you unsubscribe, run [`uninstall`](deception/operations.md#uninstalling-before-you-unsubscribe).
