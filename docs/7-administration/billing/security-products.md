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
  extras are moved out of protection and the earliest-protected mailboxes are
  kept. Mail that was already analyzed is not deleted.

To protect more than 10 mailboxes, raise the sensor quota above 2 (see
[Moving to a paid plan](#moving-to-a-paid-plan)). From then on, **every**
protected mailbox is billed at $1 per month. The 10 free mailboxes are not
deducted, the same as sensors.

## Cloud Security and Code Security free-tier trials

On the same free tier, Cloud Security and Code Security receive a limited
**14-day trial**.

| Product | Trial limits | At expiry | Purge grace period |
|---|---|---|---|
| Code Security / Cloud Security | **2 provider connections**, **10 repositories per connection**, **5 container images per organization** for hosted scanning | Collection and hosted scanning pause; provider configuration and policies are kept | **7 days** |

Data is removed after the purge grace period unless the organization moves off
the free tier before the purge. The grace period starts when the cleanup process
observes trial expiry; deletion runs asynchronously. Normal data-retention
policies continue to apply during the grace period. Unsubscribing and
resubscribing does not restart the trial.

## Moving to a paid plan

Raise the organization's configured sensor quota above **2** (to at least 3) to
move off the free tier. With the extension subscription in place:

- **Email Security**: the 10-mailbox cap is lifted and every protected mailbox is
  billed.
- **Cloud Security and Code Security**: the trial limits are lifted, collection
  or scanning resumes, and usage billing starts. Upgrading before the purge
  cancels deletion scheduled because the trial expired.

See [Email Security getting started](../../email-security/getting-started.md),
[Email Security plans and the mailbox cap](../../email-security/policy.md#plans-the-free-tier-and-the-mailbox-cap),
and [Code Security getting started](../../cloud-security/code-security/getting-started.md)
for setup instructions. [Billing options](options.md) explains organization and
unified billing.
