# Free Tier and Limits

Cloud Security has a **perpetual free tier**, like the two free sensors of the
LimaCharlie Community Edition. There is no trial period and no expiry. It is
sized for an individual's home lab or learning environment, for example one
person with a small AWS account. Teams and companies need a paid plan.

An organization is on the free tier when its **configured sensor quota is 2 or
less**. Raising the quota above **2** moves it to a paid plan with no Cloud
Security limits. See [Moving to a paid plan](#moving-to-a-paid-plan).

## What the free tier covers

The limits are counted across **all** of the organization's connections combined.

| Limit | Free tier |
|---|---|
| User accounts | Up to **10** |
| Other resources | Up to **250** |
| Connections | Up to **5**, of any type, including source-control connections such as GitHub, GitLab or Bitbucket |
| Scope of each connection | A single **AWS account**, **GCP project** or **Azure subscription** |
| Repositories scanned (Code Security) | The first **10** by name, per connected source-control organization |
| Container images scanned (Code Security) | The **5** most referenced, per organization |

Everything else in Cloud Security works the same on the free tier: findings,
the security graph, attack paths, compliance, CAASM, automation, the API and the
CLI.

### What counts as a user account

Every user account in any connected identity provider or cloud counts: Microsoft
Entra ID, Okta, Google Workspace, AWS IAM users, Google Cloud and the other
connectors. Guest users count too.

The same person in two providers counts **twice**, because it is two accounts.
A person with an Entra ID account and an Okta account uses two of your 10.

### What counts as another resource

Things that belong to you and exist in your environment:

- virtual machines and instances, and instance groups
- storage buckets and databases
- AI services
- networks and DNS zones
- applications
- Kubernetes clusters, namespaces and workloads
- third-party assets reported by your other tools
- your own groups, service accounts and managed identities, and roles outside
  Entra ID and Azure

### What is not counted

Things you do not own, or that come built in, do not use any of your allowance:

- Microsoft's built-in and first-party applications and service principals that
  exist in every Entra tenant
- Entra ID directory roles and Azure role definitions, including custom ones
- cloud-provider service principals and other principals owned by someone else
- permissions and relationships between entities
- vulnerabilities and findings
- configuration records such as policies and DNS mail records
- mailboxes. The person is already counted as a user, and mailboxes are covered
  by [Email Security's own mailbox limit](../email-security/policy.md)
- the cloud account, project or subscription itself
- code repositories and container images, which have their own limits above

### One scope per connection

On the free tier, each connection covers a single AWS account, a single Google
Cloud project or a single Azure subscription.

- **A connection syncs just the scope it names.** Every Azure connection names a
  subscription, and only that subscription syncs, even when the credential can
  see others. An AWS connection syncs only the account its role
  belongs to, even when that is the management account of an AWS Organization.
  The other accounts and subscriptions the credential can see are not scanned
  and do not count toward your allowance.
- **A connection that spans many scopes is paused.** That means a Google Cloud
  connection scoped to an organization or a folder, and an AWS connection set up
  to scan the member accounts of an AWS Organization. The connection's status
  explains which rule paused it and suggests connecting a single account,
  project or subscription, or upgrading.
- **An Azure connection must be able to read the subscription it names.** If the
  subscription ID is wrong, or the credential has no access to it, Cloud
  Security cannot narrow the connection to that subscription and does not sync
  it as named. Check the ID and give the credential Reader access to that
  subscription.

Saving a connection scoped to a Google Cloud organization or folder, or one that
sets up AWS member-account scanning, is rejected with an explanation of the
single-scope rule. Saving or enabling a sixth connection is rejected with an
explanation of the 5-connection limit. To cover more than one account, project or
subscription, create one connection per account, project or subscription, up to
the 5-connection limit, or move to a paid plan.

## What happens at the limit

Each connection **syncs completely or not at all**. Cloud Security never keeps a
partial inventory, because a partial inventory would hide risks and make your
findings look cleaner than they are.

- **Connections are evaluated in alphabetical order of their connection name.**
  Each one uses whatever allowance the earlier ones left. Name your most
  important connection so that it sorts first.
- **A connection that would push the organization over either limit is paused.**
  Its status in **Settings → Providers** explains why: which limit it would
  exceed, how many user accounts or resources it has, and how much of the
  allowance is left for it.
- **Every pause shows its reason on the connection itself**, whichever rule
  caused it: a user or resource limit, a connection scoped to more than one
  account, project or subscription, or more than 5 connections (only the first 5
  by name are collected). A paused connection is not a failed one: its
  credentials are fine and nothing is wrong with the connection. The
  connection's status in the `scan-status` API carries the same explanation as
  its error, with the sync not running.
- **Adding a connection can pause an existing one.** Because order follows the
  connection name, a new connection whose name sorts earlier is evaluated first
  and can use up the allowance, so a later connection that synced before is
  paused even though it did not grow. Pick connection names with this in mind.
- **A connection that was already syncing and then grows past the limit is
  paused too.** The same happens if an organization moves back to the free tier
  from a paid plan. Its last inventory is **kept but no longer updated**, and the
  connection shows as paused, so stale data is not mistaken for current data.
  The allowance used by its last successful free-tier sync stays reserved.
  After a paid plan, the reservation is based on what the paused sync observed,
  up to **10 user accounts** and **250 other resources**. Connections that sort
  after it do not gain that room while it is paused. Disabling or removing the
  connection frees the reservation.
- **Paused connections are re-checked and resume on their own.** After the
  organization upgrades, a paused connection syncs again within about 15
  minutes, with no action on your part. The same happens when allowance is freed
  for it, for example when you remove another connection. A connection paused
  because it is too large is otherwise counted again about once a day, so after
  you remove users or resources at the provider it can take up to a day to
  resume.

Nothing is deleted when a connection is paused, and its configuration and
credential are untouched.

### See your usage

The Cloud Security console shows how much of the allowance is used, for example
*4 of 10 user accounts, 120 of 250 resources used*, and which connections are
paused because of the limit. The [`GET /free-tier`](api-reference.md) route
reports the same usage and limits, and lists the connections paused over a user
or resource limit.

### Choose what to connect

Because the allowance is shared, the best use of it is to connect the account,
project or subscription you most need to understand. For a home lab, that is
usually one cloud account and the identity provider you sign in with.

## Moving to a paid plan

Raise the organization's configured sensor quota above **2**, to at least 3, on
the console's billing page. With Cloud Security subscribed:

- the user, resource, connection and single-scope limits no longer apply
- paused connections resume automatically, within about 15 minutes
- usage is billed as described in
  [security product billing](../7-administration/billing/security-products.md)

Lowering the quota back to 2 or less returns the organization to the free tier,
and the limits apply again as described above.

## Frequently asked questions

### Why didn't my Azure connection sync on the free tier?

Open **Settings → Providers** and read the message on the connection. The common
causes are:

- The connection would push the organization past **10 user accounts** or
  **250 other resources**. An Azure subscription backed by a busy Entra tenant
  is the usual cause, because every user and guest in the directory counts.
- The credential cannot read the subscription the connection names. Check that
  the subscription ID is correct and that the credential has Reader access to
  it.
- The organization has more than **5 connections**, for example after moving
  back from a paid plan, and this one is not in the first 5 by name.
- An earlier connection, in alphabetical order, used the allowance first. This
  includes a connection you added after this one synced.

Re-entering credentials does not lift a plan limit. Remove a connection you no
longer need, fix the subscription ID or its access, or upgrade.

### Why is the number of user accounts higher than the number of people?

Each account in each provider counts, including guest users. One person with an
Entra ID account, an Okta account and an AWS IAM user is three accounts.

### Why is a connection paused when it synced before?

It grew past the limit, the organization moved back to the free tier, or a
connection added since then sorts earlier by name and used the allowance first.
Its last inventory is kept and shown as paused. It resumes by itself after you free up
allowance or upgrade.

### Can I use a few user accounts and many cloud resources?

The two limits are separate and both apply: 10 user accounts and 250 other
resources. Using fewer of one does not raise the other.

### Is anything deleted when I run out of allowance?

No. A connection that cannot sync is paused, and what was already collected is
kept.

### Does a GitHub, GitLab or Bitbucket connection count toward the 5 connections?

Yes. Every enabled connection counts toward the limit of 5, whatever its type:
cloud accounts, identity providers and source-control connections alike.
Disabling a connection frees its slot.

### Do code repositories and container images use up the 250 resources?

No. [Code Security](code-security/index.md) has its own limits of 10
repositories and 5 container images. See
[the Code Security limits](code-security/reference.md#limits).
