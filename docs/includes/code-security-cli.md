!!! note "Install the CLI"
    CLI examples require a build that includes the `cloudsec code` commands.
    Check your installation before running them:

    ```bash
    limacharlie cloudsec code --help
    ```

    These commands are not yet in the stable CLI release. Use the web console
    or REST API, or a development build from the
    [public SDK repository](https://github.com/refractionPOINT/python-limacharlie).

    Installing the CLI does not enable a server capability. Hosted scanning
    and advanced evidence features depend on availability in your organization's
    data region. Check **Code security → Overview**, `code capabilities` and
    `code status`; if you see `code_lane_not_enabled_in_datacenter`, contact
    LimaCharlie before completing hosted-scan setup.
