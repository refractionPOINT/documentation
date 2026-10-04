# Email Security and Code Security billing

Email Security and Code Security have separate paid coverage. Paying for endpoint
security or another product does not automatically buy either one. Enabling an
extension starts setup; paid coverage requires explicit price acceptance and
confirmation from the protection service.

| Product | Paid rate | New organization trial |
|---|---|---|
| Email Security | $1 per protected mailbox-month | 14 days, up to 25 mailboxes |
| Code Security | $0.80 per protected repository-month, plus the existing Cloud Security base fee | 14 days, up to 10 repositories |

Trials cover the organization across its connections. Shared mailboxes and repeated
references to the same repository count once when they have the same stable identity.
Code includes hosted repositories and external scanner imports; container images do
not contribute to this repository meter. Telemetry and other services remain separately
priced. The console shows the organization's actual Cloud base fee; it is not included
in the $0.80 rate.

## Trial and coverage

A new trial starts at the first protected resource. Unsubscribing, resubscribing or
restarting a connection does not restart it. Use the server's trial deadline and
coverage status instead of calculating entitlement from a browser clock.

Organizations enabled before billing enforcement receive a fresh 14-day trial from
the enforcement instant. Their existing protected set stays free for those 14 days,
including sets above 25 mailboxes or 10 repositories. This exception preserves the
existing set; it does not allow unlimited expansion or swapping in an unlimited number
of new resources. New organizations and growth beyond that baseline follow the normal
limits. Existing paid protection is not silently converted into a new charge without
price acceptance.

Use Email Security mailbox scope and exclusions to choose coverage. Code's scanning
settings select repository coverage. Review resources that are discovered but not
protected; a successful configuration save is not proof that protection has started.
When eligibility expires, unpaid protection can pause. Configuration and existing
data follow the product's retention policy and scheduled-deletion notices. Review
those notices before the deadline; paying does not retroactively analyze work missed
while coverage was paused.

## Purchase and check acknowledgement

In **Billing & Usage**, or the product's overview, review trial status, protected
count, limits and the current rates. Add a payment method through the billing page
(or use authorized invoicing), then select the price-acceptance checkbox and
**Activate paid coverage**.

Billing status requires `org.get` and `billing.ctrl`. Changing paid coverage also
requires `user.ctrl`. Analysts without billing permission can still inspect product
coverage and trial information through the product's read surface without access to
payer or financial details.

A request can remain **Pending** while billing or protection reconciles. Do not treat
an HTTP success or a saved configuration as paid coverage. Refresh until the server
reports acknowledged paid protection. A failed or unavailable response does not
establish coverage; correct the payment method or contact support as indicated.
An HTTP 200 mutation with `acknowledged: false` is committed but pending; poll GET
until its control settles and protection matches the requested change. HTTP 503
is retryable after refreshing status and does not confirm paid coverage. Activation
may be temporarily unavailable during rollout while reads and stop remain available.

The billing API uses the same routes for both products:

| Operation | Route |
|---|---|
| Status and cost | `GET /v1/orgs/{oid}/billing/security/{product}` |
| Accept pricing and request activation | `POST /v1/orgs/{oid}/billing/security/{product}` with `{"accept_pricing":true,"accepted_quote":<complete status.pricing_quote>}` |
| Request paid stop | `DELETE /v1/orgs/{oid}/billing/security/{product}` |

`product` is `mail_security` or `code_security`. Optional GET parameters `from` and
`until` must be supplied together as UTC dates `YYYY-MM-DD`. The beginning is
inclusive, the end exclusive, and the maximum range is 366 days. Without a custom
range, use the returned billing period; an invoice interval can differ from a calendar
month. The normalized `status` contains phase, acknowledged protection, trial limits,
pending control, rates and costs. Fields whose authority is unavailable are omitted
or null; do not interpret missing fields as paid or as zero cost.

### Accept the exact quoted price

GET returns `status.quote_guard_version: 1` and `status.pricing_quote`. All nine
quote fields are required: `version`, `quote_id`, `product`, `currency`,
`monthly_cents`, `days_per_month`, `cloud_base_monthly_cents`, `meter_price_id`,
and `cloud_price_id`. Email's Cloud amount is `0` and price ID is an empty string;
these fields are still required. Review the rates and send the entire quote unchanged
in `accepted_quote`. Its opaque ID binds organization, payer and billing mode as
well as prices. It accepts rates, not a fixed future population or monthly total.

If pricing changed, POST returns HTTP 409 `reason: security_quote_changed` before
recording consent or performing purchase effects. Refetch GET, review the new quote,
and obtain fresh consent. The console clears its checkbox. Do not silently accept
a freshly fetched replacement quote. Missing pricing or an unsupported quote guard
pauses purchasing.

With a CLI version supporting quoted purchases, save the quote you will review:

```sh
limacharlie billing security get mail_security --oid <organization-uuid> --output json > security-status.json
python3 -c 'import json; s=json.load(open("security-status.json")); assert s["status"]["quote_guard_version"] == 1; print(json.dumps(s["status"]["pricing_quote"], indent=2))' > accepted-quote.json
cat accepted-quote.json
# After reviewing the quote:
limacharlie billing security activate mail_security --accepted-quote accepted-quote.json --accept-pricing --oid <organization-uuid> --output yaml
limacharlie billing security get mail_security --oid <organization-uuid> --output yaml
# Explicit manual stop; then poll GET for acknowledgement:
limacharlie billing security stop mail_security --confirm --oid <organization-uuid> --output yaml
```

Use `code_security` for Code; its quote also discloses the separate Cloud fee.
The SDK class `limacharlie.sdk.billing.Billing` accepts `Billing(org).activate_security("mail_security", accept_pricing=True,
accepted_quote=reviewed_quote)`, with the complete quote from
`Billing(org).get_security("mail_security")`. Both surfaces preserve pending
responses and API errors instead of claiming that purchase has completed.

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

## Stop, payment failure and recovery

**Stop paid coverage** requests an end to future paid eligibility. Check the returned
pending control and refresh until the protection service acknowledges the stop.
Already accrued usage remains payable; the final day's peak is preserved. Stopping
does not reset the trial or immediately erase configuration and data. Any remaining
valid trial or grant can still permit unpaid coverage under its limits.

Stopping Code paid coverage **keeps the separate Cloud Security subscription and
base fee**. Stopping that subscription is a separate operation and also affects Code
eligibility. Do not assume the repository stop removes every Cloud charge.

A first failed payment does not immediately remove existing paid protection. Owners
are notified while Stripe retries, with a maximum seven-day grace. Protection stops
at terminal unpaid/canceled status or the grace deadline. Scheduled cancellation
keeps coverage until its effective end. Payment recovery can resume previously
consented, payment-suspended coverage; it does not undo a voluntary product stop.

Keep the billing contact and payment method current, and inspect pending or suspended
status promptly. Neither a payment-method update nor a callback alone proves that
protection has resumed: verify the authoritative product acknowledgement.
