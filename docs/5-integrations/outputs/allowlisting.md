# Adding Outputs to an Allow List

LimaCharlie uses infrastructure with auto-scalers. LimaCharlie therefore has no static IPs and no CIDR that you can use for an allow list (or "whitelisting").

Users add IPs to an allow list for Outputs to limit abuse, and to make sure that webhook data comes from LimaCharlie and not from another source. For this purpose, LimaCharlie supplies a `secret_key` parameter that you use as a *shared secret* between LimaCharlie and your webhook receiver. Each webhook from LimaCharlie includes an `lc-signature` header. This header is an HMAC of the webhook content, computed with the shared `secret_key`.
