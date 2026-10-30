!!! info "Generally available"
    Email Security is generally available. Subscribe to the **Email Security**
    extension in your organization to purchase and enable it. Paid usage costs
    **$1 per protected mailbox per month**, billed daily at **$1/30 per
    mailbox-day**. Free-tier organizations (sensor quota of 2 or less) protect up to
    **10 mailboxes** at no charge, with no time limit.
    See [security product billing](/7-administration/billing/security-products/)
    for pricing, the free allowance and upgrading.

    CLI examples require LimaCharlie CLI **5.7.0 or later**, which includes the
    `mailsec` commands. Install or upgrade, then check:

    ```bash
    python -m pip install --upgrade limacharlie
    limacharlie mailsec --help
    ```

    Credential-file examples also require `jq`.
