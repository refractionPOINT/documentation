!!! warning "Private beta"
    Email Security is in **private beta**. It is not generally available, and
    access is enabled per organization — if the `ext-email-security` extension
    is not in your catalog, this product is not turned on for you yet.

    While it is in beta, expect the surface described here to move: commands,
    fields and event shapes may change between releases, and they may change in
    ways that are not backwards compatible. The MailSec CLI is currently available
    from the Python SDK's **master branch**, ahead of a PyPI release. Install it
    in a virtual environment before running the CLI examples:

    ```bash
    python3 -m venv .venv-mailsec
    source .venv-mailsec/bin/activate
    python -m pip install --upgrade 'git+https://github.com/refractionPOINT/python-limacharlie.git@master'
    limacharlie mailsec --help
    ```

    Use that same installation for `hive` and `secret` commands. Credential-file
    examples also require `jq`. For repeatable
    scripts, replace `master` with the tested commit SHA; `python -m pip freeze`
    records the installed revision. Re-read these pages after upgrading.

    Talk to us before relying on it in production.
