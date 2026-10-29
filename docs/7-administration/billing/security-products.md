# Email Security and Code Security billing

Email Security and Code Security are generally available. **Subscribing to the
extension is the purchase**. Subscribe to **Email Security** for mailbox
protection or **Cloud Security** for Code Security, then configure the mail
connections or repository scanning policies you want to use.

## Pricing

| Product | Monthly rate | Daily billing |
|---|---|---|
| Email Security | **$1 per protected mailbox** | That day's protected-mailbox count × **$1/30** |
| Code Security | **$0.80 per protected repository**, plus the existing **Cloud Security base fee** | That day's protected-repository count × **$0.80/30** for repository usage |

Usage is billed per day using a **30-day divisor**. Each protected mailbox-day
or repository-day contributes the daily rate, so changes in coverage affect the
days on which that coverage is protected.

The existing Cloud Security base fee applies separately from daily repository
usage charges.

## Email Security free-tier trial

An organization is on the LimaCharlie free tier when its **configured sensor
quota is 2 or less**. Email Security receives a limited **14-day trial** on the
free tier. Organizations with a sensor quota above **2** are on a paid plan and
usage is billed.

| Product | Trial limits | At expiry | Purge grace period |
|---|---|---|---|
| Email Security | **25 protected mailboxes per organization**, across all connections | Collection pauses; configuration is kept | **30 days** |

Data is removed after the purge grace period unless the organization moves off
the free tier before the purge. The grace period starts when the cleanup process
observes trial expiry; deletion runs asynchronously. Normal data-retention
policies continue to apply during the grace period. Unsubscribing and
resubscribing does not restart the trial.

## Cloud Security free tier

Cloud Security, including Code Security, has a **perpetual** free tier for
organizations on the free tier (**configured sensor quota of 2 or less**), like
the two free sensors of the Community Edition. There is no trial period and no
expiry. It is sized for an individual's home lab or learning environment, for
example one person with a small AWS account. Teams and companies need a paid
plan.

The limits are counted across **all** of the organization's connections combined:

- Up to **10 user accounts**.
- Up to **250 other resources**, such as virtual machines, storage buckets,
  databases, networks and Kubernetes workloads.
- Up to **5 connections**, each covering a single AWS account, Google Cloud
  project or Azure subscription.
- For Code Security, **10 repositories** (per connected source-control
  organization) and **5 container images** (per organization) for hosted
  scanning.

A connection that would exceed the user or resource limit is paused rather than
partly synced, and resumes automatically when the organization upgrades or
allowance is freed. What counts, what does not, and what happens at the limit
are in [Cloud Security free tier and limits](../../cloud-security/free-tier.md).

## Moving to a paid plan

Raise the organization's configured sensor quota above **2** to move off the
free tier. With the extension subscription in place:

- **Email Security**: this lifts the trial limits, allows collection to resume,
  and starts usage billing. Upgrading before the purge cancels deletion
  scheduled because the trial expired.
- **Cloud Security and Code Security**: this lifts the free-tier limits, resumes
  any connection paused by a limit within minutes, and starts usage billing.

See [Email Security getting started](../../email-security/getting-started.md),
[Email Security trial details](../../email-security/policy.md#plans-the-free-trial-and-the-mailbox-cap),
and [Code Security getting started](../../cloud-security/code-security/getting-started.md)
for setup instructions, and
[Cloud Security free tier and limits](../../cloud-security/free-tier.md) for the
limits and what happens at them. [Billing options](options.md) explains organization and
unified billing.
