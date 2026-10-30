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

## Email Security free tier

An organization is on the LimaCharlie free tier when its **configured sensor
quota is 2 or less**, like the two free sensors of the Community Edition.
Email Security has a **perpetual** free allowance for these organizations:

- Up to **10 protected mailboxes per organization**, across all mail connections.
- No trial, no expiry, no pause. The allowance lasts as long as the organization
  stays on the free tier.
- Free tier only. An organization with a sensor quota above **2** is on a paid
  plan and every protected mailbox is billed.
- **Mailboxes beyond 10 are not protected.** If a free organization has more than
  10 protected mailboxes, for example after moving down from a paid plan, the
  extras are moved out of protection and 10 stay protected. Mail that was
  already analyzed is not deleted.

To protect more than 10 mailboxes, raise the sensor quota above 2 (see
[Moving to a paid plan](#moving-to-a-paid-plan)). From then on, **every**
protected mailbox is billed at $1 per month, including the first 10: the free
allowance is not subtracted from the bill, the same as sensors.

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
- Up to **5 connections** of any type, each cloud connection covering a single AWS account, Google Cloud
  project or Azure subscription.
- For Code Security, **10 repositories** (per connected source-control
  organization) and **5 container images** (per organization) for hosted
  scanning.

A connection that would exceed the user or resource limit, or that is scoped to
more than one account, project or subscription (a connection that names a single
Azure subscription or AWS account syncs just that one), is paused rather than
partly synced. The reason is shown on the connection, and it resumes
automatically within about 15 minutes of the organization upgrading, or when
allowance is freed. What counts, what does not, and what happens at the limit
are in [Cloud Security free tier and limits](../../cloud-security/free-tier.md).

## Moving to a paid plan

Raise the organization's configured sensor quota above **2** (to at least 3) to
move off the free tier. With the extension subscription in place:

- **Email Security**: the 10-mailbox cap is lifted and every protected mailbox is
  billed.
- **Cloud Security and Code Security**: the free-tier limits are lifted, any
  connection paused by a limit resumes within about 15 minutes, and usage billing
  starts.

See [Email Security getting started](../../email-security/getting-started.md),
[Email Security plans and the mailbox cap](../../email-security/policy.md#plans-the-free-tier-and-the-mailbox-cap),
and [Code Security getting started](../../cloud-security/code-security/getting-started.md)
for setup instructions, and
[Cloud Security free tier and limits](../../cloud-security/free-tier.md) for the
limits and what happens at them. [Billing options](options.md) explains organization and
unified billing.
