# Rich Cards & Slash Commands

In interactive sessions, the agent can render **rich cards** — interactive UI
elements that appear inline in the chat instead of plain text. A card might be a
clickable list of your organizations, a detail view of a D&R rule, a form that
collects a secret, or a billing summary. Many of the same cards can also be summoned
directly with **slash commands**, without waiting on the agent.

!!! note "Where this applies"
    Rich cards are a feature of the interactive chat experience (the web UI and the
    "Chat with FDE" surface). Fire-and-forget [D&R-driven sessions](dr-sessions.md)
    don't render cards.

## How cards work

When the agent wants to show structured information, it emits a small descriptor
describing which card to render and the data to populate it with. The web app
validates that data against the card's schema and renders the matching component.
Cards that collect sensitive input (for example, a secret value) are schema-locked
so the agent cannot pre-fill the fields it shouldn't see.

There are roughly forty card types. They fall into a few groups:

- **Resource cards** — detail and list views of LimaCharlie resources: organizations,
  secrets, D&R rules, false-positive rules, YARA rules, lookups, sensors,
  installation keys, cases, detections, users, roles, outputs, adapters, artifacts,
  AI agents / skills / memories, playbooks, and SOPs.
- **Interactive cards** — actions that go beyond display: a billing and usage view,
  a secret-intake form, and a feedback form.
- **Share card** — share what you built (an editable message that opens X, LinkedIn,
  Reddit, the device share sheet, or copies a link — nothing posts automatically)
  and, for org admins, invite teammates by email and role in one step.
- **Onboarding cards** — a welcome/trust block shown to brand-new users.

## Slash commands

Typing `/` in the chat input opens a menu of commands. These render a card
**client-side**, without an agent round-trip — handy when you already know exactly
what you want. Common examples:

| Command | Renders |
|---------|---------|
| `/orgs [search]` | Your organizations, clickable to set the working org |
| `/help` | The list of available slash commands |
| `/billing` | Billing and usage for the active org |
| `/share` | The share / invite card |
| `/secrets [filter]` | Your secrets |
| `/dnr [filter]` | D&R rules |
| `/fp [filter]` | False-positive rules |
| `/yara [filter]` | YARA rules |
| `/lookups [filter]` | Lookup tables |

The agent can also emit any of these cards itself in the course of a conversation —
for example, returning a clickable list of matching rules instead of a wall of text.
