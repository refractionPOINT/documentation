!!! note "Install the CLI"
    CLI examples require LimaCharlie CLI **5.7.0 or later**, which includes the
    `cloudsec code` commands. Install or upgrade, then check:

    ```bash
    python -m pip install --upgrade limacharlie
    limacharlie cloudsec code --help
    ```

    Installing the CLI does not enable a server capability. Hosted scanning
    and advanced evidence features depend on availability in your organization's
    data region. Check **Code security → Overview**, `code capabilities` and
    `code status`; if you see `code_lane_not_enabled_in_datacenter`, contact
    LimaCharlie before completing hosted-scan setup.
