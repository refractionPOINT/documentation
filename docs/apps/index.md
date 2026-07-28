# Apps

Apps are small, custom tools that run **inside the LimaCharlie console**. An app
can be a dashboard, a table, a chart, a one-click action, or a panel that appears
next to a sensor or a case. You build each app for the way that your team works.

You do not need to be a developer to build an app. Describe what you want in plain
language to the LimaCharlie AI assistant. For example: *"show me a table of my
Windows sensors that did not check in for 24 hours"*. The assistant builds the app,
connects it to the correct LimaCharlie data, and saves it to your organization. You
then open the app and it runs.

!!! tip "The one-sentence version"
    An app turns a plain-language request into a small, safe, self-contained tool.
    The tool runs inside your LimaCharlie console and acts on your behalf, only
    within the permissions that you approve.

!!! note "Apps is a Labs feature"
    Apps is a **Labs** feature. In the console it appears as **Apps** in the
    organization sidebar, with a *Labs* badge. If you do not see it, it is possible
    that it is not enabled for your organization. Contact LimaCharlie support.

## What you can build

An app is a web page that can read your LimaCharlie data, so many types of app are
possible. Common examples:

- **Dashboards** — a live count of online sensors, of detections in the last 24
  hours, or of open cases, shown as large KPI numbers.
- **Tables** — a filtered list of sensors, detections, or cases, in the format that
  your analysts read.
- **Charts and graphs** — bar, line, or doughnut charts of activity over time. They
  use the same charting engine as the LimaCharlie console.
- **One-click tools** — a button that runs a saved query, isolates a host, or tags
  a sensor. The button needs the correct permissions and one more confirmation.
- **Context panels** — a small view that appears *on the page of a sensor* (or of a
  case, a detection, or a D&R rule). The panel shows the enrichment that your
  workflow needs.

For copy-and-paste examples of each type, including charts and tables, see
[Building Blocks & Recipes](building-blocks-and-recipes.md).

## Where apps appear

An app can appear in two kinds of place:

- **The Apps launcher** — an **Apps** page in your organization sidebar
  (`/orgs/<your-org>/apps`) that lists every app and lets you open, manage, and
  create apps.
- **Embedded in an object's page** — you can attach an app to the pages of specific
  objects, so that it appears in context. For example, an app that is declared for
  sensors appears as a panel on the page of a sensor. The console tells the app
  *which* sensor you look at. More surfaces (cases, detections, and D&R rules) use
  the same mechanism and are becoming available.

You choose where an app appears when you build it. For more information, see
[Creating & Managing Apps](creating-and-managing-apps.md).

## How apps stay safe

The platform enforces limits on every app. An app is code, and it can read
LimaCharlie data on your behalf. Three controls keep this safe.

- **It runs in a restricted sandbox.** Every app runs inside an isolated frame. The
  frame has no access to your browser cookies, your other tabs, local storage, or
  the LimaCharlie page around it. The app cannot move you to a different page and
  cannot open pop-ups.
- **It never holds your credentials.** When an app needs LimaCharlie data, the
  console brokers the request. The console attaches a **temporary key that is
  scoped to only the permissions that you approved**. There is no token inside the
  app to steal or misuse. By default, an app can reach *no* outside website. It can
  contact only the external sites that were declared and shown to you.
- **You approve what it can do — and it can never exceed you.** Before an app runs
  the first time, you see a consent screen that lists what the app will be able to
  do. The app gets the **intersection** of the permissions that the app asks for
  and the permissions that *you* hold. An app can therefore never act with more
  authority than you have. The person who built the app could request only the
  permissions that this person already held. A low-privilege author cannot put
  high-privilege actions into an app for an admin to start.

!!! info "The boundary is the platform, not the app's good behavior"
    LimaCharlie and your browser enforce the sandbox, the scoped key for each
    viewer, and the network allowlist. The app's own code does not enforce them.
    These limits also hold an app that has bugs or that is malicious. The [consent screen](creating-and-managing-apps.md#understanding-the-consent-screen)
    explains how to read what an app asks for.

## Who can use apps

A small set of organization permissions controls access:

| To… | You need |
| --- | --- |
| See and open apps | `app.get` |
| Create or edit apps | `app.set` |
| Delete apps | `app.del` |
| Turn an app on or off | `app.set.mtd` |

These permissions control who can *manage app records*. They are different from the
permissions that an app requests for its own work. For the full model, see
[Permissions](../8-reference/permissions.md).

## Your first app in two minutes

1. Open **Apps** in your organization sidebar. Click **Create new App**.
2. In the AI session that opens, describe what you want. For example:
   *"Show me a table of all my sensors with their hostname, platform, and whether
   they are online right now."*
3. Let the assistant design and build the app. The assistant saves the app and
   shows an **Open your live app** card.
4. Click the card. The first time, read the consent screen and choose **Open app**.
5. Your app now runs. Find it at any time under **Apps**.

Full instructions: [Creating & Managing Apps](creating-and-managing-apps.md).

## Where to go next

- [Creating & Managing Apps](creating-and-managing-apps.md) — build apps with the
  AI assistant, manage them, and read the consent screen.
- [Building Blocks & Recipes](building-blocks-and-recipes.md) — patterns for
  tables, KPIs, charts, forms, and embedded panels.
- [Reference](reference.md) — the app runtime (`window.lc`), the design system,
  charting, permissions, and limits.
- [Config Hive: Apps](../7-administration/config-hive/apps.md) — the underlying
  `app` record format and how to manage apps with the API, SDKs, or CLI.
- [AI Sessions](../9-ai-sessions/index.md) — the AI assistant that writes your
  apps.
