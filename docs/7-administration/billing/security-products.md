# Email Security and Code Security billing

Email Security and Code Security are generally available. **Subscribing to the
extension is the purchase**. Subscribe to **Email Security** for mailbox
protection or **Cloud Security** for Code Security, then configure the mail
connections or repository scanning policies you want to use.

## Pricing

| Product | Monthly rate | Daily billing |
|---|---|---|
| Email Security | **$1 per protected mailbox** | That day's protected-mailbox count × **$1/30** |
| Code Security | **$0.80 per protected repository**, plus the existing **Cloud Security base fee** | That day's protected-repository count × **$0.80/30**, plus the base fee |

Usage is billed per day using a **30-day divisor**. Each protected mailbox-day
or repository-day contributes the daily rate, so changes in coverage affect the
days on which that coverage is protected.

## Free-tier trials

An organization is on the LimaCharlie free tier when its **configured sensor
quota is 2 or less**. These organizations receive a limited **14-day trial**.
Organizations with a sensor quota above **2** are on a paid plan and usage is
billed.

| Product | Trial limits | At expiry | Purge grace period |
|---|---|---|---|
| Email Security | **25 protected mailboxes per organization**, across all connections | Collection pauses; configuration is kept | **30 days** |
| Code Security / Cloud Security | **2 provider connections**, **10 repositories per connection**, **5 container images per organization** for hosted scanning | Collection and hosted scanning pause; provider configuration and policies are kept | **7 days** |

Data is removed after the purge grace period unless the organization moves off
the free tier before the purge. The grace period starts when the cleanup process
observes trial expiry; deletion runs asynchronously. Normal data-retention
policies continue to apply during the grace period. Unsubscribing and
resubscribing does not restart the trial.

## Moving to a paid plan

Raise the organization's configured sensor quota above **2** to move off the
free tier. With the extension subscription in place, this lifts the trial
limits, allows collection or scanning to resume, and starts usage billing.
Upgrading before the purge cancels deletion scheduled because the trial expired.

See [Email Security getting started](../../email-security/getting-started.md),
[Email Security trial details](../../email-security/policy.md#plans-the-free-trial-and-the-mailbox-cap),
and [Code Security getting started](../../cloud-security/code-security/getting-started.md)
for setup instructions. [Billing options](options.md) explains organization and
unified billing.
