# Reference

The technical reference for app authors: the record fields, the `window.lc`
runtime that your code calls, the design system, charting, permissions, and limits.

For the canonical record format and for management of apps with the API, SDKs, or
CLI, see [Config Hive: Apps](../7-administration/config-hive/apps.md). For
task-focused examples, see
[Building Blocks & Recipes](building-blocks-and-recipes.md).

## What an app is

An app is a **single, self-contained `<body>` fragment** — your HTML, inline CSS,
and inline JavaScript — stored in the `app` config hive. The console renders the
fragment inside a sandboxed `<iframe>`. Before your content, the console injects
three items: a strict Content-Security-Policy, the design-system stylesheet, and
the `window.lc` runtime. You write only the body. The host owns the document shell.

## Record fields

These are the fields that you set when you write an app (the `data` payload of an
`app` hive record). This is a summary. For the authoritative definition and
validation, see [Config Hive: Apps](../7-administration/config-hive/apps.md).

| Field | Required | Purpose |
| --- | --- | --- |
| `display_name` | Yes | The name shown in the launcher and in embeds (≤ 256 chars). |
| `html` | Yes | The self-contained `<body>` fragment to render. |
| `description` | No | Short description (≤ 4096 chars). |
| `icon` | No | Emoji, icon id, or small data-URI (≤ 256 chars). |
| `required_permissions` | No | LimaCharlie permissions that the app needs (≤ 64). See [Permissions](#permissions-and-consent). |
| `allowed_origins` | No | External `https` sites that the app can contact (≤ 32). See [External origins](#external-origins). |
| `required_services` | No | First-party services that the app calls: `search`, `replay`, `cases`, `ai` (≤ 16). |
| `locations` | No | Where the app appears (≤ 8). See [Locations and context](#locations-and-context). |
| `expected_context` | No | Context keys that the app expects when it is embedded (≤ 32). |
| `schema_version` | No | App format version. If you omit it, the value is `1`. |

## The `window.lc` runtime

The console injects a trusted runtime as `window.lc`. It is the only connection
between your app and LimaCharlie.

```js
await lc.ready            // resolves after the secure handshake — await before any call
lc.version               // '1'
lc.ctx.user              // { id, email, displayName } | null
lc.ctx.orgs              // [{ oid, name }] — the current organization is lc.ctx.orgs[0]
lc.ctx.context           // embed identifiers, e.g. { sid } on a sensor page
lc.ctx.theme             // { mode: 'dark' | 'light', vars: { '--lc-…': '…' } }
lc.api(method, path, body?, opts?)   // brokered LimaCharlie API call → Promise<JSON>
lc.chart(target, spec)               // themed chart → Chart instance
lc.onThemeChange(cb)                 // live theme updates; returns an unsubscribe fn
```

!!! warning "Always `await lc.ready` first"
    `lc.ctx` is empty and calls fail until the handshake completes. Start every app
    with `await lc.ready`.

### The `lc.api` call

`lc.api(method, path, body?, opts?)` makes a LimaCharlie API call. The console
attaches a temporary key that is scoped to permissions. **Never put an API key in
an app.**

- **Paths are site-relative**, under `/v1`: `lc.api('GET', '/v1/who')`,
  `lc.api('GET', '/v1/sensors/' + oid)`. Absolute URLs, other hosts, and writes to
  the `app` hive itself are rejected.
- **Targeting a service.** Pass `opts.service` to route the call to a first-party
  service instead of the main API. The `required_services` field of the app must
  list the service. The console host-pins the call and sends the same scoped key,
  but it does **not** rewrite your path. Use the path that the service expects.

| Service | What it's for | Path shape |
| --- | --- | --- |
| `search` | Historical event search (LCQL) — the Query Console engine | `POST /v1/search/` → `GET /v1/search/<queryId>/` |
| `cases` | Case management | `GET /api/v1/cases` |
| `ai` | AI sessions / agents | `/v1/...` |
| `replay` | Sensor telemetry replay (different from `search`) | service-specific |

- **Errors** reject with an `Error` that carries `code` and `status`. The `code` is
  one of: `denied`, `rate_limited`, `unauthorized`, `http`, `timeout`, `aborted`,
  `malformed`. Catch the error and show `e.code`.
- **Limits:** about **10 requests/second** (burst 20), **8 concurrent**, request
  body up to **256 KB**, and a **70-second** timeout for each call.

```js
try {
  const res = await lc.api('GET', '/v1/sensors/' + lc.ctx.orgs[0].oid)
} catch (e) {
  console.log(e.code, e.status)   // e.g. 'denied', 403
}
```

### The `lc.chart` helper

`lc.chart(target, spec)` draws a themed chart with **Chart.js v4**. The runtime
supplies Chart.js, but only when your app references `lc.chart`. Do not add your
own chart library, because external scripts are blocked.

- **`target`** is a `<canvas>` element or its id, or any container element or id.
  If the target is not a canvas, the helper creates one inside it. Give the
  container an explicit **height**, or the chart is invisible.
- **`spec`** is `{ type, data, options }`, exactly as in Chart.js. `type` can be
  `bar`, `line`, `doughnut`, `pie`, and so on.
- **Theming is automatic.** Datasets that you leave uncolored get the console
  palette (`--lc-accent`, `--lc-positive`, `--lc-warning`, `--lc-danger`,
  `--lc-muted`). Axis, grid, and text colors track the live theme and render again
  when you toggle dark mode.
- **Returns** the Chart instance. Call `.update()` or `.destroy()`. If you call
  `lc.chart` again on the same target, it replaces the previous chart cleanly.

### Reacting to theme changes

Theme tokens update live. If you draw custom content, and you do not use the
design-system classes or `lc.chart`, subscribe to the theme to color the content
again:

```js
const stop = lc.onThemeChange((theme) => {
  // theme.mode is 'dark' | 'light'; theme.vars holds the --lc-* values
})
// later: stop()
```

## Design system

The runtime injects CSS variables (`--lc-*`) that come from the live console theme.
It also injects a component stylesheet (`.lc-*`) that uses only those variables.
**Combine the classes and reference the variables. Never hardcode colors or
fonts.** These rules keep apps in the brand style and aware of dark mode.

### Tokens

| Token | Use |
| --- | --- |
| `--lc-bg` | Page background |
| `--lc-surface` | Card / panel background |
| `--lc-line` | Borders and dividers |
| `--lc-ink` | Primary text |
| `--lc-muted` | Secondary text |
| `--lc-accent` | Links and primary accent |
| `--lc-positive` | Success (green) |
| `--lc-warning` | Warning (amber) |
| `--lc-danger` | Error (red) |
| `--lc-input-bg` / `--lc-input-line` | Form field background / border |
| `--lc-font-sans` / `--lc-font-mono` | UI font / monospace font |
| `--lc-radius` | Corner radius |
| `--lc-space` | Base spacing unit (8px) |

### Components

| Class | Element |
| --- | --- |
| `.lc-card` | Bordered container / panel |
| `.lc-btn`, `.lc-btn--primary`, `.lc-btn--danger` | Buttons |
| `.lc-input`, `.lc-select`, `.lc-textarea` | Form fields |
| `.lc-label` | Field label |
| `.lc-badge`, `.lc-badge--positive`, `.lc-badge--warning`, `.lc-badge--danger` | Status pills |
| `.lc-table` | Table |
| `.lc-kpi`, `.lc-kpi__value`, `.lc-kpi__label` | KPI metric (big number + label) |
| `.lc-row`, `.lc-col`, `.lc-stack` | Flex layout: horizontal row, vertical column, spaced stack |
| `.lc-muted` | Muted text |
| `.lc-mono` | Monospace text |
| `.lc-spinner` | Loading spinner |

The design system also styles links, headings, and `code` / `pre`.

## Permissions and consent

An app declares the permissions that it needs in `required_permissions`. Two rules
limit this:

- **At authoring time**, you can declare only the permissions that you hold. Each
  permission must be a real, non-root, issuable permission.
- **At view time**, the app runs with the **intersection** of its declared
  permissions and the permissions of the *viewer*. Each permission that the viewer
  does not hold is dropped. The app runs without that permission and can never get
  it.

The [consent screen](creating-and-managing-apps.md#understanding-the-consent-screen)
puts permissions in classes, so that viewers understand the risk:

| Class | Meaning | Examples |
| --- | --- | --- |
| **Dangerous** | Actions that change privileges or billing | `apikey.ctrl`, `user.ctrl`, `billing.ctrl` |
| **Sensitive read** | Reads secrets, raw telemetry, or audit logs | `secret.get`, `insight.evt.get`, `audit.get` |
| **Write** | Changes state or takes action | `sensor.task`, `dr.set`, `secret.del` |
| **Read** | Read-only | `sensor.list`, `sensor.get` |

Dangerous permissions and sensitive-read permissions cause stronger warnings, and
they need consent again in each browser session. Request the **fewest** permissions
that an app needs, and prefer read-only permissions (`*.get`, `*.list`). For the
full catalog, see [Permissions](../8-reference/permissions.md).

## External origins

By default, an app can reach **no** external website. It can reach only
LimaCharlie, through `lc.api`. To let the app's own `fetch` call an outside
service, list the service in `allowed_origins`. Each entry:

- must use **`https`**;
- is **scheme + host** only, with an optional port — **no** path, query, fragment,
  credentials, or wildcards (e.g. `https://intel.example.com` or
  `https://intel.example.com:8443`);
- appears on the consent screen for every viewer, with a warning that data can
  leave LimaCharlie.

Calls to declared origins use your app's own `fetch` and carry **no** LimaCharlie
key. Up to 32 origins.

## Locations and context

`locations` controls where an app can appear. `expected_context` declares the
identifiers that the app needs when it is embedded, and the console passes them
into `lc.ctx.context`.

| Location | Where it appears | Typical context |
| --- | --- | --- |
| `standalone` | The **Apps** launcher (default) | — |
| `within_a_sensor` | A sensor's page | `sid` |
| `within_a_detection` | A detection's page | `detection_id` |
| `within_a_case` | A case's page | case identifier |
| `within_a_dr_rule` | A D&R rule's page | rule identifier |

An app can declare several locations. Embedded surfaces other than sensors are
becoming available. See
[Choosing where an app appears](creating-and-managing-apps.md#choosing-where-an-app-appears).

## Hard rules and limits

Apps are validated when you write them *and* when they are mounted. Some problems
**block** the app. Other problems give a **warning**, because the
Content-Security-Policy of the sandbox already stops them at runtime. The app then
breaks with no message.

**Blocked** (the app does not save or run):

- Empty HTML, HTML over **3 MB**, or more than **20,000** elements.
- A `<base>` element, or a `<meta http-equiv>` that the app supplies. The host owns
  the document shell and the CSP.

**Warned** (allowed, but the CSP blocks them at runtime, so they do not work):

- External `<script src>`, external stylesheets, `@import` — inline everything.
- Nested `<iframe>`, `<embed>`, `<object>`, or `<form>` that posts to an external
  action.
- Direct network calls (`fetch`, `XMLHttpRequest`, `WebSocket`) to anything that is
  not in `allowed_origins` — use `lc.api` for LimaCharlie data.

**Record limits:** unknown fields are rejected; total record size up to **10 MB**;
field caps as listed under [Record fields](#record-fields).

### The author's checklist

1. Output a single self-contained `<body>` fragment — no `<html>`, `<head>`,
   `<base>`, or `<meta http-equiv>`.
2. Inline all JavaScript and CSS. Do not use external resources.
3. Read LimaCharlie data through `lc.api`. Never embed a key and never ask for
   credentials.
4. Contact only the external sites that you declared in `allowed_origins`.
5. Style with `.lc-*` classes and `--lc-*` tokens. Never hardcode colors or fonts.
6. Request the least permission necessary. Prefer read-only permissions.

## Where to go next

- [Building Blocks & Recipes](building-blocks-and-recipes.md) — worked examples.
- [Creating & Managing Apps](creating-and-managing-apps.md) — build, manage, place,
  and consent.
- [Config Hive: Apps](../7-administration/config-hive/apps.md) — record format and
  management with code.
