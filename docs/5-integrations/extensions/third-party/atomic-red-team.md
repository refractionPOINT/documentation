# Atomic Red Team

**Atomic Red Team** is a library of tests from Red Canary. The tests map to the MITRE ATT&CK framework. This Extension lets LimaCharlie users test their environments with Atomic Red Team. The tests are fast, portable, and repeatable.

See [the Atomic Red Team project site](https://atomicredteam.io/) for more information.

## Enabling the Atomic Red Team Extension

Enable Atomic Red Team in the LimaCharlie **Marketplace**, or on the [Atomic Red Team extension page](https://beta.app.limacharlie.io/add-ons/extension-detail/ext-atomic-red-team).

Under the Organization dropdown, select the organization that you want to subscribe to Atomic Red Team, then click subscribe.

Extensions apply to one organization at a time. To use Atomic Red Team in more than one organization, subscribe each organization to the extension separately.

## Supported Platforms

The extension supports sensors on **Windows**, **Linux**, and **macOS**. Sensors must be online for tests to run.

If PowerShell Core (`pwsh`) is not present on Linux or macOS, the extension installs it in the Prepare step.

## Three-Step Workflow

The extension uses a workflow of three steps: **Prepare Host** → **Run Tests** → **Cleanup Host**. This is the intended use of the upstream Atomic Red Team project.

### Step 1: Prepare Host

Prepare the target sensor before you run tests. This step installs the Atomic Red Team framework and its dependencies.

**What it does:**

- **Windows**: tries to add a Windows Defender exclusion for `C:\AtomicRedTeam` (Tamper Protection can block this), then installs NuGet, the `powershell-yaml` module, and the Invoke-AtomicRedTeam framework with atomics.
- **Linux**: installs PowerShell Core with the system package manager (apt/dnf), then installs the framework to `/opt/AtomicRedTeam`.
- **macOS**: installs PowerShell Core with the official `.pkg` installer, then installs the framework to `/opt/AtomicRedTeam`.

You prepare a host one time only. After that, you can run as many tests as you want.

### Step 2: Run Tests

1. Select one or more MITRE ATT&CK technique IDs from the dropdown.
2. Click Run.

The tests run in sequence. Each test checks the prerequisites and installs them if they are absent. The test then runs the technique. The test can also run the atomic cleanup step.

The **Clean** option controls the atomic cleanup after each test. The atomic cleanup reverses the changes of that technique. It is separate from the Cleanup step for the host.

If you select more than one test, the extension chains the tests. When a test ends, a callback starts the next test. One `job_id` tracks the full run.

### Step 3: Cleanup Host

After you finish your tests, run Cleanup to reverse the changes from Prepare:

- **Windows**: removes the Defender exclusion and deletes `C:\AtomicRedTeam`.
- **Linux/macOS**: deletes `/opt/AtomicRedTeam`.
- All platforms: uninstalls the `powershell-yaml` PowerShell module.

Cleanup does what it can. If it cannot remove some components, for example locked files, it reports partial success with the details.

## Checking Results

When you enable the extension, an Adapter with the name `ext-atomic-red-team` appears. This adapter receives all extension activity as webhook events:

| Event | When |
|-------|------|
| `prepare_started` / `prepare_success` / `prepare_failed` | Prepare Host lifecycle |
| `run_started` / `test_result` / `run_success` / `run_failed` | Test execution (one `test_result` per technique) |
| `cleanup_started` / `cleanup_success` / `cleanup_failed` | Cleanup Host lifecycle |

Each event includes a `job_id` for correlation and the sensor ID. The `test_result` event includes the technique ID, the status of the run, and a base64-encoded log of the test output.

The **Timeline** of the sensor that ran the test also contains `RECEIPT` events. These events hold the raw output of the run (STDOUT, STDERR, exit code).

Use the webhook events in the `ext-atomic-red-team` adapter with the `RECEIPT` events on the sensor. Together they show which tests passed and which tests failed.

## Notes

- The extension tries to add the Defender exclusion on Windows. If Tamper Protection blocks the exclusion, the extension still installs the framework and reports a warning. Defender can quarantine some atomic test files.
- Some techniques include many sub-tests. For example, T1082 on Windows has 17 or more. A sub-test can time out after 120 seconds. This is a default of the upstream `Invoke-AtomicTest`, not a limit of the extension.
- The extension loads the list of available techniques from the upstream Atomic Red Team index when it starts.
