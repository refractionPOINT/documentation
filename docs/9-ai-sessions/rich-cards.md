# Rich Cards & Slash Commands

In interactive sessions, the agent can show **rich cards**. These are interactive UI
elements that appear in the chat instead of plain text. A card can be a
clickable list of your organizations, a detail view of a D&R rule, a form that
collects a secret, or a billing summary. You can also open many of the same cards
directly with **slash commands**, and you do not wait for the agent.

!!! note "Where this applies"
    Rich cards are part of the interactive chat experience (the web app and the
    "Chat with FDE" surface). [D&R-driven sessions](dr-sessions.md)
    do not show cards.

## How cards work

To show structured information, the agent emits a small descriptor. The descriptor
names the card to show and gives the data for it. The web app checks that data
against the schema of the card, then shows the matching component.
Cards that collect sensitive input, for example a secret value, are schema-locked.
The agent cannot pre-fill the fields that it must not see.

About forty card types exist. They are in these groups:

- **Resource cards** — detail and list views of LimaCharlie resources: organizations,
  secrets, D&R rules, false-positive rules, YARA rules, lookups, sensors,
  installation keys, cases, detections, users, roles, outputs, adapters, artifacts,
  AI agents / skills / memories, playbooks, and SOPs.
- **Interactive cards** — cards that do more than show data: a billing and usage view,
  a secret-intake form, and a feedback form.
- **Share card** — share what you built. The card gives an editable message that opens X,
  LinkedIn, Reddit, or the device share sheet, or copies a link. The card posts nothing
  automatically. An org admin can also invite teammates by email and role in one step.
- **Onboarding cards** — a welcome/trust block for new users.

## Slash commands

Type `/` in the chat input to open a menu of commands. These commands show a card
**client-side**, with no round-trip to the agent. Use them when you know which
card you want. Common examples:

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

The agent can also emit any of these cards during a conversation. For example, it can
return a clickable list of matching rules instead of a long block of text.
