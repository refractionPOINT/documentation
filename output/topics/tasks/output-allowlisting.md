# Adding Outputs to an Allow List

At LimaCharlie, we rely on infrastructure with auto-scalers, and thus do not have static IPs nor a CIDR that you can rely on for an allow list (or "whitelisting").

Typically, the concern around adding IPs to an allow list for Outputs is based on wanting to limit abuse and ensure that data from webhooks is truly coming from LimaCharlie and not other sources. To address this, we provide a `secret_key` parameter that can be used as a *shared secret* between LimaCharlie and your webhook receiver. 

## Authentication Using Secret Keys

When you configure an Output with a `secret_key`, LimaCharlie includes an `lc-signature` header in every webhook request. This header contains an HMAC (Hash-based Message Authentication Code) of the webhook content, generated using the shared `secret_key`.

### How It Works

1. Configure your Output with a `secret_key` parameter
2. LimaCharlie generates an HMAC signature of the webhook payload using your secret key
3. The signature is included in the `lc-signature` HTTP header with each webhook request
4. Your webhook receiver validates the signature to confirm the request originated from LimaCharlie

This cryptographic approach provides strong authentication without requiring static IP addresses, allowing you to securely receive webhook data while maintaining the flexibility of LimaCharlie's auto-scaling infrastructure.