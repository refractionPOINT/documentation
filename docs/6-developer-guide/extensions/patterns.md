# Common Patterns

Most extensions are built from a handful of recurring designs. This page describes the ones LimaCharlie's own extensions use, so you can pick a known-good shape instead of discovering the edge cases yourself. Each pattern says what problem it solves, how it is put together with the public SDK, and what tends to go wrong.

Nothing here assumes a particular cloud provider. Where a pattern needs infrastructure of your own, such as a queue or a database, any equivalent works.

## Installing and Maintaining Resources in the Organization

**Problem.** The extension needs things to exist inside each subscribed organization: D&R rules that call it back, lookups, an adapter. They have to be created on subscribe, kept up to date as the extension evolves, and removed on unsubscribe.

**How it is built.**

- **`subscribe`** schedules the installation instead of doing it inline. Return a [continuation](runtime-contract.md#continuations) with a short delay (one second is enough) to an internal action that does the work. The subscription is only confirmed once your handler answers, so writing a rule that sends `extension request` to your own extension from inside the handler can be refused, because the platform does not yet see the organization as subscribed. The subscribe handler also has about a minute before the user's subscribe fails.
- **`update`**, sent once a day per organization, writes the same resources again. Make the install function idempotent and call it from both places. That repairs anything a user deleted or edited and rolls out the new rules a new release of your extension ships.
- **`unsubscribe`** deletes what the extension created. Treat "not found" as success.
- **Tag everything you create** with `lc:system` and your extension's private tag, `ext:<extension-name>` (`GetExtensionPrivateTag()` in Go, `get_extension_private_tag()` in Python). Only delete or overwrite records carrying your tag, never everything in a hive.
- **Compare before you write.** Read the existing record and skip the write if the content is unchanged. Rewriting every record every day creates churn in the organization's audit log for no benefit.
- **Add `acl_scopes: ['*']`** to rules that call `extension request`, as described in [Getting Started](building-extensions.md#rules-your-extension-installs-and-resource-acls), so organizations using Resource ACLs keep working.

```go
EventHandlers: map[common.EventName]core.EventCallback{
    common.EventTypes.Subscribe: func(ctx context.Context, p core.EventCallbackParams) common.Response {
        // Defer: the subscription is not committed until this returns.
        return common.Response{Continuations: []common.ContinuationRequest{
            {InDelaySeconds: 1, Action: "install", State: limacharlie.Dict{}},
        }}
    },
    common.EventTypes.Update: func(ctx context.Context, p core.EventCallbackParams) common.Response {
        return install(p.Org) // the same idempotent function the "install" action calls
    },
    common.EventTypes.Unsubscribe: func(ctx context.Context, p core.EventCallbackParams) common.Response {
        return uninstall(p.Org) // remove only records tagged ext:<name>
    },
},
```

**What goes wrong.**

- The `unsubscribe` event is best-effort. If your extension is down or fails, the platform still completes the unsubscribe and deletes your extension's API key, so you never get a second chance. Resources you created stay behind. Tagging them is what lets a customer find and remove them later.
- The time of day `update` arrives is not predictable and you cannot request one. Do not use it for anything time-sensitive.
- The [`segment` flair](building-extensions.md#flairs) limits you to records your extension created. That is usually what you want here. It also means a user-created record with the same name is invisible to you, and your write to that name fails.

The [D&R rules and Lookups frameworks](building-extensions.md#simplified-frameworks) implement this whole pattern for those two resource types. If your extension distributes rules or a lookup, use them rather than writing it yourself.

## Scheduled Work

**Problem.** Extensions are called; they do not run timers. Something has to wake them up to poll a vendor, refresh a feed, or clean up.

**How it is built.** Install a D&R rule on the `schedule` target (see [Schedule Events](../../8-reference/schedule-events.md)) whose response is an `extension request` to one of your actions:

```yaml
detect:
  target: schedule
  event: 1h_per_org
  op: exists
  path: /
respond:
  - action: extension request
    extension name: my-extension
    extension action: sync
    extension request: {}
acl_scopes:
  - '*'
```

Use the `_per_org` events for work about the organization and `_per_sensor` for work about each sensor. Install the rule with the [pattern above](#installing-and-maintaining-resources-in-the-organization).

**What goes wrong.**

- Requests from D&R rules are not queued. If your extension is down when the schedule fires, that run is lost, so a scheduled sync has to catch up on its next run rather than assume it saw every interval. Keep a watermark (the last record or timestamp processed) and resume from it.
- When the schedule is user-configurable, rewrite the rule when the configuration changes, and again on `update` in case a configuration save failed after your validation passed.
- The platform only generates `_per_org` schedule events for organizations that had at least one sensor online in the last 7 days (see [Schedule Events](../../8-reference/schedule-events.md)). An organization that only uses your extension and has no sensors never fires the rule. If that can happen, drive the work from the daily `update` event as well.

## Long-Running Work

**Problem.** A single call has 2 minutes. Pagination through a large vendor API, a scan, or processing a large file takes longer.

There are three shapes, in order of how much infrastructure they need.

**Continuations.** Do a bounded slice of work, return its result, and ask to be called again with a cursor in the continuation `State`. The platform calls the named action with that state as the request data. This needs no infrastructure of your own. Size each slice well under the timeout, since a slice that times out is not retried and its continuation never gets requested. Remember the [100-level depth limit](runtime-contract.md#continuations), and fail closed: if the state you receive is malformed, stop instead of starting over from the beginning, or a bug turns into a loop that redoes all the work.

**Event-driven chains.** When the slow part happens on an endpoint, do not wait for it. Send the task, return, and let a D&R rule bring the result back. See [Tasking Sensors and Getting Results Back](#tasking-sensors-and-getting-results-back). This handles work that takes hours.

**A queue and workers.** The request handler validates the input, puts a job on a queue, and returns straight away. Separate workers take jobs off the queue and do the heavy lifting. This is the shape for CPU-heavy work such as parsing or scanning large artifacts. Two things to know:

- The worker has no webhook call, so it has no LimaCharlie credentials, and it should not be handed a token to keep. Have the worker write its result to your own store, keyed on organization ID and job ID. Have the request handler return a [continuation](runtime-contract.md#continuations) to an action that checks the job. That action arrives with a fresh token: if the job is finished, it does the LimaCharlie side of the work (sending events through an [extension adapter](#pushing-telemetry-into-the-organization), writing records); if not, it returns another continuation. With the 300-second maximum delay and 100-level depth, one chain can wait a little over 8 hours.
- Bill from the response of the action that sees the finished job, so you only bill work that succeeded. Use a metric idempotency key derived from the original request's key and the job ID, so a redelivered job or a repeated check is not billed twice.

## Tasking Sensors and Getting Results Back

**Problem.** The extension needs to run a command on endpoints and act on the result, which may come back seconds or hours later.

**How it is built.**

1. Send the task with an investigation ID that marks it as yours, and carry any state you will need in the investigation context. In Go, `sensor.Task(command, limacharlie.TaskingOptions{InvestigationID: "my-extension", InvestigationContext: state})` sets the event's `routing/investigation_id` to `my-extension/<state>`.
2. Install a D&R rule that matches the reply and sends it back to you:

    ```yaml
    detect:
      event: OS_PACKAGES_REP
      op: starts with
      path: routing/investigation_id
      value: my-extension/
    respond:
      - action: extension request
        extension name: my-extension
        extension action: handle_packages
        extension request:
          sid: routing.sid
          inv_id: routing.investigation_id
          event: event
    acl_scopes:
      - '*'
    ```

3. The `handle_packages` action parses its state back out of `inv_id` and continues: stores the result, sends the next task to the same sensor, or reports a finding.

Carrying state in the investigation ID makes the whole workflow stateless on your side. A multi-step job, such as scanning with one rule at a time, can send the next task from the handler of the previous result without keeping anything in a database.

**What goes wrong.**

- Sensors are often offline. A plain task to an offline sensor is not delivered later. The [Reliable Tasking extension](../../5-integrations/extensions/limacharlie/reliable-tasking.md) queues tasks until the sensor comes back; its `context` field ends up in the reply's `investigation_id` the same way. List it in your definition's **Required Extensions**.
- Use a selector only for the first task. Follow-up tasks should name the `sid` the result came from, or you fan out to sensors that were never part of the job.
- Each reply arrives as its own request, so a task to a thousand sensors is a thousand calls to your extension. Make the handler cheap.

## Pushing Telemetry into the Organization

**Problem.** The extension produces data customers want to search, alert on with their own D&R rules, keep, and forward to their outputs: scan findings, vendor alerts, logs from a third-party product.

**How it is built.** Create an extension adapter on subscribe with `CreateExtensionAdapter` (Go) or `create_extension_adapter` (Python), send events with `SendToWebhookAdapter` / `send_to_webhook_adapter`, and delete it on unsubscribe. See [Runtime Contract](runtime-contract.md#pushing-telemetry-into-an-organization).

Pass a mapping when you create the adapter, such as `{"event_type_path": "event"}`, so one adapter carries many kinds of event and each gets its own event type. Customers can then write rules like `event: my_finding`.

**What goes wrong.**

- The adapter's secret is derived from your extension's shared secret and the organization ID. That saves you storing a per-organization secret, but it means rotating the shared secret changes every adapter's secret.
- Decide whether a failed send should fail the call. For best-effort findings in the middle of a longer chain, log the failure and carry on, so one failed send does not stop the job.

## Integrating a Third-Party Product

**Problem.** The extension calls a vendor's API on the customer's behalf, so it needs the customer's credential for that vendor.

**How it is built.**

- Declare the credential as a [`secret`](schema-data-types.md#secrets) config field. The customer stores the credential in their own [secrets manager](../../7-administration/config-hive/secrets.md) and picks it. On requests, the platform replaces the reference with the value before calling you, so the credential never has to live in your systems.
- Build a vendor client per organization and cache it, keyed on the organization ID and a hash of the credential. When the customer rotates the secret, the hash changes and you build a new client instead of reusing one with a stale token. If the vendor uses short-lived OAuth tokens, cache the token in that client too, rather than fetching a new one per call.
- On a `401` from the vendor, drop the cached client so the next call rebuilds it.
- Map vendor errors onto [retriable and permanent](runtime-contract.md#making-retries-work-for-you): a rejected credential or a `4xx` is permanent, a timeout, a `5xx` or a vendor `429` is retriable. Bound your own retries against the vendor inside a call, since the platform may retry the whole call on top of them.

**Typed actions plus a passthrough.** A vendor API often has hundreds of endpoints. A useful shape is a small set of typed actions for the common tasks (`isolate_host`, `list_alerts`) plus one generic `api_call` action taking a method, path and body. Customers get a good UI for the common cases and are not blocked on you for the rest.

**Scope limits.** Customers who manage many tenants inside the vendor product need to limit what one LimaCharlie organization can reach. Put the limit in config (for example a list of vendor site or account IDs) and intersect every request with it. A request can narrow the scope, never widen it.

**What goes wrong.**

- Secret resolution happens on requests. Event callbacks (`subscribe`, `unsubscribe`, `update`) receive the configuration as stored, with `hive://secret/...` references unresolved. If an event handler needs the vendor credential, have it schedule a continuation to a request action and do the vendor call there.
- Never log a resolved credential. `MaskSecrets` in the Go SDK helps when you log configuration.

## Ticketing and Case Synchronisation

**Problem.** Detections or cases in LimaCharlie should become tickets in another system, and possibly stay in sync with it.

**How it is built.** Expose actions such as `create_ticket`, `add_note` and `search_tickets`, and let customers drive them from their own D&R rules. Keep the opinionated "mirror everything" behaviour as an optional recipe on top of those actions, not the only way to use the extension.

**What goes wrong.**

- **Duplicates.** A detection can be delivered more than once (retries, a rule firing twice). Store the LimaCharlie identifier, such as the detection or case ID, in a correlation field on the ticket, and search for it before creating a new one.
- **Echo loops.** If you also pull changes back from the ticketing system, exclude changes made by your own integration user, or every update bounces back and forth.
- **Polling windows.** When polling for changes since a timestamp, make the window inclusive and deduplicate by record ID. An exclusive window loses records that share the boundary timestamp.
- **Query injection.** Escape any value you interpolate into the vendor's query language. Detection fields are attacker-influenced data.

## Packaging Content: Rules and Feeds

**Problem.** You maintain detection content or threat intelligence and want it in many organizations, kept current, without each customer copying it by hand.

**How it is built.** Use the [simplified frameworks](building-extensions.md#simplified-frameworks). For rules, implement `GetRules()`; for a feed, implement `GetLookup()`. The framework installs the content on subscribe, refreshes it on a recurring rule, deletes only what it installed, and gives customers a config to disable new rules by default or apply a suppression period. A complete feed extension is a few dozen lines.

Customers who manage many organizations through infrastructure as code get your updates without a change on their side, which is the main reason to ship content as an extension rather than as files.

## Acting as the User

**Problem.** Some actions should only do what the person asking is allowed to do, for example exporting configuration or reading data the caller may not otherwise see.

**How it is built.** Set `is_impersonated: true` on the action. The request then carries the caller's own token, and every API call the extension makes with it is checked against the caller's permissions. See [Impersonation](runtime-contract.md#impersonation).

A request from a D&R rule has no user behind it, so it cannot call an impersonated action. If an impersonated action should also be usable from automation, set `allow_automation: true` (`AllowAutomation` in Go). When a rule drives it, the action then runs with the extension's own credential, and the request carries the rule's name. Decide explicitly what the action may do in that case.

## Isolating Organizations from Each Other

**Problem.** The extension runs code or tools that should not share a process, a filesystem or memory between customers, such as untrusted scripts or third-party binaries.

**How it is built.** Put a small router in front of a pool of per-organization workers. The router is the extension: it verifies the webhook signature, looks up or provisions the worker for the request's organization, and forwards the call. Keep the shared secret and any privileged credential in the router, and give workers only what one call needs.

The [multiplexer](https://github.com/refractionPOINT/lc-extension/tree/master/multiplexer) in the SDK repository is an implementation of this pattern for one container platform, and a useful reference if you build it on another.

## See Also

- [Design Considerations & Gotchas](design-considerations.md)
- [Runtime Contract](runtime-contract.md)
- [Testing Extensions](testing.md)
