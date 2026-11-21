# Design Considerations & Gotchas

An extension that works for one organization in a demo can still fail its first real customer. This page covers what to decide before that happens: tenancy, security, state, availability and change. It ends with a checklist of the gotchas that catch extension authors most often, each linked to the page with the details.

## Multi-Tenancy

One deployment of your extension serves every subscribed organization. Every request names its organization (`params.Org.GetOID()` in Go), and everything your extension keeps has to be keyed on it.

- **Key every cache and every stored record on the organization ID.** A vendor client, a parsed configuration or a cursor cached under a key that leaves out the organization will sooner or later be served to the wrong customer. Include a hash of the credential in client cache keys too, so a rotated secret gets a new client.
- **Expect very different organizations.** Some have ten sensors, some have a hundred thousand. Some managed-service providers subscribe thousands of organizations at once. Page through everything, bound the size of what you load into memory, and never assume a list call returns everything in one response.
- **Stop one organization from starving the others.** If a single customer can queue an hour of work, limit concurrency per organization inside your service. The platform's own protection is coarse: when an organization's calls keep failing, it stops sending that organization's requests for a while, and when most organizations are failing, it stops sending to your extension altogether. Callers then get `EXTENSION_UNAVAILABLE` immediately.
- **Test with two organizations.** The [simulator](testing.md#testing-against-the-limacharlie-api) can run several organizations against one extension, each with its own configuration and mock API. It is the cheapest way to find state leaking between tenants.

Many customers manage their organizations through infrastructure as code. Everything your extension does should follow from its configuration, which they can declare, review and roll out to thousands of organizations. Avoid behaviour that depends on hidden state, a per-organization setup step, or a manual action in the UI.

## Security

Your extension is an HTTPS endpoint anyone on the internet can reach, holding credentials for many customers' organizations.

**Authenticate every call.** The SDKs check the `lc-ext-sig` signature and reject a mismatch. In Python, passing `secret=None` turns the check off, so never do that outside a test. Keep the shared secret in a secret store, and treat it like a credential to every subscribed organization, because a signed request is what makes your extension act.

**Treat request data as untrusted.** Requests from D&R rules carry values templated from events, and events come from endpoints and third-party products an attacker may control. The platform type-checks only the top level of a request. It does not enforce `filter` constraints or anything inside `object` and `record` fields (see [Schema & Data Types](schema-data-types.md#the-schema-is-enforced)). Validate in your handler anything your code depends on. In particular:

- Escape values you put into a vendor query, a shell command or a file path.
- If an action takes a URL or hostname, decide which destinations are allowed. Otherwise your extension can be pointed at internal services on its own network.
- Keep the SDK's request body limits, or lower them to the largest request you actually expect.

**Ask for as few permissions as you can.** Each subscribed organization grants every permission in your definition to your extension's key. Leave the [`segment` flair](building-extensions.md#flairs) on unless you need to touch resources you did not create.

**Use impersonation where the caller's rights matter.** An action that is not impersonated runs with your extension's permissions, whoever calls it. If an action returns or changes something a particular user should only reach with their own access, make it [impersonated](runtime-contract.md#impersonation).

**Respect Resource ACLs.** When an action acts on many sensors, the request's `acl` block says which scopes your key holds. Use it to skip what the organization has not opened to you. See [Getting Started](building-extensions.md#rules-your-extension-installs-and-resource-acls).

**Do not keep tokens.** Each call hands you a short-lived token for the organization, valid for at least about 30 minutes from receipt. Use it during the call. Do not store it for background work; continuations arrive with a fresh one.

**Never log secrets.** Resolved `secret` fields arrive in plaintext. Mask them before logging configuration (`MaskSecrets` in the Go SDK).

## Credentials for Third-Party Services

Declare third-party credentials as [`secret`](schema-data-types.md#secrets) fields and let customers keep them in their own secrets manager. Two details are easy to miss:

- **Secrets are only resolved on requests.** On requests, the platform replaces a `hive://secret/<name>` reference with the value before calling you. Event callbacks (`subscribe`, `unsubscribe`, `update`) and `ValidateConfig` receive the configuration as stored, with references unresolved. Do credentialed work from a request action. From an event handler, schedule a continuation to one.
- **A segmented extension cannot read the customer's secrets directly.** With the `segment` flair on, your key can only read records it created. Resolving a reference yourself (for example with `UseSecretValue` in Go) then fails for a secret the customer created. The platform-side resolution on requests is not affected, which is one more reason to do this work in requests.

Do not ask customers to paste credentials into a `string` field, and do not store vendor credentials in your own database if the secrets manager can hold them. Customers then rotate and revoke them in one place they control.

## State

Decide where each kind of state lives. The options, from simplest:

| Where | Good for | Limits |
| --- | --- | --- |
| The extension's configuration | Settings the customer chooses | One record per organization, up to 1 MB. Users can edit it, and every write goes through your `ValidateConfig` |
| Records your extension creates in the organization (rules, lookups, other Hive records) | Resources that must live in the organization | Visible to and editable by the customer. Tag them so you can find your own |
| Continuation state and investigation context | Cursors and progress for a job in flight | Travels with the call. Keep it small |
| Your own database, keyed on organization ID | Large or high-volume data, history, deduplication markers | You run it, back it up, and delete from it |

Things that follow from this:

- **The configuration outlives the subscription.** Unsubscribing does not delete the extension's configuration record, so a customer who subscribes again gets their old settings back. Do not rely on the configuration being empty on `subscribe`.
- **`ValidateConfig` runs on every write**, including writes your extension makes to its own configuration, and it runs with your extension's credentials rather than the user's. It has about a minute. If your extension is down, nobody can save its configuration.
- **Clean up your own database on unsubscribe, and also by retention.** The `unsubscribe` event is not guaranteed to reach you. Data you hold should have a retention period that applies even if it never does.
- **Tell customers what you keep.** If your extension stores event data, detections or vendor data outside LimaCharlie, say where, for how long and in which region. For many customers that decides whether they can use it.

## Availability

There is no queue between LimaCharlie and your extension. What happens when it is down depends on who called:

| Caller | When the extension is down |
| --- | --- |
| A user in the web app, the CLI or the API | The call fails and the caller sees the error |
| A D&R rule | The request is attempted a few times, then dropped. The only record is an entry in the organization's errors |
| A continuation | Retried with backoff for about an hour, then dropped |
| The `subscribe` event | The subscription fails |
| The `unsubscribe` event | The unsubscribe completes anyway and your extension is not told again |
| A configuration save | The save fails, because `ValidateConfig` cannot be called |
| The schema request | Every request and event fails, and the extension's page in the web app does not load |

So:

- **Run at least two instances**, or on a platform that restarts failed instances and spreads them across failure domains.
- **Make the schema cheap and static.** It is requested about once a minute while the extension is in use, and nothing works while it fails. Build it at startup; never call an external service to produce it.
- **Shut down gracefully.** During a deploy, let in-flight calls finish. The Go web server waits 10 seconds after `SIGTERM`, which is shorter than the 2-minute call limit, so long handlers can be cut off by a deploy.
- **Design scheduled work to catch up.** A missed run from a D&R schedule is not replayed. The next run should resume from a watermark instead of only covering its own interval.
- **Answer fast.** The 2-minute limit is a ceiling, not a target. A slow extension holds up whoever called it, and `update` events for one organization are sent to its extensions one after another, so a slow one delays others.

## Retries and Idempotency

Assume any call can arrive more than once. The [Runtime Contract](runtime-contract.md#timeouts-and-retries) has the rules; in practice:

- **Use the idempotency key.** It is the same across retries of one logical call. Use it to deduplicate side effects (a ticket, a task, a charge) and pass it as the metric report's `IdempotentKey`.
- **Classify errors.** Mark permanent failures `Retriable: false`. A permanent error left retriable is attempted three times with backoff. A request from a D&R rule has its own retries on top of the platform's, so a retriable error there can be attempted more than three times.
- **A timeout is not a retry.** The platform does not re-send a call that reached your extension and timed out, because the work is probably still running. That also means nobody tells you it timed out except your own logs, and no continuation it would have returned is ever scheduled.
- **Make external effects idempotent** where you can: store the LimaCharlie identifier on the record you create in another system, and look it up before creating another.

## Billing

If your extension charges for usage, the metrics you attach to responses are the bill. See [Metrics and Billing](runtime-contract.md#metrics-and-billing).

- Pick SKUs that a customer can predict from their own usage: calls, scans, gigabytes processed. Avoid SKUs that depend on internal details of your implementation.
- Bill once per logical operation, with the request's idempotency key, and only when the work succeeded.
- Test that you bill. A missing metric is lost revenue that no error reports.

## Changing the Extension After Launch

Customers depend on the schema, the actions and the behaviour you ship. Some changes are free and some are not:

| Change | Effect on existing subscribers |
| --- | --- |
| Add an action or an optional field | Visible within about a minute. Safe |
| Rename or remove an action | Breaks every D&R rule and script that calls it. Keep the old name working until customers have moved |
| Make a parameter required | Breaks callers that do not send it. Give it a default instead |
| Remove a config field | The stored value is silently dropped from the configuration you receive |
| Add a permission | Only new subscriptions get it. Existing ones keep the old key until the organization re-keys (`limacharlie extension rekey`) |
| Change flairs | Changes the identity of your extension's key for re-keyed and new subscriptions. Records created under the old identity can become invisible to a segmented extension. Settle flairs before launch |
| Rotate the shared secret | Needs a release that accepts both secrets, and changes the secret of every [extension adapter](runtime-contract.md#pushing-telemetry-into-an-organization). See [the walkthrough](walkthrough.md#10-ship-changes) |

Write a changelog customers can follow. Managed-service providers roll changes out to many organizations at once and need to know what changed before it reaches them.

## Gotchas Checklist

Go through this before your first customer subscribes.

- [ ] `ErrorHandler` is set in Go. Without it, the first request with a bad signature panics the extension. ([Runtime Contract](runtime-contract.md#where-failures-surface))
- [ ] Python extensions define `validateConfig`. The base class has none, so every configuration save fails without it.
- [ ] Every event you need has a handler. In Go, the `EventHandlers` map is what subscribes you to events, not `RequiredEvents`. ([Runtime Contract](runtime-contract.md#events))
- [ ] Request struct field names match the schema's parameter names. A mismatch gives you a zero value, not an error. ([Getting Started](building-extensions.md#a-complete-extension))
- [ ] No top-level field uses `text` or `event_name`. The platform rejects them. ([Schema & Data Types](schema-data-types.md#unsupported-data-types))
- [ ] `display_index` starts at 1. ([Schema & Data Types](schema-data-types.md#schema-element-fields))
- [ ] Nested fields, filters and anything security-relevant are validated in your handler, not only in the schema.
- [ ] `subscribe` returns within a few seconds and defers rule installation to a continuation.
- [ ] Rules you install carry `acl_scopes: ['*']` and your private tag. ([Getting Started](building-extensions.md#rules-your-extension-installs-and-resource-acls))
- [ ] Permanent errors are marked `Retriable: false`.
- [ ] Side effects and metrics use the request's idempotency key.
- [ ] Credentialed work happens in request actions, not in event callbacks.
- [ ] Every cache key includes the organization ID.
- [ ] Your host's request timeout is at least 2 minutes, and a Python server's worker timeout is raised to match.
- [ ] D&R-triggered actions write their results somewhere visible, because the response is discarded.
- [ ] Data you keep outside LimaCharlie has a retention period.

## See Also

- [Step-by-Step Walkthrough](walkthrough.md)
- [Common Patterns](patterns.md)
- [Runtime Contract](runtime-contract.md)
