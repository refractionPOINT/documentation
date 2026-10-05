# Email Security and Code Security billing

Subscribing to the extension purchases coverage, just like other LimaCharlie
extensions. Email Security uses `ext-email-security`; Code Security is included
in `ext-cloud-security`. On a paid plan, coverage starts automatically when the
organization is subscribed and has a payment method or authorized invoicing.
A paid organization is one that is off the free tier. Review the extension's
pricing when subscribing.

| Product | Paid rate | New organization trial |
|---|---|---|
| Email Security | $1 per protected mailbox-month | 14 days, up to 25 mailboxes |
| Code Security | $0.80 per protected repository-month, plus the Cloud Security base fee | 14 days, up to 10 repositories |

Trials cover the organization across its connections. Shared mailboxes and repeated
references to the same repository count once when they have the same stable identity.
Code includes hosted repositories and external scanner imports; container images do
not contribute to this repository meter. Telemetry and other services remain separately
priced. Review the Cloud Security base fee in the extension listing before subscribing;
it is not included in the $0.80 rate.

## Trial and coverage

A new trial starts at the first protected resource. Unsubscribing, resubscribing or
restarting a connection does not restart it. Use the server's trial deadline and
coverage status instead of calculating entitlement from a browser clock.

Organizations enabled before billing enforcement receive a fresh 14-day trial from
the enforcement instant. Their existing protected set stays free for those 14 days,
including sets above 25 mailboxes or 10 repositories. This exception preserves the
existing set; it does not allow unlimited expansion or swapping in an unlimited number
of new resources. New organizations and growth beyond that baseline follow the normal
limits. Trial-period usage stays free for everyone, including organizations on paid plans.

Use Email Security mailbox scope and exclusions to choose coverage. Code's scanning
settings select repository coverage. Review resources that are discovered but not
protected; a successful configuration save is not proof that protection has started.
When eligibility expires, unpaid protection can pause. Configuration and existing
data follow the product's retention policy and scheduled-deletion notices. Review
those notices before the deadline; paying does not retroactively analyze work missed
while coverage was paused.

## Subscribe and check coverage

In **Extensions**, review pricing and subscribe to Email Security or Cloud
Security. Subscribing on a paid organization with a payment method or authorized
invoicing automatically enables paid coverage. Moving a subscribed organization
from the free tier to a paid plan, or adding a payment method to a subscribed paid
organization, also enables it automatically. Trial-period usage remains free.

A free-tier organization receives the trial and pauses when it expires. To keep
protecting resources after the trial, move the organization to a paid plan and
keep the extension subscribed with a payment method or authorized invoicing.

Billing status requires `org.get` and `billing.ctrl`. Analysts without billing
permission can inspect product coverage and trial information through the
product's read surface without access to payer or financial details.

Coverage can remain **Pending** while billing or protection reconciles. Refresh
status until the protection service acknowledges the transition. A saved
configuration or subscription alone does not prove that protection has started.
If coverage is suspended or unavailable, correct the payment method or contact
support as indicated.

Read billing status and costs with
`GET /v1/orgs/{oid}/billing/security/{product}`, where `product` is
`mail_security` or `code_security`. Optional GET parameters `from` and `until`
must be supplied together as UTC dates `YYYY-MM-DD`. The beginning is inclusive,
the end exclusive, and the maximum range is 366 days. Without a custom range,
use the returned billing period; an invoice interval can differ from a calendar
month. The normalized `status` contains phase, acknowledged protection, trial
limits, pending control, rates and costs. Fields whose authority is unavailable
are omitted or null; do not interpret missing fields as paid or as zero cost.

## How cost is calculated

Each UTC day uses the **highest paid protected resource count** reached that day.
Removing resources later that day does not erase the day's peak. Trials are free;
trial observed counts do not become billable resource-days.

The monthly resource rate is divided by a fixed **30** to price each resource-day.
The billing period sums daily peaks and rounds the resulting period amount; it does
not round each resource-day to whole cents.

For example, one paid mailbox protected throughout a 31-day period contributes
31 mailbox-days: `31 × $1 / 30 = $1.0333…`, or approximately **$1.03** before other
charges. One repository contributes `31 × $0.80 / 30 = $0.8266…`, approximately
**$0.83**, plus the separate Cloud base fee. A 28-day period contributes 28/30 of
the resource's monthly rate when coverage stays constant.

The console labels today's count **provisional** because its high-water mark can
still increase. Closed days are settled separately. Accrued cost is an estimate, not
a finalized invoice or the total across telemetry, Cloud fees, tax, discounts and
other products. See the invoice for the final amount.

## Unsubscribe, payment failure and recovery

Unsubscribe from the extension to stop future billing. Moving the organization
back to the free tier also stops paid coverage. Refresh billing and product status
until the protection service acknowledges the change. Already accrued usage
remains payable; the final day's peak is preserved. Neither change resets the
trial or immediately erases configuration and data. Any remaining valid trial or
grant can still permit unpaid coverage under its limits while subscribed.

Unsubscribing from Cloud Security stops Code Security coverage and the Cloud
Security base fee. It also affects the other features of that extension. Review
that impact before unsubscribing.

A first failed payment does not immediately remove existing paid protection.
Owners are notified while Stripe retries, with a maximum seven-day grace.
Protection stops at terminal unpaid/canceled status or the grace deadline.
Scheduled cancellation keeps coverage until its effective end. Payment recovery
can resume coverage when the organization remains subscribed and on a paid plan;
it cannot resume an unsubscribed extension or make a free-tier organization paid.

Keep the billing contact and payment method current, and inspect pending or
suspended status promptly. Neither a payment-method update nor a callback alone
proves that protection has resumed: verify the authoritative product
acknowledgement.
