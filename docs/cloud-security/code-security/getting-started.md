# Get started with Code Security

Scanning needs two things:

1. **A source-control connection** that can read repository contents.
2. **A code-scanning policy** that turns scanning on and says which
   repositories to scan.

Code Security is opt-in. Connecting GitHub, GitLab or Bitbucket alone scans
nothing until a policy selects repositories.

## Before you start

- The organization is subscribed to Cloud Security (`ext-cloud-security`). Without
  the subscription the Cloud Security pages show an enable screen, and the API
  answers `403`.
- You have `cloudsec.get` and `cloudsec.set`. Connecting GitHub with the
  automatic setup below needs a few more permissions, listed in that section.
- For GitHub, someone who is an **owner of the GitHub organization** is
  available to approve the App.

## GitHub: let LimaCharlie create the App

This is the fastest path. The console creates a GitHub App in your GitHub
organization with the right permissions, its webhook, and the rules that react
to pushes and pull requests. Nobody has to configure a webhook by hand.

1. Go to **Cloud Security → Settings → Providers → Add provider → GitHub** and
   choose **Create a GitHub App for me (recommended)**.
2. Name the connection, then enter the GitHub **organization** slug and a name
   for the App. The App name defaults to `LimaCharlie <organization>` and must be
   unique on GitHub.
3. Choose the options:
    - **Allow AutoFix to open fix pull requests** gives the App **Contents: Read
      and write**. Leave it off unless you want
      [AutoFix pull requests](autofix.md). You can grant it later.
    - **Turn on code scanning with pull-request checks** creates a
      [starter policy](#the-starter-policy). It is offered, and ticked, only when
      the organization has no code-scanning policy yet.
4. Choose **Continue on GitHub**. GitHub shows the App it is about to create. A
   GitHub organization owner creates it, then installs it on **All
   repositories**.
5. GitHub sends you back to LimaCharlie, which verifies the installation and
   saves the connection.

**Do not close or reload the page until the App's private key is saved.** GitHub
hands over the key only once. If saving fails, keep the page open and choose
**Retry**.

If you ticked the starter policy option, scanning is now on. The first scan
starts on the next pass, usually within minutes. Skip to
[Check that it worked](#check-that-it-worked).

??? info "Permissions this setup needs"
    Your LimaCharlie user or API key needs `cloudsec.get`, `cloudsec.set`,
    `secret.get`, `secret.set`, `cloudsensor.get`, `cloudsensor.set`,
    `ikey.list` and `ikey.set`. The setup stores the App's private key and
    webhook secret, and creates the webhook adapter and its installation key.
    Without all of them, the wizard opens on **I already have a GitHub App** and
    names what is missing.

    Installing the push and pull-request rules also needs `dr.list` and `dr.set`.
    Without them the connection is still saved, and you can install the rules
    later from the **Code security** page.

??? info "What the App is created with"
    | Permission | Access | Used for |
    |---|---|---|
    | Repository: **Actions**, **Administration**, **Code scanning alerts**, **Dependabot alerts**, **Metadata**, **Secret scanning alerts**, **Secrets**, **Webhooks** | Read-only | Inventory and posture ([GitHub provider](../provider-setup/github.md)), and GitHub's own security alerts |
    | Organization: **Administration**, **Members**, **Secrets**, **Webhooks** | Read-only | Inventory and posture |
    | Repository: **Contents** | Read-only, or **Read and write** with AutoFix | Reading code to scan it; writing AutoFix branches |
    | Repository: **Checks**, **Pull requests** | Read and write | Pull-request checks and comments. Nothing is published until the policy turns them on |
    | Webhook | Active, **Push** and **Pull request** events | Push rescans and pull-request checks |

    The App belongs to your GitHub organization and can be installed only there.
    You can edit or delete it like any other App. Its private key and webhook
    secret are stored in your LimaCharlie organization's secrets, never in the
    browser.

??? note "When the setup does not finish in one go"
    - **You are not a GitHub organization owner.** GitHub only *requests* the
      installation. Once an owner approves it, add the connection with **I
      already have a GitHub App**, using the App ID and credentials the page
      showed.
    - **More than an hour passed.** GitHub requires the App to be created within an
      hour. Start again from Settings.
    - **The page was closed before the private key was saved.** The App may exist
      on GitHub already. Generate a new private key for it on GitHub and connect
      it with **I already have a GitHub App**, or delete it and start again.
    - **A later step failed.** Once the key is saved, the setup can be resumed for
      7 days from the same browser. Choose **Retry**, or come back to the page.
    - **The webhook or the rules could not be set.** The connection is still
      saved. Finish from the **GitHub webhooks** section on the **Code security**
      Overview tab. See [Webhook status](pull-requests.md#webhook-status).

### The starter policy

The **Turn on code scanning with pull-request checks** option creates one
code-scanning policy, and only if the organization has none when the connection
is saved. It:

- scans **every repository the App can see**, daily;
- runs the dependency, secrets, infrastructure-as-code, static-analysis and
  license engines;
- publishes pull-request checks that report findings without blocking merges
  (`pr_checks: true`, no `gating.fail_on`), and posts no pull-request comments.

Edit it any time under **Cloud Security → Policies → Code scanning**. See
[Scan policy](policy.md).

## GitHub: use an App you already have

If you already connected GitHub for Cloud Security, add **Contents: Read-only**
to its GitHub App. That permission lets LimaCharlie read code:

1. On GitHub, open **Organization → Settings → Developer settings → GitHub
   Apps → your App → Permissions & events** and set **Repository → Contents**
   to **Read-only**.
2. A GitHub organization owner **approves the permission change** on the
   organization's installation page. GitHub does not apply a permission increase
   until an owner accepts it.
3. [Create a policy](#create-a-policy).

Without **Contents**, repositories selected for scanning report
`github_app_missing_contents_permission` rather than failing silently.

For push rescans and pull-request checks with your own App, also follow
[Webhook status](pull-requests.md#webhook-status). The full permission list is in
[GitHub provider setup](../provider-setup/github.md).

## GitLab or Bitbucket Cloud

Reading repositories is part of the connection's required token scopes, so there
is nothing extra to grant.

1. Connect the provider: [GitLab setup](../provider-setup/gitlab.md) or
   [Bitbucket Cloud setup](../provider-setup/bitbucket.md).
2. [Create a policy](#create-a-policy).

GitLab code scanning works for **GitLab.com** only. A self-managed GitLab
instance can be connected for inventory, but its projects cannot be scanned.
Pull-request checks, push rescans and AutoFix are GitHub-only. GitLab and
Bitbucket repositories are scanned on the policy's schedule.

## Create a policy

In the console, open **Cloud Security → Policies → Code scanning**:

1. Turn on **Enable code scanning**.
2. Under **Repositories → Include**, add the repositories to scan, as
   `<owner>/<repository>` or a glob such as `acme/api-*`. For GitLab subgroups,
   use the full path, such as `acme/platform/api`. **An empty include list scans
   every repository the connection can see.**
3. Review the engines. Dependencies, secrets, infrastructure as code, static
   analysis and licenses are on by default.
4. Save.

Or as code:

```yaml
# code-policy.yaml
policy_type: code_scanning
enabled: true
repos:
  include: ["acme/api-*", "acme/payments"]
scanners:
  sca: true
  secrets: true
  iac: true
  licenses: true
```

```bash
limacharlie hive set --hive-name cloudsec_policy --key code-scanning \
    --input-file code-policy.yaml --enabled
```

Static analysis is not listed above because it runs unless a policy sets
`sast: false`. Every field is described in [Scan policy](policy.md).

## Check that it worked

Open **Cloud Security → Code security → Repositories**. Each selected repository
shows **Scanned** once the first pass reaches it, with the time of the scan.
Large organizations take longer on the first pass.

From the CLI:

```bash
# Has the lane run, and did anything fail?
limacharlie cloudsec code status

# Repositories with their scan status and open findings.
limacharlie cloudsec code repos --with-findings

# Scan one repository now instead of waiting.
limacharlie cloudsec code rescan acme/payments
```

If a repository stays unscanned, see [Troubleshooting](troubleshooting.md).

## Next steps

- [Working with results](results.md): triage what the first scan found.
- [Pull-request checks and push rescans](pull-requests.md): catch problems before they merge.
- [AutoFix pull requests](autofix.md): have LimaCharlie open dependency upgrades.
