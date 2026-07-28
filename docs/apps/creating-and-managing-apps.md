# Creating & Managing Apps

This page explains how to build an app with the AI assistant and how to manage apps
from the **Apps** page. It also explains the consent screen that appears before an
app runs.

You manage everything from **Apps** in your organization sidebar
(`/orgs/<your-org>/apps`). The page header reads:

> Custom mini apps for this organization. Apps run in a sandboxed frame and act on
> your behalf only within the permissions you approve.

## Building an app with the AI assistant

The fastest way to build an app is to describe it to the LimaCharlie AI assistant.
This method needs no code.

1. On the **Apps** page, click **Create new App**. A new AI session opens that is
   ready to build an app for your organization.
2. **Describe the outcome that you want**, in plain language. Be specific about the
   result, not about the method. Good prompts:
    - *"A dashboard with three big numbers: total sensors, sensors online now, and
      sensors that did not check in for 24 hours."*
    - *"A table of my detections from the last 7 days, with the detection name, the
      sensor hostname, and the time, newest first."*
    - *"A bar chart of how many of my sensors are on Windows, macOS, and Linux."*
3. **Let the assistant build the app.** The assistant reads the official guide for
   app authors. It confirms every LimaCharlie data call against the live API of
   your organization, so that it does not invent endpoints. It then writes the app
   and saves it to your organization.
4. When the assistant is done, it shows an **Open your live app** card in the chat.
   Click the card to go to your running app.

!!! tip "Talk in outcomes, refine in conversation"
    You do not need to know any LimaCharlie API or to write any HTML. If the first
    result is not correct, say so: *"group the table by platform"*, *"make the
    offline count red"*, *"add a refresh button"*. The assistant then revises the
    app in place.

!!! note "New apps may start turned off"
    An app must be **enabled** to be active and to appear in any embedded location.
    If your new app shows a *disabled* status, switch it on with the **Status**
    toggle on the **Apps** page. See [Turning apps on and off](#turning-apps-on-and-off).

### Editing an existing app

1. On the **Apps** page, open the **⋯** menu on the row of the app and choose
   **Edit with AI**. The same command is available as **Edit App** on the page of
   the app.
2. Describe the change that you want in the AI session that opens with your
   existing app loaded. The assistant updates the app and saves it again.

## Building an app with the API, SDKs, or CLI

Apps are stored as records in the `app` config hive, so you can also create and
manage them with code. This is useful for version control, Infrastructure-as-Code,
or deployment in many organizations at the same time.

[Config Hive: Apps](../7-administration/config-hive/apps.md) gives the record
format, the security rules that are enforced when you save, and full REST, Python,
Go, and CLI examples. The short version of the CLI procedure:

```bash
# Create (and enable) an app from a JSON file describing the record:
limacharlie hive set --hive-name app --key my-app --input-file app.json --enabled

# Later, turn it off or back on:
limacharlie hive disable --hive-name app --key my-app
limacharlie hive enable  --hive-name app --key my-app
```

!!! warning "Apps are created disabled unless you say otherwise"
    A new hive record is **disabled by default**. The `--enabled` flag above
    creates and enables the app in one step. Without the flag, the app stays off
    until you run `limacharlie hive enable`.

For the contents of the `html` field, see the [Reference](reference.md). It
explains the runtime that your code calls, the design system, and charting.

## Managing apps from the Apps page

The **Apps** page lists every app in the organization. Each row shows four columns:

| Column | What it shows |
| --- | --- |
| **App** | The icon, name, and description of the app. |
| **Permissions** | A short summary of what the app can do — for example *"2 read"* or *"1 sensitive · 1 write"*. Red badges mark sensitive access. |
| **Last modified** | When the app changed last, and who changed it. |
| **Status** | A toggle to enable or disable the app. |

The **⋯** menu on each row gives these commands:

- **Open** — run the app in its own full-page view.
- **Edit with AI** — open an AI session to change the app (needs `app.set`).
- **Delete** — remove the app (needs `app.del`). The console asks you to confirm:
  *Delete "&lt;name&gt;"? This cannot be undone.*

### Turning apps on and off

The **Status** toggle enables or disables an app (you need `app.set.mtd`).

- A **disabled** app is inactive and does **not** appear in its embedded locations
  (for example, it does not appear on sensor pages).
- An **enabled** app is live. To enable an app does not bypass consent. Each viewer
  still approves the app the first time that the viewer opens it.

## Choosing where an app appears

When you build an app, you decide where it appears. In the AI session, tell the
assistant where you want the app — *"put this on each sensor's page"* — and the
assistant configures the rest. Two settings control this:

- **Locations** — where the app is allowed to appear:
  - **Standalone** — in the **Apps** launcher (the default).
  - **Within a sensor / case / detection / D&R rule** — embedded as a panel on the
    page of that object.
- **Expected context** — the identifiers that the app needs when it is embedded.
  The console passes these identifiers in automatically. For example, an app that
  is placed on sensor pages receives the ID of that sensor (`sid`). The app can
  then show data for *the sensor that you look at*, and you type nothing.

An app can appear in several places at the same time, for example both in the
launcher and on every sensor page. For a worked embedded example, see [Building Blocks & Recipes](building-blocks-and-recipes.md#recipe-an-embedded-sensor-panel).
For the exact values, see the [Reference](reference.md#locations-and-context).

## Understanding the consent screen

The first time that you open an app, you see a **consent screen** before the app
runs. You see the screen again each time that the app changes materially. The
screen lets you confirm what the app will be able to do *on your behalf*. Read it
like a permission prompt for a phone app. It has four parts:

1. **What it is and who touched it last.** The name of the app, its description,
   and the user who edited it last, with the date. If the author is not the author
   that you expect, stop and check.
2. **Permissions this app will use.** The access that the app runs with, in groups
   by how much each group matters:
    - **Sensitive permissions** (red) — actions that change privileges or billing.
      Be most careful with these actions.
    - **Sensitive data access** (red) — the app can read secrets, raw telemetry,
      or audit logs. If the app can *also* reach an external site, that data can
      leave LimaCharlie.
    - **Can make changes** (amber) — the app can change your environment (for
      example, tag or isolate a sensor, or change a rule).
    - **Read-only access** — the app can read the listed data but cannot change it.
    - **Not granted** — permissions that the app asked for but that *you do not
      hold*. The app runs **without** these permissions and can never get them by
      asking.
3. **External data access.** The screen shows either *"This app cannot contact any
   external sites."*, or a warning. The warning lists every outside website that
   the app can contact. Anything that the app can read can go to those sites, so
   continue only if you trust the author.
4. **LimaCharlie services.** More first-party services that the app can call in
   addition to the main API — Search (historical events), Replay (telemetry),
   Cases, or AI. These services use the same approved permissions.

The button reads **Open app** for an ordinary app, or **I understand, open app**
when the app requests sensitive access. Choose **Cancel** to exit without running
the app.

!!! info "When you'll be asked again"
    For most apps, your browser remembers your approval, so the consent screen does
    not appear again. It appears again **if the app changes** — its content,
    permissions, external sites, or services — so that you can review what is new.
    Apps that can read **sensitive data** or that do **privileged or billing**
    actions are deliberately *not* remembered across sessions. You approve these
    apps again in each browser session.

## Where to go next

- [Building Blocks & Recipes](building-blocks-and-recipes.md) — patterns for
  tables, KPIs, charts, forms, and embedded panels.
- [Reference](reference.md) — the runtime, design system, charting, permissions,
  and limits.
- [Config Hive: Apps](../7-administration/config-hive/apps.md) — the record format
  and management with code.
