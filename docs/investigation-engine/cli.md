# Command Line Interface

The `limacharlie investigate` command group is the CLI for the Investigation Engine:
build and test templates, start and follow runs, work the approvals inbox, and manage
the pause switch.

!!! info "Pre-release"
    The `investigate` group ships with a CLI release that follows the Investigation
    Engine pre-release. Check that your CLI has it, and see the exact flags of your
    version, with:

    ```bash
    limacharlie investigate --help
    limacharlie investigate templates test --help
    ```

    Every command and subgroup also answers `--ai-help` with task-oriented guidance.

Commands take the global options (`--oid`, `--output json|yaml|toon|csv|table|jsonl`,
`--filter <jmespath>`, `--fields <names>`). Use the organization's UUID for `--oid`.
The permissions each command needs are the ones of the corresponding
[API route](api-reference.md#routes).

A command that completes but says "no" (an invalid template, a refused save, a refused
promotion) prints the engine's coded answer and **exits with code 4**. Other failures
exit with 1.

```bash
export OID=<organization UUID>
```

## Templates

```bash
# What the organization has, and what the default library offers
limacharlie investigate templates list --oid $OID
limacharlie investigate templates list --status active --oid $OID
limacharlie investigate templates get suspicious-process --yaml --oid $OID

# Install the default library (written as drafts unless you say otherwise)
limacharlie investigate templates install-defaults --oid $OID
limacharlie investigate templates install-defaults --name suspicious-process --oid $OID
```

| Command | What it does |
|---|---|
| `templates list [--status draft\|active]` | The organization's templates: name, version, description, `applies_to`, status. |
| `templates get NAME [--yaml]` | A stored template record. `--yaml` prints only the source. |
| `templates validate -f FILE` | Checks a template (`-` for stdin) and runs nothing. Exit 4 when it has errors. |
| `templates test [NAME] -f FILE ...` | Dry run on past alerts. See below. |
| `templates save NAME -f FILE` | Validates, then saves a **draft** record. Exit 4 when refused. |
| `templates promote NAME --confirm` | Makes a reviewed draft **active**. A person's decision. |
| `templates delete NAME --confirm` | Deletes the record. |
| `templates install-defaults` | Writes the [default library](templates.md#the-default-library) into the organization. |

**`templates install-defaults`** never overwrites silently: a template that already
exists is skipped unless you pass `--overwrite`. `--name` (repeatable) installs only
the templates you name. `--status` is the status the templates are written with,
whatever the library says; the CLI default is `draft`, so review and promote what you
want to run on its own.

**`templates save`** writes a draft. `--comment` stores what the template was tested on
and how it did as the record's comment, `--tag` (repeatable) adds tags, and
`--overwrite` replaces an existing draft. An AI agent leaves `--status` at its default,
`draft`. Writing an active template is a person's decision, and the Hive refuses it
from an API key (see [Permissions](permissions.md#active-templates-can-only-be-written-by-a-person)).

**`templates promote`** requires `--confirm` and the permissions of a person who
reviewed the draft.

### Testing a template on past alerts

```bash
# The newest 15 detections of a category
limacharlie investigate templates test -f plan.yaml \
  --detect-cat rare-process --last 15 --oid $OID

# Specific detections and a closed case (its classification is the expected answer)
limacharlie investigate templates test -f plan.yaml \
  --detection-id <detect id> --case-id <case id> --oid $OID

# A stored template, with a free-form sample
limacharlie investigate templates test host-activity \
  --sample '{"inputs": {"msg_uuid": "..."}, "expected": "false_positive"}' --oid $OID
```

| Flag | Meaning |
|---|---|
| `NAME` or `-f FILE` | A stored template, or a template file (`-` for stdin). |
| `--detection-id`, `--case-id` | A sample (repeatable). |
| `--detect-cat` with `--last N` | The newest N alerts of the category (1 to 25, default 10). |
| `--sample JSON`, `--samples-file FILE` | Free samples. At most 25 alerts in all. |
| `--mode triage\|full` | `triage` (the default, the cheap pass) or `full`. |
| `--strict` | Treat any unknown as a failure of the plan. |
| `--overrides-json JSON` | Tighten-only overrides, such as `{"budgets": {"max_wall_seconds": 120}}`. |
| `--wait SECONDS`, `--timeout SECONDS`, `--no-wait` | How long the start call and the whole command wait. `--no-wait` prints the `test_id` and returns. |
| `--test-id ID` | Keep waiting on a test started earlier. |
| `--include-steps` | Keep every step of every sample (large). By default only the steps that did not succeed. |

The result is the one described in [Test on past alerts](templates.md#test-on-past-alerts):
per sample the verdict, proof, unknowns, cost and agreement with the case, and a summary.

## Authoring helpers

```bash
limacharlie investigate kit --section guide --section schema --section codes --oid $OID
limacharlie investigate operators --match mailsec --brief --oid $OID
limacharlie investigate packs --brief --oid $OID
```

| Command | What it does |
|---|---|
| `kit [--section S]...` | The authoring kit. Sections: `schema`, `guide`, `operators`, `examples`, `policy`, `codes`, `packs`, `library`. Without `--section`, everything but `library` (about 33,000 tokens). |
| `operators [--match TEXT] [--name NAME]... [--brief]` | The typed operator catalog. |
| `packs [--name NAME] [--brief]` | The fact packs. `--brief` is the compact index. |

## Waves

```bash
limacharlie investigate wave -f wave.yaml --oid $OID
limacharlie investigate wave -f wave.yaml --validate-only --oid $OID
```

`wave.yaml` (or JSON) has the fields of the [wave request](api-reference.md#waves):
`steps`, `stop_when`, `deadline_ms`, `inputs`. The flags `--stop-when` (repeatable, up to
8), `--deadline-ms` and `--input KEY=VALUE` add to the file, `--full` returns raw
values, and `--validate-only` validates and runs nothing.

## Runs

```bash
limacharlie investigate runs start --template suspicious-process \
  --detection-id <detect id> --wait 30 --oid $OID
limacharlie investigate runs list --state running --oid $OID
limacharlie investigate runs events <run id> --follow --oid $OID
limacharlie investigate runs case <run id> --oid $OID
```

| Command | What it does |
|---|---|
| `runs start` | Starts a run on `--detection-id`, `--case-id`, `--entity-id` or `--question`, with `--template NAME` or a template file `-f`. `--input KEY=VALUE` and `--inputs-json` give run inputs; `--mode triage\|full\|scope`; `--case-mode create\|none\|attach:<id>`; `--idempotency-key`; `--wait SECONDS` (up to 60) to block for the verdict; `--follow` to stream events until the run ends. |
| `runs get RUN_ID` | State, phase, verdict, actions and usage. |
| `runs list` | The organization's runs, newest first. Filters `--state`, `--verdict`, `--template`, `--trigger`, `--entity`, `--started-by`, `--idempotency-key`, `--since`, `--until`; `--limit` and `--cursor` page; `--all` follows every page. |
| `runs events RUN_ID` | The run's events after `--after`. `--follow` keeps polling until the run is over, one event per line. It exits 0 when the run finished and 1 when `--timeout` is reached. |
| `runs steps RUN_ID [--values]` | The step log, plan graph, usage and belief curve. `--values` includes customer values; by default the output is structure only. |
| `runs case RUN_ID` | The case document the run wrote. |
| `runs cancel RUN_ID [--revert-leases]` | Cancels a run, and optionally reverts the leases of its active actions. |

A run started with a draft template runs with autonomy capped at `suggest`.

## Approvals and the pause switch

```bash
limacharlie investigate actions list --state awaiting_approval --oid $OID
limacharlie investigate actions approve <run id> <action id> --oid $OID
limacharlie investigate actions deny <run id> <action id> --note "Expected maintenance" --oid $OID

limacharlie investigate policy get --category rare-process --priority 5 --oid $OID
limacharlie investigate policy status --oid $OID
limacharlie investigate policy pause --oid $OID
limacharlie investigate policy resume --oid $OID
```

| Command | What it does | Needs |
|---|---|---|
| `actions list [--state S] [--class C] [--run-id ID]` | The approvals inbox, what needs a person first. `--limit`, `--cursor`, `--all` page. | read |
| `actions approve RUN_ID ACTION_ID` | Approves an action. | write, plus the action class's permission |
| `actions deny RUN_ID ACTION_ID [--note TEXT]` | Denies an action. | same |
| `policy get [--category] [--priority] [--severity] [--target-tag]... [--class]` | The effective policy, record by record, for those attributes. | read |
| `policy status` | Whether automatic actions are paused. | read |
| `policy pause`, `policy resume` | Stops or allows every automatic action in the organization. | `org.conf.set` |

Policies and templates themselves are Hive records. Create and edit them with the
standard `limacharlie hive` commands for the `investigation_plan` and
`investigation_policy` types, or with infrastructure-as-code.
