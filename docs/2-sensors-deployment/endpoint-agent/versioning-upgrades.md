# Endpoint Agent Versioning and Upgrades

LimaCharlie releases new versions of the endpoint agent often, usually every few weeks. You control which version runs in your Organization. Sensors do not update by default, so you manage versions and deployment yourself.

## Endpoint Agent Components

The LimaCharlie endpoint agent has two main components, each with an independent version:

1. **On-disk agent**: Supplies core identity, cryptography, and transport mechanisms. This component needs updates rarely and usually stays the same.
2. **Over-the-air core**: The main component that gets frequent updates and supplies advanced functions. You can update it through the LimaCharlie cloud.

Updates change the over-the-air component, because it is the easiest component to change. The update size is usually about 3-5 MB.

## Version Labels

LimaCharlie has three version labels that make version management easier:

1. **Latest**: The most recent release with new fixes and features.
2. **Stable**: A version with fewer updates. Use it to keep a slower update rate.
3. **Experimental**: The beta version of the next "Latest" release.

You can upgrade your organization to any of these version labels. Use the LimaCharlie web interface or the [API](https://api.limacharlie.io/static/swagger/#/Modules/upgradeOrg).

### Upgrading to Specific Versions

You can also upgrade your organization to a specific sensor version with a semantic version string (for example, `4.33.20`). Use a specific version when:

- You must pin your organization to a specific tested version
- You want the same version in many organizations
- You must roll back to a previous version for compatibility
- You test a specific version before a wider deployment

To upgrade or manage sensors with the API:

```bash
# Upgrade to a specific version
curl -X POST "https://api.limacharlie.io/v1/modules/{oid}?specific_version=4.33.20" \
  -H "Authorization: Bearer {api_key}" \
  -H "Content-Type: application/json"

# Upgrade to latest version label
curl -X POST "https://api.limacharlie.io/v1/modules/{oid}?specific_version=latest" \
  -H "Authorization: Bearer {api_key}" \
  -H "Content-Type: application/json"

# Downgrade to previous version (rollback)
curl -X POST "https://api.limacharlie.io/v1/modules/{oid}?is_fallback=true" \
  -H "Authorization: Bearer {api_key}" \
  -H "Content-Type: application/json"

# Move sensors to dormant mode
curl -X POST "https://api.limacharlie.io/v1/modules/{oid}?is_sleep=true" \
  -H "Authorization: Bearer {api_key}" \
  -H "Content-Type: application/json"
```

**Note**: Specific version strings use the semantic versioning format (MAJOR.MINOR.PATCH). The string must match an available LimaCharlie sensor release. If you give an invalid or unavailable version, the API returns an error.

## Managing Versioning for Sensors

To manage the versions of sensors, use LimaCharlie's **System** Tags:

- `lc:latest`: Tags the Sensor to receive the most recent version.

  - Use this tag mainly to test the `latest` sensor version on a small set of representative sensors, before you upgrade the full org to `latest`.
- `lc:stable`: Tags the sensor to receive a stable version.
- `lc:experimental`: Tags the sensor to receive the experimental version.

Apply these tags to individual sensors to change the version behavior. The updates take effect in 10 minutes or less. You can also stage deployments with these tags, and test updates on a small group of sensors before an organization-wide rollout.

## Updating Endpoint Agents

### Best Practices

To deploy a new sensor version, use a controlled test:

1. Apply the `lc:latest` tag to a small set of representative systems. Include different operating systems and workloads.
2. Monitor these test systems for a period of time. Evaluate stability, performance, and the quality of the telemetry.
3. If the test is successful, update the sensor version at the organization level.
4. Remove the `lc:latest` tag from the test systems.
5. Keep a rollback plan, and monitor the health of the systems during the deployment.

Use the `lc:latest` sensor tag mainly for upgrade tests, because it updates sensors to each new version automatically at its release.

### Manual Update

To start an update for all endpoint agents in your organization, click a button in the web interface. The action updates the over-the-air component of the sensors in 20 minutes or less. You do not download the installers again, because the installer does not change.

### Auto-Update

To automate updates, apply the `lc:stable` tag to your sensors. The sensors then update to the latest stable version automatically at its release.

### Staged Deployment

To test new versions, tag specific sensors with `lc:latest`. These sensors run the latest version, and the rest of your organization does not change. You can test new releases on selected hosts before a full rollout.
