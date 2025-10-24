# Azure Security Monitoring with LimaCharlie

Complete guide for implementing Azure and Microsoft 365 security monitoring using LimaCharlie adapters, detection rules, and managed rulesets.

## Overview

LimaCharlie provides comprehensive Azure security monitoring through:
- Azure Event Hub integration for Azure Monitor logs
- Microsoft Entra ID (Azure AD) monitoring
- Microsoft 365 audit logs
- Microsoft Defender integration
- Pre-built detection rules (Soteria)
- Custom threat detection

## Azure Data Sources

### 1. Azure Event Hub

Azure Event Hub is the primary method for ingesting Azure logs, supporting multiple data types.

**Supported Platforms**:
- `azure_monitor`: Azure Monitor logs
- `azure_ad`: Entra ID (formerly Azure AD) logs
- `msdefender`: Microsoft Defender events

#### Event Hub Configuration

**CLI Command**:
```bash
./lc_adapter azure_event_hub \
  client_options.identity.installation_key=<INSTALLATION_KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=azure_monitor \
  client_options.sensor_seed_key=<SENSOR_SEED_KEY> \
  client_options.hostname=<HOSTNAME> \
  "connection_string=Endpoint=sb://mynamespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=<KEY>=;EntityPath=lc-stream"
```

**IaC Configuration**:
```yaml
sensor_type: "azure_event_hub"
azure_event_hub:
  connection_string: "Endpoint=sb://your-eventhub-namespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=<KEY>;EntityPath=your-event-hub-name"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_FOR_AZURE"
    hostname: "azure-eventhub-adapter"
    platform: "azure_monitor"
    sensor_seed_key: "azure-eventhub-prod-sensor"
```

**When to Use**:
- Real-time log streaming required
- Multiple log sources to consolidate
- Native Azure integration preferred
- Scalable high-volume ingestion needed

**Azure Setup**:
1. Create Event Hub namespace
2. Create Event Hub within namespace
3. Configure Diagnostic Settings to stream logs to Event Hub
4. Create Shared Access Policy with Listen permissions
5. Use connection string with adapter

### 2. Microsoft Entra ID (Azure AD)

Monitor identity and access management events, including:
- Sign-in activity (successful and failed)
- Risky sign-ins and users
- Conditional access policy triggers
- User and group management
- Application access
- Multi-factor authentication events

**Platform**: `azure_ad`

**Setup Options**:
1. **Azure Event Hub**: Configure Event Hub connection (recommended for real-time)
2. **Entra ID API**: Direct API integration (polling-based)
3. **Webhooks**: Push-based event delivery

#### Entra ID API Setup

**Step 1: Create App Registration**
1. Navigate to Azure Portal > Entra ID > App Registrations
2. Click "New registration"
3. Name: "LimaCharlie-EntraID-Reader"
4. Supported account types: Single tenant
5. No redirect URI needed

**Step 2: Required API Permissions**

Add the following Microsoft Graph API permissions (Application type):
- `IdentityRiskEvent.Read.All`
- `IdentityRiskEvent.ReadWrite.All`
- `IdentityRiskyServicePrincipal.Read`
- `IdentityRiskyServicePrincipal.ReadWrite.All`
- `IdentityRiskyUser.Read.All`
- `IdentityRiskyUser.ReadWrite.All`
- `User.Read`
- `AuditLog.Read.All`
- `Directory.Read.All`

**Step 3: Grant Admin Consent**
- Click "Grant admin consent for [Your Tenant]"
- Confirm the consent

**Step 4: Create Client Secret**
1. Navigate to Certificates & secrets
2. New client secret
3. Description: "LimaCharlie Integration"
4. Expiration: 24 months (set reminder to rotate)
5. Copy the secret value immediately

**Step 5: Collect Configuration Values**
- Tenant ID: Overview page of Entra ID
- Client ID: Overview page of App Registration
- Client Secret: From previous step

**Step 6: Configure in LimaCharlie**
Use these values in your adapter configuration or store in Hive Secrets.

#### Entra ID via Event Hub

**CLI Command**:
```bash
./lc_adapter azure_event_hub \
  client_options.identity.installation_key=<INSTALLATION_KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=azure_ad \
  client_options.hostname=entra-id-logs \
  client_options.sensor_seed_key=entra-prod \
  "connection_string=Endpoint=sb://your-namespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=<KEY>;EntityPath=entra-logs"
```

**Azure Configuration**:
1. Navigate to Entra ID > Diagnostic settings
2. Add diagnostic setting
3. Select log categories:
   - SignInLogs
   - AuditLogs
   - RiskyUsers
   - UserRiskEvents
4. Stream to Event Hub
5. Select your Event Hub namespace and hub

### 3. Microsoft 365

Monitor Office 365 audit events across the Microsoft 365 ecosystem.

**Platform**: `office365`

**Content Types**:
- `Audit.AzureActiveDirectory`: Azure AD events
- `Audit.Exchange`: Exchange/email events
- `Audit.SharePoint`: SharePoint activity
- `Audit.General`: General M365 events
- `DLP.All`: Data Loss Prevention events

**What You Can Monitor**:
- Email access and sending
- File sharing and access
- Teams meetings and chat
- OneDrive operations
- SharePoint modifications
- Admin actions
- DLP policy matches
- Insider risk signals

#### M365 Prerequisites

1. Microsoft 365 E3/E5 or equivalent license
2. Audit logging enabled (enabled by default for E5)
3. App Registration with appropriate permissions

**Required API Permissions**:
- `ActivityFeed.Read`
- `ActivityFeed.ReadDlp`
- `ServiceHealth.Read`

#### M365 Configuration

**IaC Configuration**:
```yaml
sensor_type: "office365"
office365:
  tenant_id: "hive://secret/azure-o365-tenant-id"
  client_id: "hive://secret/azure-o365-client-id"
  client_secret: "hive://secret/azure-o365-client-secret"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_O365"
    hostname: "ms-o365-adapter"
    platform: "json"
    sensor_seed_key: "office365-audit-sensor"
    mapping:
      sensor_hostname_path: "ClientIP"
      event_type_path: "Operation"
      event_time_path: "CreationTime"
  content_types:
    - "Audit.AzureActiveDirectory"
    - "Audit.Exchange"
    - "Audit.SharePoint"
    - "Audit.General"
    - "DLP.All"
```

**Content Type Selection**:
- Start with `Audit.General` for overview
- Add `Audit.Exchange` for email monitoring
- Add `Audit.SharePoint` for file activity
- Add `DLP.All` for data loss prevention
- `Audit.AzureActiveDirectory` if not using Entra ID adapter separately

### 4. Azure Monitor Logs

Collect logs and performance data from Azure resources:
- Virtual machine logs
- Container logs
- Application Insights
- Resource diagnostic logs
- Activity logs

**Platform**: `azure_monitor`

**Ingestion Methods**:
- Azure Event Hub (recommended)
- LimaCharlie Webhooks

**Common Use Cases**:
- VM security events
- Application errors and exceptions
- Resource health events
- Metric alerts
- Custom logs

### 5. Azure Key Vault

Monitor access to cryptographic keys and secrets:
- Secret access events
- Key operations
- Certificate management
- Vault configuration changes

**Ingestion Methods**:
- Azure Event Hub
- LimaCharlie Webhooks

**Event Type**: Based on log `category` field

**Azure Configuration**:
1. Navigate to Key Vault > Diagnostic settings
2. Add diagnostic setting
3. Select log categories:
   - AuditEvent
   - AllMetrics (optional)
4. Stream to Event Hub

### 6. Microsoft Defender

Integrate Microsoft Defender for Cloud and Defender for Endpoint findings.

**Platform**: `msdefender`

**What You Get**:
- Security alerts from Defender for Cloud
- Endpoint detection and response alerts
- Vulnerability findings
- Compliance status
- Recommendations

**Setup**: Configure via Event Hub or API integration

## Azure Detection Rules

### Detect Entra ID Risky Sign-In

**Threat**: High-risk sign-ins indicate potential account compromise, credential theft, or malicious access.

```yaml
# Detection
target: artifact
op: and
rules:
  - op: is platform
    name: azure_ad
  - op: contains
    path: /riskLevel
    value: high

# Response
- action: report
  name: High-Risk Entra ID Sign-In Detected
  metadata:
    user: "{{ .artifact.userPrincipalName }}"
    risk: "{{ .artifact.riskLevel }}"
```

**Enhanced Detection with Context**:
```yaml
# Detection
target: artifact
op: and
rules:
  - op: is platform
    name: azure_ad
  - op: or
    rules:
      - op: contains
        path: /riskLevel
        value: high
      - op: contains
        path: /riskLevel
        value: medium
  - op: is
    path: /status/signInStatus
    value: 0  # Successful sign-in

# Response
- action: report
  name: Risky Sign-In Succeeded
  metadata:
    user: "{{ .artifact.userPrincipalName }}"
    risk: "{{ .artifact.riskLevel }}"
    location: "{{ .artifact.location.city }}"
    ip: "{{ .artifact.ipAddress }}"
```

### Detect Azure Resource Deletion

**Threat**: Resource deletion can indicate malicious activity, insider threat, or ransomware.

```yaml
# Detection
event: AzureActivity
op: and
rules:
  - op: contains
    path: event/operationName
    value: Delete
  - op: is
    path: event/status/value
    value: Success

# Response
- action: report
  name: Azure Resource Deleted
  metadata:
    resource: "{{ .event.resourceId }}"
    user: "{{ .event.caller }}"
```

**Critical Resource Deletion**:
```yaml
# Detection
event: AzureActivity
op: and
rules:
  - op: or
    rules:
      - op: contains
        path: event/resourceId
        value: /VIRTUALMACHINES/
      - op: contains
        path: event/resourceId
        value: /DATABASES/
      - op: contains
        path: event/resourceId
        value: /STORAGEACCOUNTS/
  - op: contains
    path: event/operationName
    value: Delete
  - op: is
    path: event/status/value
    value: Success

# Response
- action: report
  name: Critical Azure Resource Deleted
  metadata:
    severity: high
    resource: "{{ .event.resourceId }}"
    user: "{{ .event.caller }}"
    subscription: "{{ .event.subscriptionId }}"
```

### Detect Key Vault Access from Unusual Location

**Threat**: Key Vault access from unexpected IPs may indicate credential theft or unauthorized access.

```yaml
# Detection
event: AuditEvent
op: and
rules:
  - op: is platform
    name: azure_monitor
  - op: contains
    path: event/resourceId
    value: KEYVAULT
  - op: is public address
    path: event/callerIpAddress

# Response
- action: report
  name: Azure Key Vault Access from External IP
  metadata:
    ip: "{{ .event.callerIpAddress }}"
    operation: "{{ .event.operationName }}"
```

### Detect M365 File Access by Anonymous User

**Threat**: Anonymous file access indicates potential data leak or misconfigured sharing.

```yaml
# Detection
event: FileAccessed
op: contains
path: event/UserId
value: anon

# Response
- action: report
  name: OneDrive File Accessed by Anonymous User
  metadata:
    file: "{{ .event.ObjectId }}"
    user: "{{ .event.UserId }}"
```

**External Sharing Detection**:
```yaml
# Detection
event: SharingSet
op: or
rules:
  - op: contains
    path: event/TargetUserOrGroupType
    value: Guest
  - op: contains
    path: event/TargetUserOrGroupType
    value: Anonymous

# Response
- action: report
  name: File Shared with External User
  metadata:
    file: "{{ .event.ObjectId }}"
    shared_by: "{{ .event.UserId }}"
    shared_with: "{{ .event.TargetUserOrGroupName }}"
```

### Detect Admin Role Assignment in Azure AD

**Threat**: Admin role assignments can indicate privilege escalation or unauthorized access.

```yaml
# Detection
event: AzureActiveDirectory
op: and
rules:
  - op: or
    rules:
      - op: contains
        path: event/Operation
        value: Add member to role
      - op: contains
        path: event/Operation
        value: Add eligible member to role
  - op: contains
    path: event/ModifiedProperties
    value: Admin

# Response
- action: report
  name: Azure AD Admin Role Assigned
  metadata:
    target: "{{ .event.TargetUserOrGroupName }}"
    role: "{{ .event.ModifiedProperties }}"
```

**Specific High-Privilege Roles**:
```yaml
# Detection
event: AzureActiveDirectory
op: and
rules:
  - op: contains
    path: event/Operation
    value: Add member to role
  - op: or
    rules:
      - op: contains
        path: event/ModifiedProperties
        value: Global Administrator
      - op: contains
        path: event/ModifiedProperties
        value: Privileged Role Administrator
      - op: contains
        path: event/ModifiedProperties
        value: Security Administrator

# Response
- action: report
  name: High-Privilege Azure AD Role Assigned
  metadata:
    severity: critical
    target: "{{ .event.TargetUserOrGroupName }}"
    role: "{{ .event.ModifiedProperties }}"
    assigned_by: "{{ .event.Actor }}"
```

### Detect Network Security Group Modifications

**Threat**: NSG changes can expose resources to internet or enable lateral movement.

```yaml
# Detection
event: AzureActivity
op: and
rules:
  - op: contains
    path: event/resourceId
    value: NETWORKSECURITYGROUPS
  - op: or
    rules:
      - op: contains
        path: event/operationName
        value: securityRules/write
      - op: contains
        path: event/operationName
        value: securityRules/delete

# Response
- action: report
  name: Azure Network Security Group Modified
  metadata:
    nsg: "{{ .event.resourceId }}"
    operation: "{{ .event.operationName }}"
    user: "{{ .event.caller }}"
```

### Detect Conditional Access Policy Changes

**Threat**: Changes to conditional access policies can weaken security posture.

```yaml
# Detection
event: AzureActiveDirectory
op: or
rules:
  - op: contains
    path: event/Operation
    value: Add conditional access policy
  - op: contains
    path: event/Operation
    value: Update conditional access policy
  - op: contains
    path: event/Operation
    value: Delete conditional access policy

# Response
- action: report
  name: Conditional Access Policy Modified
  metadata:
    operation: "{{ .event.Operation }}"
    policy: "{{ .event.TargetResources }}"
    modified_by: "{{ .event.Actor }}"
```

### Detect Multiple Failed Sign-Ins

**Threat**: Multiple failed sign-ins indicate brute force, password spraying, or credential stuffing attacks.

```yaml
# Detection
target: artifact
op: and
rules:
  - op: is platform
    name: azure_ad
  - op: not is
    path: /status/signInStatus
    value: 0

# Response
- action: report
  name: Entra ID Sign-In Failure
  metadata:
    user: "{{ .artifact.userPrincipalName }}"
    error: "{{ .artifact.status.errorCode }}"
  suppression:
    is_global: false
    keys:
      - "{{ .artifact.userPrincipalName }}"
    max_count: 5
    period: 300
```

### Detect Impossible Travel

**Threat**: Sign-ins from geographically distant locations in short time indicate compromised credentials.

```yaml
# Detection
target: artifact
op: and
rules:
  - op: is platform
    name: azure_ad
  - op: contains
    path: /riskEventTypes
    value: impossibleTravel

# Response
- action: report
  name: Impossible Travel Detected
  metadata:
    severity: high
    user: "{{ .artifact.userPrincipalName }}"
    locations: "{{ .artifact.location }}"
```

### Detect Storage Account Public Access

**Threat**: Public storage accounts can lead to data exposure.

```yaml
# Detection
event: AzureActivity
op: and
rules:
  - op: contains
    path: event/resourceId
    value: STORAGEACCOUNTS
  - op: or
    rules:
      - op: contains
        path: event/operationName
        value: allowBlobPublicAccess/write
      - op: contains
        path: event/operationName
        value: publicNetworkAccess/write
  - op: is
    path: event/status/value
    value: Success

# Response
- action: report
  name: Storage Account Public Access Changed
  metadata:
    account: "{{ .event.resourceId }}"
    operation: "{{ .event.operationName }}"
    user: "{{ .event.caller }}"
```

### Detect Subscription-Level Changes

**Threat**: Subscription-level changes can impact entire organization security.

```yaml
# Detection
event: AzureActivity
op: and
rules:
  - op: contains
    path: event/resourceId
    value: /SUBSCRIPTIONS/
  - op: not contains
    path: event/resourceId
    value: /RESOURCEGROUPS/
  - op: contains
    path: event/operationName
    value: write

# Response
- action: report
  name: Azure Subscription Configuration Changed
  metadata:
    subscription: "{{ .event.subscriptionId }}"
    operation: "{{ .event.operationName }}"
    user: "{{ .event.caller }}"
```

## Soteria M365 Rules

Managed detection rules for Microsoft 365 environments.

**Setup**:
1. Navigate to Add-Ons > Extensions in LimaCharlie
2. Subscribe to the `soteria-rules-o365` extension
3. Subscribe to the `tor` lookup (free, required dependency)
4. Configure Office 365 Adapter

**Coverage**:
- Teams activity monitoring
- Email/Exchange threats
- SharePoint data access
- OneDrive file operations
- DLP policy violations
- Insider risk indicators
- External sharing anomalies
- Admin activity tracking

**Benefits**:
- Pre-tuned for M365 environment
- Regular updates for new threats
- Community-driven improvements
- Professional SOC-grade rules

## Complete Azure Setup

### Step 1: Create Event Hub Infrastructure

**Create Event Hub Namespace**:
1. Navigate to Azure Portal > Event Hubs
2. Click "Create"
3. Subscription: Your subscription
4. Resource group: Create "limacharlie-monitoring"
5. Namespace name: "lc-logs-namespace"
6. Location: Your preferred region
7. Pricing tier: Standard (required for multiple consumer groups)
8. Throughput units: Start with 1

**Create Event Hubs**:
Create separate Event Hubs for each data source:
1. `azure-monitor-hub`
2. `entra-id-hub`
3. `key-vault-hub`

**For each Event Hub**:
1. Navigate to namespace > Event Hubs
2. Click "Event Hub"
3. Name: As above
4. Partition count: 2 (start low, increase if needed)
5. Message retention: 1 day

### Step 2: Configure Diagnostic Settings

**Azure Activity Log**:
1. Navigate to Monitor > Activity Log
2. Export Activity Logs
3. Add diagnostic setting
4. Name: "lc-activity-export"
5. Select categories: Administrative, Security, Alert, Policy
6. Stream to an event hub
7. Event hub namespace: lc-logs-namespace
8. Event hub name: azure-monitor-hub

**Entra ID Logs**:
1. Navigate to Entra ID > Diagnostic settings
2. Add diagnostic setting
3. Name: "lc-entra-export"
4. Select categories:
   - AuditLogs
   - SignInLogs
   - RiskyUsers
   - UserRiskEvents
   - ServicePrincipalSignInLogs
5. Stream to event hub: entra-id-hub

**Key Vault Logs** (for each Key Vault):
1. Navigate to Key Vault > Diagnostic settings
2. Add diagnostic setting
3. Select: AuditEvent
4. Stream to event hub: key-vault-hub

**Resource Logs** (for VMs, databases, etc.):
1. Navigate to resource > Diagnostic settings
2. Add diagnostic setting
3. Select relevant log categories
4. Stream to event hub: azure-monitor-hub

### Step 3: Create Shared Access Policies

For each Event Hub:
1. Navigate to Event Hub (not namespace)
2. Shared access policies
3. Add policy
4. Name: "limacharlie-listen"
5. Permissions: Listen only
6. Copy connection string (primary or secondary)

### Step 4: Deploy Event Hub Adapters

**Azure Monitor Adapter**:
```bash
# Download adapter
curl -L https://downloads.limacharlie.io/adapter/linux/64 -o lc_adapter
chmod +x lc_adapter

# Run adapter
./lc_adapter azure_event_hub \
  client_options.identity.installation_key=<YOUR_INSTALLATION_KEY> \
  client_options.identity.oid=<YOUR_OID> \
  client_options.platform=azure_monitor \
  client_options.hostname=azure-monitor-production \
  client_options.sensor_seed_key=azure-mon-prod \
  "connection_string=Endpoint=sb://lc-logs-namespace.servicebus.windows.net/;SharedAccessKeyName=limacharlie-listen;SharedAccessKey=<KEY>;EntityPath=azure-monitor-hub"
```

**Entra ID Adapter**:
```bash
./lc_adapter azure_event_hub \
  client_options.identity.installation_key=<YOUR_INSTALLATION_KEY> \
  client_options.identity.oid=<YOUR_OID> \
  client_options.platform=azure_ad \
  client_options.hostname=entra-id-production \
  client_options.sensor_seed_key=entra-prod \
  "connection_string=Endpoint=sb://lc-logs-namespace.servicebus.windows.net/;SharedAccessKeyName=limacharlie-listen;SharedAccessKey=<KEY>;EntityPath=entra-id-hub"
```

**Using Hive Secrets**:
```bash
./lc_adapter azure_event_hub \
  client_options.identity.installation_key=<YOUR_INSTALLATION_KEY> \
  client_options.identity.oid=<YOUR_OID> \
  client_options.platform=azure_monitor \
  client_options.hostname=azure-monitor-production \
  client_options.sensor_seed_key=azure-mon-prod \
  "connection_string=hive://secret/azure-eventhub-connection-string"
```

### Step 5: Configure M365 Adapter

**Create App Registration**:
1. Navigate to Entra ID > App Registrations
2. New registration
3. Name: "LimaCharlie-M365-Audit"
4. Supported account types: Single tenant

**Configure API Permissions**:
1. Add permission > Office 365 Management APIs
2. Application permissions:
   - ActivityFeed.Read
   - ActivityFeed.ReadDlp
   - ServiceHealth.Read
3. Grant admin consent

**Create Client Secret**:
1. Certificates & secrets
2. New client secret
3. Copy value immediately

**Configure in LimaCharlie Web UI**:
1. Navigate to Sensors > Add Sensor
2. Select Office 365
3. Enter:
   - Tenant ID
   - Client ID
   - Client Secret
4. Select content types
5. Deploy

### Step 6: Subscribe to Soteria Rules

1. Navigate to Add-Ons > Extensions
2. Subscribe to `soteria-rules-o365`
3. Subscribe to `tor` lookup

### Step 7: Deploy Detection Rules

Implement Azure-specific rules focusing on:
1. Entra ID risky sign-ins
2. Admin role assignments
3. Resource deletions
4. Key Vault access
5. M365 anonymous access
6. NSG modifications
7. Conditional access changes

### Step 8: Configure Outputs

Set up outputs to your SIEM, Slack, or incident response platform.

### Step 9: Validate Setup

**Check Adapter Connectivity**:
1. Navigate to Sensors in LimaCharlie
2. Verify all adapters are online
3. Check last event time

**Generate Test Events**:
1. Sign in to Azure Portal
2. View Activity Log in LimaCharlie Timeline
3. Create/delete a test resource
4. Verify event appears

**Test Detection Rules**:
1. Trigger known detection
2. Verify alert generated
3. Check output delivery

## Azure Best Practices

### Critical Events to Monitor

**High Priority**:
- Entra ID risky sign-ins
- Admin role assignments
- Resource deletions
- Key Vault access
- Network security group changes
- Subscription-level changes
- Conditional access policy modifications
- Storage account public access

**Medium Priority**:
- VM operations
- Database configuration changes
- Application Gateway changes
- Load balancer modifications
- DNS zone changes
- Virtual network changes

**Context-Dependent**:
- Service principal changes
- Managed identity operations
- Policy assignments
- Blueprint deployments

### Cost Management

**Event Hub Costs**:
- Start with Standard tier, 1 throughput unit
- Monitor ingress metrics
- Scale up only if needed
- Use separate hubs for different sources to identify high-volume sources

**Diagnostic Settings**:
- Be selective with log categories
- Exclude verbose categories if not needed
- Use sampling for high-volume resources
- Archive old logs to storage instead

**M365 Audit**:
- Start with essential content types
- Add DLP.All only if using DLP
- Monitor API call consumption
- Use appropriate polling intervals

### Security Hygiene

**Protect Credentials**:
```yaml
# Use Hive Secrets for all credentials
connection_string: "hive://secret/azure-eventhub-connection"
client_secret: "hive://secret/m365-client-secret"
```

**Principle of Least Privilege**:
- Event Hub: Listen permission only
- Entra ID App: Only required API permissions
- M365 App: Read-only permissions
- Service Principal: Reader role on monitored resources

**Credential Rotation**:
- Rotate client secrets every 6-12 months
- Set calendar reminders before expiration
- Use multiple secrets for zero-downtime rotation
- Audit app registrations quarterly

**Monitor the Monitors**:
```yaml
# Detect adapter disconnection
target: deployment
event: sensor_disconnected
op: or
rules:
  - op: is platform
    name: azure_monitor
  - op: is platform
    name: azure_ad
  - op: is platform
    name: office365

# Response
- action: report
  name: Azure Adapter Disconnected
  metadata:
    severity: high
```

### Rule Tuning

**Baseline Normal Activity**:
- Identify service principals and their actions
- Document regular admin operations
- Map business hours for context
- Track seasonal patterns (e.g., fiscal year-end changes)

**Use Suppression for High-Volume Events**:
```yaml
# Response
- action: report
  name: Azure Resource Read Operation
  suppression:
    is_global: false
    keys:
      - "{{ .event.caller }}"
      - "{{ .event.resourceId }}"
    max_count: 1
    period: 3600
```

**Add Temporal Context**:
```yaml
# Alert on after-hours admin activity
event: AzureActiveDirectory
op: and
rules:
  - op: contains
    path: event/Operation
    value: Admin
  - op: not in time window
    days:
      - monday
      - tuesday
      - wednesday
      - thursday
      - friday
    start: 08:00
    end: 18:00
    timezone: America/New_York
```

### Multi-Subscription Strategies

**Centralized Monitoring**:
1. Create dedicated monitoring subscription
2. Create Event Hub namespace in monitoring subscription
3. Grant cross-subscription permissions
4. Configure diagnostic settings in each subscription to central Event Hub
5. Deploy adapters in monitoring subscription

**Per-Subscription Adapters**:
1. Deploy Event Hub in each subscription
2. Local diagnostic settings
3. Subscription-specific adapters
4. Tag sensors with subscription ID
5. Centralized detection rules

**Hybrid Approach**:
1. Central Event Hub for critical subscriptions
2. Per-subscription for high-volume environments
3. Aggregate in LimaCharlie
4. Unified detection and response

## Azure Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#azure) for Azure-specific troubleshooting guidance.

## Additional Resources

- [Azure Monitor Documentation](https://docs.microsoft.com/azure/azure-monitor/)
- [Microsoft Entra ID Documentation](https://docs.microsoft.com/azure/active-directory/)
- [Microsoft 365 Audit Documentation](https://docs.microsoft.com/microsoft-365/compliance/search-the-audit-log)
- [LimaCharlie Azure Adapter Documentation](/docs/adapter-types-azure-event-hub)
- [Soteria M365 Rules Documentation](/docs/soteria-m365-rules)
