# Apps

Apps are small, custom tools that live **inside the LimaCharlie console**. An app
can be a dashboard, a table, a chart, a one-click action, or a focused panel that
shows up right next to a sensor or a case — purpose-built for the way *your* team
works.

You don't have to be a developer to build one. You describe what you want in plain
language to the LimaCharlie AI assistant ("show me a table of my Windows sensors
that haven't checked in for 24 hours"), and it builds the app, wires it to the
right LimaCharlie data, and saves it to your organization. You open it and it just
runs.

!!! tip "The one-sentence version"
    An app turns a plain-language request into a small, safe, self-contained
    tool that runs inside your LimaCharlie console and acts on your behalf — only
    within the permissions you explicitly approve.

!!! note "Apps is a Labs feature"
    Apps is currently a **Labs** feature. In the console it appears as **Apps** in
    the organization sidebar, marked with a *Labs* badge. If you don't see it yet,
    it may not be enabled for your organization — contact LimaCharlie support.

## What you can build

Because an app is just a web page that can read your LimaCharlie data, the range
is wide. Common examples:

- **Dashboards** — a live count of online sensors, detections in the last 24
  hours, or open cases, shown as big KPI numbers.
- **Tables** — a filtered list of sensors, detections, or cases, formatted the way
  your analysts actually read them.
- **Charts and graphs** — bar, line, or doughnut charts of activity over time,
  built on the same charting engine the LimaCharlie console itself uses.
- **One-click tools** — a button that runs a saved query, isolates a host, or
  tags a sensor (with the appropriate permissions and an extra confirmation).
- **Context panels** — a mini view that appears *on a sensor's page* (or a case,
  detection, or D&R rule) and shows exactly the enrichment your workflow needs.

See [Building Blocks & Recipes](building-blocks-and-recipes.md) for copy-and-paste
examples of each — including charts and tables.

## Where apps appear

An app can surface in two kinds of places:

- **The Apps launcher** — a dedicated **Apps** page in your organization sidebar
  (`/orgs/<your-org>/apps`) that lists every app and lets you open, manage, and
  create them.
- **Embedded in an object's page** — an app can be attached to the pages of
  specific objects, so it appears in context. For example, an app declared for
  sensors shows up as a panel on a sensor's page, and the console automatically
  tells it *which* sensor you're looking at. Additional surfaces (cases,
  detections, and D&R rules) use the same mechanism and are rolling out.

You choose where an app appears when you build it — see
[Creating & Managing Apps](creating-and-managing-apps.md).

## How apps stay safe

Apps run with strong, platform-enforced guardrails. This matters: an app is code,
and it can read LimaCharlie data on your behalf. Three things keep that safe.

- **It runs in a locked-down sandbox.** Every app runs inside an isolated frame
  with no access to your browser cookies, your other tabs, local storage, or the
  LimaCharlie page around it. It can't navigate you away or open pop-ups.
- **It never holds your credentials.** When an app needs LimaCharlie data, the
  request is brokered by the console itself. The console attaches a **temporary
  key scoped to only the permissions you approved** — there is no token inside the
  app to steal or misuse. By default, an app can reach *no* outside websites at
  all; it can only contact external sites that were explicitly declared and shown
  to you.
- **You approve what it can do — and it can never exceed you.** Before an app runs
  for the first time, you see a consent screen listing exactly what it will be
  able to do. The permissions it actually gets are the **intersection** of what
  the app asks for and what *you* already hold, so an app can never act with more
  authority than you have. And whoever built the app could only request
  permissions *they* already held — closing the door on a low-privilege author
  smuggling powerful actions into an app for an admin to trigger.

!!! info "The boundary is the platform, not the app's good behavior"
    The sandbox, the per-viewer scoped key, and the network allowlist are enforced
    by LimaCharlie and your browser — not by the app's own code. Even a buggy or
    malicious app is bounded by them. The [consent screen](creating-and-managing-apps.md#understanding-the-consent-screen)
    explains how to read what an app is asking for.

## Who can use apps

Access to apps is governed by a small, dedicated set of organization
permissions — the `app.*` set. They follow LimaCharlie's standard config-hive
pattern: a plain permission grants access to the **whole record** (including the
app's HTML and its name, description, and icon), while its `.mtd` ("metadata")
counterpart grants access only to the record's metadata envelope — its
enabled/disabled status, tags, and timestamps — never the app's contents.

| Permission | Grants | What it's for |
| --- | --- | --- |
| `app.get` | Read the full app record — its HTML, name, description, and icon | **View and run** an app, view its source, and see it in the launcher |
| `app.get.mtd` | Read only the record's metadata envelope — enabled/disabled status, tags, timestamps, last editor — **not** the app's HTML, name, or description | Check whether apps exist and are turned on, without being able to open, run, or read them |
| `app.set` | Create and modify app records, including their HTML and configuration | Build a new app or edit an existing one |
| `app.set.mtd` | Modify only the record's metadata, most notably its enabled/disabled status | Turn an app on or off without the ability to change what it does |
| `app.del` | Delete app records | Remove an app from the organization |

!!! note "These gate managing apps, not what an app can do"
    The `app.*` permissions decide who can **manage app records**. They are
    entirely separate from the permissions an individual app requests in its
    `required_permissions` to do its job — those are minted into the app's
    scoped, per-viewer key. Don't conflate the two. See
    [Permissions](../8-reference/permissions.md) for the full catalog and
    [Reference: Permissions and consent](reference.md#permissions-and-consent)
    for how an app's own permissions work.

## Your first app in two minutes

1. Open **Apps** in your organization sidebar and click **Create new App**.
2. In the AI session that opens, describe what you want — for example:
   *"Show me a table of all my sensors with their hostname, platform, and whether
   they're online right now."*
3. Let the assistant design and build it. When it's done it saves the app and
   shows you an **Open your live app** card.
4. Click it. The first time, review the consent screen and choose **Open app**.
5. Your app is running. Find it any time under **Apps**.

Full walkthrough: [Creating & Managing Apps](creating-and-managing-apps.md).

## Where to go next

- [Creating & Managing Apps](creating-and-managing-apps.md) — build apps with the
  AI assistant, manage them, and understand the consent screen.
- [Building Blocks & Recipes](building-blocks-and-recipes.md) — ready-made patterns
  for tables, KPIs, charts, forms, and embedded panels.
- [Reference](reference.md) — the app runtime (`window.lc`), the design system,
  charting, permissions, and limits.
- [Config Hive: Apps](../7-administration/config-hive/apps.md) — the underlying
  `app` record format and how to manage apps with the API, SDKs, or CLI.
- [AI Sessions](../9-ai-sessions/index.md) — the AI assistant that authors your
  apps.
