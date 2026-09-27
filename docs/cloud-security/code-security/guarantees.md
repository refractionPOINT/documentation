# What Code Security guarantees

Code Security connects a code change to what runs in your cloud, lets you act
on it through an approved LimaCharlie workflow, and checks afterwards whether
the risk is gone. When the evidence is incomplete, it says `unknown` and gives
the reason. It does not fill a gap with a guess.

These are the rules it follows. Each one is enforced in the product, and the
reason codes it returns when a rule is not met are listed in
[Unknown, partial and refusal reasons](reasons.md).

## The rules

**A fix is `verified` only when it runs everywhere in scope.** Every in-scope
deployment must have fresh, complete evidence. Every digest it runs must be a
proven build of the fix, and nothing in scope may still run the vulnerable
digest. For an image fix, each running fixed digest also needs a completed scan
that does not report the issue. The scan must come from a scanner that reported
the original vulnerability, using vulnerability data at least as fresh as the
finding. An image that was never scanned is never treated as clean. For a
dependency fix in a repository, detection must also close the finding. A fix
with no deployment in scope ends as unverifiable, not `verified`. A merged pull
request is progress, not a fix. If the vulnerable digest runs again within 30
days of verification, the run becomes `regressed`. You do not have to delete the
old image from your registry. While it exists, its own finding stays open.

**Every image-to-source link says how it was established.** `inferred` means
the image's build steps and files match a repository you connected. It names the
repository, never the exact build commit. `asserted` means a label or build
record names the source without a trusted signature. `verified` means a
signature was checked for that exact digest. The signature can come from a
Google Cloud Build or GitHub Actions artifact attestation, or from a statement
you pushed that matches a signing identity you trust in your `provenance_trust`
policy. Conflicting evidence is `ambiguous`, never resolved by picking one. Public vendor images that match
none of your connections are reported separately as third-party and do not
count against your coverage. None of this requires a change to your build
pipeline.

**"Not observed" needs a complete telemetry window.** A runtime check says
`not_observed` only when every sensor on the resource reported a complete window.
Missing, late or partial telemetry never gives `not_observed`. The answer is
`present` or `unknown`, with a reason. A package already seen loaded or running
stays `loaded` or `executing`. Runtime evidence never changes a finding's risk
score.

**Every change to your systems has a named approver and a confirmed outcome.**
Fix pull requests (AutoFix included), notifications, tickets, temporary
detections and endpoint isolation all run as remediation runs. A person with the
`cloudsec.respond` permission approves each run, the server derives its target
from the finding, and the outcome comes back through an authenticated callback
that the run records. Temporary controls expire on their own, after at most 7
days, or 4 hours for isolation. If a control cannot be removed on time, a HIGH
finding opens. LimaCharlie never merges, deploys, rolls back or revokes
credentials for you.

**Secrets in Terraform state and plans are never stored.** LimaCharlie refuses
state and plan files. An extractor you run yourself turns them into a map of
resource identities and allowlisted settings, and drops sensitive values before
anything is uploaded. The API refuses maps with secret-looking keys. Secrets
found in code are kept as a salted hash, never the value.

**Code-to-cloud matches are exact or not made.** A finding is attributed to a
cloud resource only on an exact identifier. A declaration that matches several
resources is reported as `ambiguous`. One that matches none is `none`, with a
reason.

**Pull-request summaries don't expose your estate.** In `risk_summary` mode a
pull-request check shows counts and yes/no facts, with no resource names,
account IDs, IP addresses or sensor IDs. When the live lookup fails, the check
publishes its normal scan verdict unchanged.

**Your data stays separate, and leaves when you do.** Every record that holds
your data is keyed to your organization, and every API route checks the caller
against it.
When an organization is deleted or unsubscribes, Code Security data is removed
from the live databases after a 7-day grace period, and remaining backup copies
expire within 7 days after that. Scan result files expire within 30 days of
their creation. See [Data handling and privacy](data-handling.md).

## What it does not claim

- It does not prevent a vulnerable change from shipping. Pull-request checks
  block a merge only if you configure them to.
- A finding without a runtime observation is not "not exploitable", and a
  resource without an exposure fact is not "not exposed".
- It does not contain an incident automatically. Every action waits for a
  person.
- Coverage is reported per organization with its denominator. Where the
  denominator is unknown, no percentage is shown.
- Only Cloud Run and GKE deployments are traced to an image digest today.
