# Git Sync

The Git Sync Extension automates the management of Infrastructure-as-Code (IaC) configurations. It synchronizes changes between a Git repository and target organizations. This makes the deployment and management of infrastructure less complex.

**Key features:**

- **Centralized Configuration:** Stores all IaC configurations in a single Git repository.
- **Recurring Apply:** Can synchronize IaC changes between Git and LC organizations automatically at regular intervals.
- **Recurring Export:** Can export IaC from LC organizations to GitHub automatically at regular intervals.
- **Export Request:** Lets you export the configuration of an Organization into the Git repository.
- **Automated Deployment:** Helps automate the deployment process. This decreases manual work.
- MSSP**-Friendly:** Designed for many organizations in a single repository. Orgs can share global configurations.
- **Flexible Configuration:** Lets you customize the configuration and add more configuration directories.
- **Transparent Operations:** Tracks operations through an extension Sensor.

Use `ext-git-sync` to make your IaC workflows more efficient, improve consistency, and decrease the risk of errors.

## Use Cases

### Sync FROM Git

If your git repository has the correct structure and contains org configurations, the extension can synchronize the running org configurations with the configs in git.

![d2 (1).png "pull config(1).png"](../../../assets/images/d2-(1).png "pull_config(1).png")

### Export TO Git

If you have an empty git repository, you can configure the extension to export the current org configuration to it. The extension puts the configuration in an `exports` subdirectory.

![d2 (2).png "push config(1).png"](../../../assets/images/d2-(2).png "push_config(1).png")

## Git Repo Structure

To apply org configs from a git repository, the repo must obey this structure. The root of the repository must contain an `orgs` directory. The `orgs` directory must contain `[org-id]` child directories, and each one must contain an `index.yaml`.

```text
.
└── orgs [required]
    └── a326700d-3cd7-49d1-ad08-20b396d8549d [required]
        └── index.yaml [required]
```

The `index.yaml` file decides which other files in the repo are part of the configuration for this org.

For example, assume that all configurations for this org are unique to it, and that they are inside the directory of the org.

```text
.
└── orgs
    └── a326700d-3cd7-49d1-ad08-20b396d8549d
        ├── extensions.yaml
        ├── hives
        │   ├── cloud_sensor.yaml
        │   ├── dr-general.yaml
        │   ├── dr-managed.yaml
        │   ├── dr-service.yaml
        │   ├── extension_config.yaml
        │   ├── fp.yaml
        │   ├── lookup.yaml
        │   ├── query.yaml
        │   ├── secret.yaml
        │   └── yara.yaml
        ├── index.yaml
        ├── installation_keys.yaml
        ├── org_values.yaml
        ├── outputs.yaml
        └── resources.yaml
```

All configurations for this org are in the directory of the org. In this case, the `index.yaml` file contains the relative paths of the configuration files for this org. The next example shows the contents of `index.yaml` for this use case.

```yaml
version: 3
include:
    - extensions.yaml
    - hives/fp.yaml
    - outputs.yaml
    - resources.yaml
    - hives/query.yaml
    - hives/yara.yaml
    - hives/dr-managed.yaml
    - hives/lookup.yaml
    - hives/dr-service.yaml
    - org_values.yaml
    - installation_keys.yaml
    - hives/secret.yaml
    - hives/cloud_sensor.yaml
    - hives/dr-general.yaml
    - hives/extension_config.yaml
```

### Sharing configurations across multiple orgs

Assume that you have a global rule set that you want to apply to many orgs. You can structure the repo as in the next example.

```text
.
├── hives
│   ├── dr-general.yaml
│   └── yara.yaml
└── orgs
    ├── 7e41e07b-c44c-43a3-b78d-41f34204789d
    │   └── index.yaml
    ├── a326700d-3cd7-49d1-ad08-20b396d8549d
    │   └── index.yaml
    └── cb639126-e0bc-4563-a577-2e559c0610b2
        └── index.yaml
```

The related `index.yaml` file at each org level is similar to this

```yaml
version: 3
include:
    - ../../hives/yara.yaml
    - ../../hives/dr-general.yaml
```

### Exporting configurations

The extension puts configuration exports in a separate `exports` subdirectory. This stops the exports from overwriting configurations that you push to many organizations.

```text
.
└── exports
    └── orgs
        └── a326700d-3cd7-49d1-ad08-20b396d8549d
            ├── extensions.yaml
            ├── hives
            │   ├── cloud_sensor.yaml
            │   ├── dr-general.yaml
            │   ├── dr-managed.yaml
            │   ├── dr-service.yaml
            │   ├── extension_config.yaml
            │   ├── fp.yaml
            │   ├── lookup.yaml
            │   ├── query.yaml
            │   ├── secret.yaml
            │   └── yara.yaml
            ├── index.yaml
            ├── installation_keys.yaml
            ├── org_values.yaml
            ├── outputs.yaml
            └── resources.yaml
```

## Setting up Git Sync with Github

This guide explains how to configure Git synchronization between GitHub and LimaCharlie. Git synchronization gives you automated deployment and version control of your security configurations.

### Step 0: Making a Git Sync specific SSH Key

- Create the directory

`mkdir -p ~/.ssh/gitsync`

- Set the correct permissions on the directory

`chmod 700 ~/.ssh/gitsync`

- Generate the SSH key

`ssh-keygen -t ed25519 -C "limacharlie-gitsync" -f ~/.ssh/gitsync/id_ed25519`

### Step 1: Generate GitHub Deploy Keys

1. Open your GitHub repository
2. Click the **Settings** tab
3. In the left sidebar, select **Deploy keys**
4. Click the **Add deploy key** button
5. Enter a descriptive title for your key (e.g., "LimaCharlie Git Sync Integration")
6. Paste your public SSH key into the "Key" field
7. **Important:** Check the box for **Allow write access**
8. Click **Add key** to save

### Step 2: Store SSH Private Key in LimaCharlie

1. Log in to your LimaCharlie account
2. Open the **Secret Manager** section of your Organization
3. Click **Create New Secret**
4. Choose a descriptive name for your secret (e.g., "github-deploy-key")
5. Paste the **private** part of your SSH key into the value field
6. Save the secret

### Step 3: Configure Git Sync in LimaCharlie

1. Open the **Git Sync** section in LimaCharlie
2. Under the **SSH Key** section, select **Secret Manager**
3. From the dropdown menu, select the secret you created in Step 2
4. Set the **user name** to `git`
5. Copy the SSH URL from your GitHub repository (found on the repository's main page, under Code)
6. Paste the SSH URL into the **repository** URL field in LimaCharlie
7. Configure the **branch** name (required)
8. Select the push and pull options. These options set which items to push to or pull from Git configurations.
9. Optionally, select push and pull schedules to synchronize or export your Infrastructure as Code configurations to and from LimaCharlie at regular times. This creates D&R rules in the cloud that start the push and pull actions on the selected schedule or interval.
10. Click **save settings**.

### Step 4: Verify Integration

1. Do a test commit to your GitHub repository. Click "Push to Git" in the upper right corner.

2. Check that your configuration is now in Github.

### Troubleshooting

If you have synchronization problems:

- Check that the deploy key has write permissions
- Make sure that the SSH URL has the correct format (it must begin with `git@github.com:`)
- Check that the private key in Secret Manager matches the public key that you added to GitHub

[Infrastructure](infrastructure.md)
