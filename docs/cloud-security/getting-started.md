# Getting Started with Cloud Security

Connect an account you administer to discover resources, identities, and security
findings. This guide uses the web app. Your first goal is to **connect one
provider, confirm that resources appear, and inspect a finding**.

A **provider** is a service such as AWS, Google Cloud, Microsoft Azure, or GitHub.
A **connection** gives LimaCharlie access to a specific account, project, tenant,
or organization in that service. **Scope** means the part of that service you
want to collect. A **finding** is a potential security issue identified in the
collected data; an empty findings list does not by itself prove collection worked.

## Before you start

- Sign in to LimaCharlie and select the organization that should hold the data.
  An organization is your team's workspace.
- Choose one account or project you administer and know contains resources.
  Starting small makes it easier to recognize whether collection worked.
- Have an administrator of that provider available to create the credential and
  grant access. Being an administrator in LimaCharlie does not grant access to
  AWS, Microsoft, Google, or another provider.
- Ask your LimaCharlie administrator for permission to subscribe and configure
  connections if those actions are unavailable. Subscribing requires
  `billing.ctrl` and `user.ctrl`; testing requires `cloudsec.set`.

!!! info "Free trial"
    Free-tier organizations can connect up to **2 providers** for a **14-day**
    collection trial, starting when Cloud Security is enabled. Prepare provider
    access first. At trial expiry, or when exceeding the connection limit,
    affected collection pauses. Review the status in **Settings → Providers**
    and the trial information in Overview before expanding your setup.

## 1. Enable Cloud Security

Open **Extensions → Cloud Security** and select **Subscribe**. Then open
**Cloud Security** from your organization's sidebar. You may also arrive here
through Cloud Security signup after creating your organization.

Before a provider has data, the workspace directs you to Settings. This is
expected; other pages become available as you connect and collect data.

<span id="2-connect-a-provider"></span>

## 2. Choose your provider and prepare access

Open **Cloud Security → Settings → Providers → Add provider**. Give the
connection a recognizable name, such as `test-aws` or `company-directory`,
and choose the service you want to connect.

For GitHub, use **Create a GitHub App for me (recommended)** when offered.
The wizard prepares the app and stores its credential after an organization
owner installs it; you do not need to create and paste a key manually on that
path. Review the requested access before approving.

Open its [provider setup guide](provider-setup/index.md) in another tab. It
lists administrator prerequisites, where to find IDs, how to create credentials,
and how to fix provider-specific errors. Common starting points:

| What you want to inspect | Guide |
|---|---|
| AWS resources in an account | [AWS](provider-setup/aws.md) |
| Resources in a Google Cloud project | [Google Cloud](provider-setup/gcp.md) |
| Resources in an Azure subscription | [Azure](provider-setup/azure.md) |
| Microsoft directory users and access, without an Azure subscription | [Microsoft Entra ID](provider-setup/entra.md) |
| Google Workspace users and configuration | [Google Workspace](provider-setup/google-workspace.md) |
| GitHub repositories and organization | [GitHub](provider-setup/github.md) |
| Another supported service | [All provider guides](provider-setup/index.md) |

Google Workspace Cloud Security inspects configuration and identity. To analyze
individual email messages, use [Email Security](../email-security/getting-started.md).

## 3. Complete the wizard

### Configuration: choose what to inspect

Enter the account, tenant, project, or organization identifiers from the provider
guide. These are IDs from that service, not your LimaCharlie organization ID.
For Google Cloud, a single project is a useful starting scope; use the project
ID, not its display name. Wider folder/organization access requires corresponding
grants.

If you enter **internal domains**, list the email domains used by your own staff
(for example, `example.com`). This helps distinguish staff from external users.
The product can discover the primary cloud organization domain, but you should
include secondary domains your staff use too.

<span id="test-the-credential-before-saving"></span>

### Permissions: grant access and store the credential

A credential is a key or token used to access the provider. LimaCharlie stores
it in **Secrets Manager**, separately from the connection settings.

1. Follow the selected provider's setup guide. The wizard lists required grants
   and optional grants with the capabilities they enable.
2. If the credential is already saved in LimaCharlie, select it. Otherwise,
   select **New secret**, choose a name, and paste the credential in the format
   shown. Do not wrap it in an extra `secret` property.
3. Select **Test Provider** once the configuration and credential are ready.
   Fix required failures before saving. For optional failures, read which data
   will be missing and decide whether you need it.

Choose **Web console** in the provider guides for browser instructions. The
command tabs are an alternative for administrators comfortable with a terminal.
Use Cloud Shell or install and sign in to the provider's CLI, select
the intended account, and replace any remaining placeholders. Those commands
create access credentials; collection itself reads provider data. Some provider
keys allow broader access than the collector uses—the wizard and provider guide
explain those exceptions.

If **New secret** is unavailable, ask an administrator with Secrets Manager
write access to save the credential for you. Never paste it into a connection
name or account ID field.

GitHub setup may also offer an optional **Code Actions App** step. Read its access
requirements before enabling features that write checks or propose code changes.
You can begin with the collection path and configure those features later.

### Sync cadence: choose how often to collect

Keep the service default for a first connection. **Sync cadence** is the interval
between collections, not a deadline for the first scan. You can change it later.

### Summary: save and start collection

Review the scope, credential name, and optional features, then select **Add
provider**. Saving an enabled connection starts collection. A saved connection
is not proof of a successful scan.

<span id="3-watch-the-first-sweep"></span>

## 4. Verify the first collection

The completion screen shows scan progress. Return to **Settings → Providers**
to inspect **Status**, **Resources**, and **Last sync**.

| What you see | What to do |
|---|---|
| Queued or in progress | Allow time for collection. Large accounts take longer than small ones. |
| Failed | Read the provider error, edit the connection or grants, and run Test Provider again. |
| Trial/limit pause | Check your trial standing and provider count. Re-entering credentials will not remove a plan limit. |
| Completed, with resources | Open Inventory and confirm a resource you recognize. |
| Completed, but no expected resources | Check account/project IDs, scope, and optional permission failures. A successful credential check does not guarantee access to everything you intended. |

Scan progress is reported by provider type: if you have multiple connections to
the same service, it is not independent proof that each one collected correctly.
Use the intended resource's account/project details to verify your scope.

Use **Sync now** on the provider row after fixing access. See the provider's
setup guide for common error messages and their fixes.

<span id="4-declare-what-matters"></span>
<span id="5-look-at-the-result"></span>

## 5. Understand your first results

Open **Inventory** and find something you recognize, such as a cloud resource or
user. Then open **Risks**. Start with a high-severity finding, read the affected
resource and evidence, and follow its remediation guidance. If no findings
appear, check Inventory and collection status before concluding there are no
issues. See [Findings & Triage](findings.md).

You do not need to configure every policy before exploring your first results.
When collection is working, open **Policies → Data classification** to identify
sensitive resources, such as databases containing customer information. Nothing
is classified sensitive by default. Classification lets the product prioritize
access and attack paths involving that data; use **Simulate** to preview matches
before saving. Classification currently uses resource attributes, not inspection
of the contents of your databases.

## Next steps

- Add a second account or service using [Provider Setup](provider-setup/index.md).
- Learn the day-to-day workflow in [Findings & Triage](findings.md).
- Use [Setup with the CLI](setup-cli.md) for scripted onboarding and the
  [configuration reference](configuration.md) for advanced settings.
