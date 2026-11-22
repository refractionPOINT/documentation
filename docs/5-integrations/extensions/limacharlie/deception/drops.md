# Deception: Tokens (Drops)

A **token** is a decoy that no sensor places: a link, a QR code, a hostname or a document that you put where an intruder would look, such as a wiki page, a ticket, an email, a printed badge or a file share. The web app calls them **Tokens**. The API, the configuration and the CLI call them **drops**. A hit on a token names the label you gave it, not a machine.

Tokens need no sensor and no other extension. They are included with a Deception subscription.

## Forms

| Form | What you get | What raises a hit |
| --- | --- | --- |
| `url` | A link under a LimaCharlie-operated decoy domain. | Any request to the link, from anywhere. The visitor sees a sign-in page, or is sent on to a page you choose (see [Redirects](#redirects)). |
| `qr` | A QR code (SVG) that encodes the token's own link. | The link being opened. A QR token has its own value, so a hit tells a scanned badge apart from a pasted link. |
| `hostname` | A host name under a decoy domain. | An HTTP or HTTPS request to the name, from anywhere, or a DNS lookup of the name reported by one of your organization's sensors. A lookup made from a machine outside your organization is not seen, and neither is SSH, RDP or SMB to the name (only web ports answer). |
| `document` | A Word (`docx`) or SVG (`svg`) document to download. | The document being opened in a viewer that loads its linked image (see [Documents](#documents)). |

### Documents

A document token calls home when a viewer loads a linked image inside it. What loads it depends on the viewer:

- **Word (`docx`)**: desktop Word on Windows and macOS loads the image without asking when the file is opened. A file that carries the "downloaded from the internet" mark opens in Protected View and fetches nothing until the reader clicks **Enable Editing**. Files copied off a host with tools such as `scp`, `rclone` or SMB usually carry no such mark. Word for the web, mobile apps and preview panes are **not verified** and probably fetch nothing.
- **SVG (`svg`)**: fires when the file is opened in a web browser, which is what double-clicking an `.svg` file does on most desktops. It never fires as an embedded image or a thumbnail. Mail gateways often block SVG files, so use it on file shares and desktops, not in email.

Excel and PDF documents are not offered in this release (`format_unavailable`). No viewer has been tested in a lab for this release: the behavior above comes from vendor documentation and published research, and is **not verified**. The same document format is also available for decoys placed on hosts, through the `document` [kind](decoys.md#decoy-kinds).

## Create a token

From the web app: **Deception** > **Tokens** > **Create token**. From the CLI:

```bash
limacharlie extension request --name ext-deception --action create_drop \
  --data '{"form":"url","label":"finance wiki: payroll page","memo":"pasted in the payroll space"}' \
  --oid "$OID"
```

The answer holds the token (`drop`) and what to put where it goes (`paste`): `url` for the url and qr forms, `qr_svg` for a QR code, `hostname`, or `document` (`filename`, `content_type`, `content_b64`, `sha256`). These three requests (`create_drop`, `get_drop`, `rotate_drop`) are the only ones that return a secret value, because the value is what you paste. `list_drops` never returns it.

| Field | Meaning |
| --- | --- |
| `form` | `url`, `qr`, `hostname` or `document`. Fixed once the token exists. |
| `label` | Where you put it, at most 128 characters (and 253 bytes), one line. The case for a hit shows it where a host name usually is. It is never written into the token, its page or the document. |
| `memo` | Notes for the analyst, at most 1,024 characters. |
| `format` | Documents only: `docx` or `svg`. |
| `domain` | One of the deployment's decoy domains. Default: the first. [Custom domains](configuration.md#custom-domains) are not used. |
| `redirect_url` | url and qr only. See [Redirects](#redirects). |
| `mode`, `observe_until` | `live` (default) or `observe`. See [Observe mode for tokens](#observe-mode-for-tokens). |

## Declare tokens in the configuration

To manage tokens as code across many organizations, declare them in the `drops` list of the same `ext-deception` configuration record that holds your policies and templates:

```yaml
drops:
  - name: finance-wiki-payroll
    form: url
    label: "finance wiki: payroll page"
    redirect_url: https://intranet.example.com/payroll
  - name: lobby-badge
    form: qr
    label: lobby visitor badge
  - name: vpn-howto
    form: document
    format: docx
    label: "IT share: VPN setup"
    mode: observe
    observe_until: "2026-12-15T00:00:00Z"
```

- `name` is the key: unique in the list, 1 to 64 lowercase letters, digits, `.`, `_` or `-`, starting with a letter or digit. The other fields are the ones of `create_drop`, plus `state` (`active`, the default, or `disabled`). `name`, `form` and `label` are required.
- Each time the record changes, the extension makes the organization's named tokens match the list: a new name creates its token with its own secret, a changed entry updates it, and a removed entry deletes it (it stops alerting at once). Renaming an entry deletes the old token and creates a new one.
- A name that comes back within 90 days of its token's deletion gets the same token and secret back, so reverting a commit revives copies already pasted or printed. After 90 days the name creates a new token.
- `form`, `format` and `domain` cannot change. An entry that changes one is refused with `drop_config_immutable`: give it a new name.
- An entry that is malformed, or that this deployment cannot serve (an unknown domain or format, a redirect target that is not an acceptable public `https` URL), refuses the whole record when it is saved (code `invalid_config`, each problem naming its field). A disabled or unreadable record never deletes a token.
- Some problems are found only when the list is applied, entry by entry, and do not stop the other entries: a change of `form`, `format` or `domain` on an existing token (`drop_config_immutable`), a redirect target Google Web Risk lists or could not check, and the token limit. Those entries are left as they were and reported in `blocked` (in the answer of `deploy` and the daily run, and in `plan` as `drops.blocked` with `drops.sync: blocked`), while the other entries are applied. After a push, check `plan` until `drops.sync` is `applied`.
- Tokens made with `create_drop` or the web app have no name and are never touched by the list. A token the list declares cannot be edited or deleted with `update_drop` or `delete_drop` (`drop_config_managed`): change its entry instead. `rotate_drop` and `test_fire` work on it.
- Read a declared token's link, host name, QR code or document with `get_drop` and its `name`:

    ```bash
    limacharlie extension request --name ext-deception --action get_drop \
      --data '{"name":"finance-wiki-payroll"}' --oid "$OID"
    ```

- `plan` shows what the next sync would create, restore, update and delete (`drops.pending`), whether the list is applied (`drops.sync`: `applied`, `pending`, `running` or `blocked`), and how many pending creates would not fit under the [limit](#limits) (`drops.cap`). `deploy` and the daily run apply the list again and report what they did (`drops`: `created`, `restored`, `updated`, `deleted`, `blocked`).
- A large list is applied in bounded passes (about 20 seconds and 2,000 token writes each). The configuration change runs the first pass, and the rest is picked up by the 30-minute sweep, so thousands of new tokens can take up to about 30 minutes to all exist. Wait for `drops.sync: applied` in `plan` before handing out their links or documents.

The list holds at most 10,000 entries; the record's 1 MB size limit is usually reached first, at a few thousand. Creates count toward the organization's token limit and hourly create rate. An entry that does not fit because of tokens made in the web app is reported (`drop_cap`) and created by the next `deploy` or daily run once there is room.

## Limits

| Limit | Value | Refusal code |
| --- | --- | --- |
| Tokens per organization (active and disabled) | 100,000 | `drop_cap` |
| Token creations per organization per hour | 10,000 | `drop_rate` |
| Unexpired values per token (the current one and rotated ones) | 4 | `drop_rotations` |
| Redirect target checks per organization | 10,000 an hour, 1,000 a minute | `target_check_rate_hour`, `target_check_rate_minute` |
| `drop_preview_match` entries | 50 | `invalid_config` |

LimaCharlie can raise or lower the token and target-check limits for an organization. Hidden test tokens (below) count toward neither.

## Redirects

A url or qr token can send the visitor on to a page you choose after the hit is recorded, so the link looks real. Without a redirect the visitor sees a sign-in page, so a curious person who types a password produces a second, richer hit.

- The target must be a public `https://` URL of at most 2,048 bytes: no IP address, no `localhost`, no single-label or private-use name (such as `.local`, `.internal` or `.corp`), no user name or password, nothing under a decoy domain, and a port from 1 to 65535. An international host name is stored in punycode. A target that breaks a rule is refused with `redirect_invalid`, and the text says why.
- Every time a target is written (on create, and on an update that changes it), it is checked with **Google Web Risk**. A target listed as malware, social engineering or unwanted software is refused (`redirect_flagged`). If the check cannot be made right now the write is refused too (`redirect_check_unavailable`): try again later. An unchanged target, removing a target (`""`), rotating, disabling and deleting cost no check.
- Each check first takes one of the organization's target checks (10,000 an hour, 1,000 a minute), and counts even when the target is flagged or the check fails. A target shared by many organizations costs one check in each.
- A stored target is not checked again later: a page that becomes malicious after you saved it stays the target until you change or remove the redirect. Editing the label or saving the same target again does not check it again.
- A changed or removed redirect takes effect within a minute. A disabled token keeps its redirect, so a printed badge keeps working.

## Link previews and mail scanners

Chat apps and mail gateways fetch every link they see before a person does. Those fetches are real requests, and some come from infrastructure an attacker could use too, so they are recorded and still raise a detection, at a lower priority:

| Classification | When | Default rule |
| --- | --- | --- |
| `scanner-likely` | A known scanner User-Agent or scanner network. | `deception-drop-preview`, priority 3 |
| `link-preview-likely` | A known link unfurler or link checker (Slack, Teams, LinkedIn, Discord, Telegram, WhatsApp, Bing and Google previewers, among others), an entry of your own `drop_preview_match`, or, for url and qr tokens, a `HEAD` request or a request without the headers a browser sends when a person navigates. | `deception-drop-preview`, priority 3 |
| `human-likely` with `details.proxied: true` | An image proxy such as Gmail's fetched a document's image for a person who opened the email. The source address is the proxy's. | `deception-drop-alert`, priority 10 |
| Otherwise | `ai-agent-likely`, `automated`, `human-likely` or `unknown`, as for decoys on hosts. | `deception-drop-alert`, priority 10 |

Mail security sandboxes that run a real browser (link detonation) look like a person and raise a critical hit. Before you mail a token through a gateway that rewrites or opens links, create it in observe mode, send one test message, add what fetched it to your preview list, then switch the token to live.

**Your own preview list.** `drop_preview_match`, a top-level field of the configuration record, lists what fetches your tokens with no person behind it. A matching hit is `link-preview-likely`:

```yaml
drop_preview_match:
  - user_agent: examplemailgateway
    comment: our mail link scanner
  - cidr: 203.0.113.0/24
    comment: mail gateway egress
```

An entry sets `user_agent` (a case-insensitive substring of at least 3 characters), `cidr` (at least /8 for IPv4, /16 for IPv6) or both, and every field it sets must match. At most 50 entries.

## Observe mode for tokens

A token in `mode: observe` records its hits and reports them at priority 3 (a medium case) with no automatic response, so you can see what fetches it before it goes live. With `observe_until` (an RFC 3339 time) it turns live by itself at that time. `observe_until` is refused on a live token (`observe_until_live`). Setting `mode: live` clears it.

## What a hit looks like

A token hit is a `deception_drop_hit` event, through the same `ext-deception` adapter as decoy hits. It uses the [`deception_hit` envelope](detections.md#the-deception_hit-event), with these differences:

| Field | Value |
| --- | --- |
| `drop_id`, `decoy_id` | The token's id. |
| `label` | The token's label. |
| `kind` | `token` (url, qr, hostname) or `document`. |
| `template` | `drop:url`, `drop:qr`, `drop:hostname` or `drop:document`. |
| `layer` | `use`. A document's hit has `details.signal: "opened"`. |
| `sid`, `hostname`, `policy` | Empty: a token is on no machine. |
| `reporting_sid` | The sensor that reported a DNS lookup of a hostname token, else empty. |
| `on_host` | Always `false`. |
| `mode` | `observe` or `live`. |
| `details` | `memo`, `form`, `format`, `referer` (url and qr; browsers often send only the site's origin), `geo` (country, region and city from the load balancer, when available), `method`, `answer` (`page`, `redirect` or `pixel`) and `proxied`. |

Your existing rules that match `deception_hit` do not match token hits. The two shipped token rules install themselves:

| Rule | Matches | Does |
| --- | --- | --- |
| `deception-drop-alert` | A real token hit, live, not `link-preview-likely` or `scanner-likely` | Report `deception.<kind>.use`, priority 10 |
| `deception-drop-preview` | A real token hit that is `link-preview-likely`, `scanner-likely`, or in observe mode | Report, priority 3 |

## Cases and response

With `ext-cases` subscribed, a token hit opens one case per token and incident. The case is filed with no sensor and shows the token's label as its host name (the web app shows "(no sensor)"). Priority 10 opens a critical case, priority 3 a medium one.

There is no machine to isolate, so `respond` refuses to isolate or tag on a token hit (`no_endpoint`). A hostname token looked up by one of your sensors names that sensor in `reporting_sid`, but never isolates it automatically: looking a name up is weak evidence (a mail scanner resolves links too). An analyst can isolate that sensor by hand. Notification outputs and `start ai agent` responses in your own rules work as for any detection.

## Lifecycle

| Action | Request | Effect |
| --- | --- | --- |
| Edit | `update_drop` with `drop_id` and the `version` you read | Label, memo, redirect, state, mode. A stale version is refused (`drop_version_conflict`): read the token again. |
| Disable | `update_drop` with `state: disabled` | Hits are not recorded and the token answers exactly as before, so an attacker learns nothing. It still counts toward the limit. |
| Rotate | `rotate_drop` with `drop_id` and `version` | A new value to paste. The old one keeps alerting for 90 days, because it was handed out. |
| Delete | `delete_drop` with `drop_id` | Its values stop alerting at once and its redirect goes. The record stays 90 days, so past hits keep their label. Not reversible, except by a configuration entry coming back (above). |

The token stays wherever you put it. Deleting it stops the alerts. Remove it from the wiki, ticket or share too.

Page through tokens with `list_drops` (filters `forms`, `states`, `text`, `name`, `managed_by` (`config` or `api`) and `include_test`, applied before paging, newest first). Every token carries `managed_by` and, for a declared token, its `name`.

## Testing and coverage

The first time your organization creates a token of a form, the extension makes a hidden test token of that form, and the daily test-fire fires each one through an internal collector path. `test_fire` with a `drop_id` fires one token now (the web app's **Send a test hit**). Test hits are `deception_hit` events with `synthetic: true`: they show in the token's hits as test hits and never open a case.

`coverage` returns `drops`: one row per form your organization uses, `active`, `broken` (its latest test found no detection, or a token rule is missing or disabled) or `unverified` (a token rule was edited, or could not be checked). There is no per-token coverage: a token has nothing that can break on its own. A test proves the path from the collector to a detection, not that anyone will read the place where you put the token.

## Uninstall and billing

The [uninstall](operations.md#uninstalling-before-you-unsubscribe) removes the rules and the adapter, so tokens go silent, but it does not remove them from where you put them. After an unsubscribe a token's redirect keeps working until the organization's stored data is purged, so a printed QR code does not break the moment someone unsubscribes by mistake.

Tokens are included with a Deception subscription. The daily report carries an `active_drops` count (active tokens, test tokens excluded) as `ext-deception:active_drops`, with no price attached.
