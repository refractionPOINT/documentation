!!! note "Code Security CLI availability"
    The latest stable `limacharlie` release, **5.6.2**, includes Cloud Security
    posture commands but does **not** include `cloudsec code`, `cloudsec image`,
    Code Security evidence or remediation commands, or the `--repo` / `--source` finding
    filters. Those CLI examples currently require the development version of
    the [public Python SDK](https://github.com/refractionPOINT/python-limacharlie).
    Install it separately from your normal CLI:

    ```bash
    python3 -m venv .venv-code-security
    source .venv-code-security/bin/activate
    python -m pip install --upgrade 'git+https://github.com/refractionPOINT/python-limacharlie.git@master'
    limacharlie cloudsec code --help
    ```

    For repeatable scripts, replace `master` with a tested commit SHA and record
    it with `python -m pip freeze`. Check the selected command's `--help` after
    upgrading. You can also use the console or the documented REST routes with
    the stable CLI's `limacharlie api` command.

    Installing a newer CLI does not enable a server capability. Hosted scanning
    and advanced evidence features depend on availability in your organization's
    data region. Check **Code security → Overview**, `code capabilities` and
    `code status`; if you see `code_lane_not_enabled_in_datacenter`, contact
    LimaCharlie before completing hosted-scan setup.
