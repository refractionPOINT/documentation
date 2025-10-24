# GCP Security Monitoring with LimaCharlie

Complete guide for implementing Google Cloud Platform security monitoring using LimaCharlie adapters, detection rules, and best practices.

## Overview

LimaCharlie provides comprehensive GCP security monitoring through:
- Cloud Pub/Sub integration for Cloud Logging
- Cloud Audit Logs analysis
- Custom threat detection
- Automated response actions
- Flexible log filtering and routing

## GCP Data Sources

### 1. Google Cloud Pub/Sub

Primary method for ingesting GCP Cloud Logging data, supporting:
- Cloud Audit Logs (Admin Activity, Data Access, System Events)
- VPC Flow Logs
- Firewall logs
- DNS logs
- Cloud Load Balancing logs
- Custom application logs

**Platform**: `gcp`

#### Pub/Sub Configuration

**CLI Command**:
```bash
./lc_adapter pubsub \
  client_options.identity.installation_key=<INSTALLATION_KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=gcp \
  sub_name=<SUBSCRIPTION_NAME> \
  project_name=<GCP_PROJECT> \
  client_options.sensor_seed_key=gcplogs
```

**IaC Configuration**:
```yaml
sensor_type: "pubsub"
pubsub:
  sub_name: "your-pubsub-subscription-name"
  project_name: "your-gcp-project-id"
  service_account_creds: "hive://secret/gcp-pubsub-service-account"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_PUBSUB"
    platform: "gcp"
    sensor_seed_key: "gcp-pubsub-sensor"
    mapping:
      sensor_hostname_path: "attributes.hostname"
      event_type_path: "attributes.eventType"
      event_time_path: "publishTime"
```

**When to Use**:
- Real-time log streaming required
- Scalable high-volume ingestion
- Native GCP integration
- Multiple log sources to consolidate

### 2. Cloud Audit Logs

Cloud Audit Logs record administrative activities and data access across GCP services.

**Log Types**:

1. **Admin Activity Logs** (always enabled, no cost):
   - Configuration changes
   - Resource creation/deletion
   - Access grants
   - API calls that modify resources

2. **Data Access Logs** (configurable, additional cost):
   - Read operations on resources
   - Metadata access
   - Data queries
   - Object storage access

3. **System Event Logs** (always enabled, no cost):
   - System-initiated actions
   - Maintenance events
   - Automatic scaling
   - Instance lifecycle events

4. **Policy Denied Logs** (always enabled, no cost):
   - Denied API calls
   - Permission failures
   - Policy violations

**What You Can Monitor**:
- IAM policy changes
- Service account operations
- Compute instance lifecycle
- Storage bucket permissions
- Firewall rule modifications
- VPC network changes
- Cloud SQL operations
- GKE cluster changes
- BigQuery access
- Cloud Functions deployment

## Setting Up GCP Log Ingestion

### Step 1: Create a Log Sink

**Via GCP Console**:
1. Navigate to **Logging > Logs Router** in GCP Console
2. Click **Create Sink**
3. Sink name: "limacharlie-audit-logs"
4. Select sink service: **Cloud Pub/Sub topic**
5. Select or create topic: "limacharlie-logs"
6. Define inclusion filter (see examples below)

**Via gcloud CLI**:
```bash
# Create topic first
gcloud pubsub topics create limacharlie-logs --project=YOUR_PROJECT

# Create log sink
gcloud logging sinks create limacharlie-audit-logs \
  pubsub.googleapis.com/projects/YOUR_PROJECT/topics/limacharlie-logs \
  --log-filter='logName:cloudaudit.googleapis.com' \
  --project=YOUR_PROJECT
```

**Recommended Inclusion Filter** (Security-focused):
```
logName:cloudaudit.googleapis.com
protoPayload.serviceName!="k8s.io"
protoPayload.serviceName!="compute.googleapis.com"
```

**Comprehensive Filter** (All audit logs):
```
logName:cloudaudit.googleapis.com
```

**Exclude Noisy Services** (Reduce volume):
```
logName:cloudaudit.googleapis.com
protoPayload.serviceName!="k8s.io"
protoPayload.serviceName!="compute.googleapis.com"
protoPayload.serviceName!="container.googleapis.com"
-protoPayload.methodName:"storage.objects.get"
-protoPayload.methodName:"storage.objects.list"
```

**Critical Operations Only** (Minimize cost):
```
logName:cloudaudit.googleapis.com AND (
  protoPayload.methodName:"SetIamPolicy" OR
  protoPayload.methodName:"CreateServiceAccountKey" OR
  protoPayload.methodName:"DeleteServiceAccountKey" OR
  protoPayload.methodName:"setIamPermissions" OR
  protoPayload.methodName:("v1.compute.firewalls.*") OR
  protoPayload.methodName:("v1.compute.instances.insert") OR
  protoPayload.methodName:("v1.compute.instances.delete")
)
```

### Step 2: Create Subscription

**Via GCP Console**:
1. Navigate to **Pub/Sub > Topics**
2. Select your topic: "limacharlie-logs"
3. Click **Create Subscription**
4. Subscription ID: "limacharlie-logs-sub"
5. Delivery type: Pull
6. Acknowledgment deadline: 60 seconds
7. Message retention: 7 days
8. Expiration period: Never expire

**Via gcloud CLI**:
```bash
gcloud pubsub subscriptions create limacharlie-logs-sub \
  --topic=limacharlie-logs \
  --ack-deadline=60 \
  --message-retention-duration=7d \
  --project=YOUR_PROJECT
```

### Step 3: Create Service Account

**Via GCP Console**:
1. Navigate to **IAM & Admin > Service Accounts**
2. Click **Create Service Account**
3. Name: "limacharlie-pubsub-reader"
4. Description: "LimaCharlie Pub/Sub log ingestion"
5. Grant role: **Pub/Sub Subscriber**
6. Click **Done**

**Create JSON Key**:
1. Click on created service account
2. Keys tab
3. Add Key > Create new key
4. Key type: JSON
5. Download and store securely

**Via gcloud CLI**:
```bash
# Create service account
gcloud iam service-accounts create limacharlie-pubsub-reader \
  --display-name="LimaCharlie Pub/Sub Reader" \
  --project=YOUR_PROJECT

# Grant Pub/Sub Subscriber role
gcloud pubsub subscriptions add-iam-policy-binding limacharlie-logs-sub \
  --member="serviceAccount:limacharlie-pubsub-reader@YOUR_PROJECT.iam.gserviceaccount.com" \
  --role="roles/pubsub.subscriber" \
  --project=YOUR_PROJECT

# Create and download key
gcloud iam service-accounts keys create limacharlie-key.json \
  --iam-account=limacharlie-pubsub-reader@YOUR_PROJECT.iam.gserviceaccount.com \
  --project=YOUR_PROJECT
```

**Minimum Required Permissions**:
- `pubsub.subscriptions.consume`
- `pubsub.subscriptions.get`

### Step 4: Deploy Adapter

**Option A: Using Service Account Credentials**

Best for running adapter outside GCP:
```bash
# Download adapter
curl -L https://downloads.limacharlie.io/adapter/linux/64 -o lc_adapter
chmod +x lc_adapter

# Run adapter
./lc_adapter pubsub \
  client_options.identity.installation_key=<YOUR_INSTALLATION_KEY> \
  client_options.identity.oid=<YOUR_OID> \
  client_options.platform=gcp \
  sub_name=limacharlie-logs-sub \
  project_name=YOUR_PROJECT \
  service_account_creds='<JSON_CREDENTIALS>' \
  client_options.sensor_seed_key=gcplogs-production
```

**Using Hive Secrets**:
```bash
./lc_adapter pubsub \
  client_options.identity.installation_key=<YOUR_INSTALLATION_KEY> \
  client_options.identity.oid=<YOUR_OID> \
  client_options.platform=gcp \
  sub_name=limacharlie-logs-sub \
  project_name=YOUR_PROJECT \
  service_account_creds=hive://secret/gcp-service-account-json \
  client_options.sensor_seed_key=gcplogs-production
```

**Option B: Using Default GCP Credentials**

Best for running adapter on GCE instance with attached service account:
```bash
# Run on GCE instance
./lc_adapter pubsub \
  client_options.identity.installation_key=<YOUR_INSTALLATION_KEY> \
  client_options.identity.oid=<YOUR_OID> \
  client_options.platform=gcp \
  sub_name=limacharlie-logs-sub \
  project_name=YOUR_PROJECT \
  client_options.sensor_seed_key=gcplogs-production
```

**GCE Instance Setup**:
1. Create Compute Engine instance
2. Attach service account with Pub/Sub Subscriber role
3. SSH to instance
4. Install and run adapter
5. (Optional) Configure as systemd service for auto-restart

### Step 5: Run as Service (Recommended for Production)

**Create systemd service file**:
```bash
sudo nano /etc/systemd/system/lc-gcp-adapter.service
```

**Service file content**:
```ini
[Unit]
Description=LimaCharlie GCP Pub/Sub Adapter
After=network.target

[Service]
Type=simple
User=limacharlie
WorkingDirectory=/opt/limacharlie
ExecStart=/opt/limacharlie/lc_adapter pubsub \
  client_options.identity.installation_key=<KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=gcp \
  sub_name=limacharlie-logs-sub \
  project_name=YOUR_PROJECT \
  service_account_creds=/opt/limacharlie/gcp-creds.json \
  client_options.sensor_seed_key=gcplogs-production
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable lc-gcp-adapter
sudo systemctl start lc-gcp-adapter
sudo systemctl status lc-gcp-adapter
```

## GCP Detection Rules

### Detect IAM Policy Changes

**Threat**: IAM policy changes can grant unauthorized access, escalate privileges, or establish persistence.

```yaml
# Detection
event: google.iam.admin.v1.SetIamPolicy
op: exists
path: event/protoPayload/methodName

# Response
- action: report
  name: GCP IAM Policy Modified
  metadata:
    resource: "{{ .event.protoPayload.resourceName }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

**Enhanced with Resource Type**:
```yaml
# Detection
event: google.iam.admin.v1.SetIamPolicy
op: and
rules:
  - op: exists
    path: event/protoPayload/methodName
  - op: or
    rules:
      - op: contains
        path: event/protoPayload/resourceName
        value: projects/
      - op: contains
        path: event/protoPayload/resourceName
        value: organizations/

# Response
- action: report
  name: GCP Project/Org IAM Policy Modified
  metadata:
    severity: high
    resource: "{{ .event.protoPayload.resourceName }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

### Detect GCS Bucket Permission Changes

**Threat**: Public bucket exposure can lead to data leaks and compliance violations.

```yaml
# Detection
event: storage.setIamPermissions
op: and
rules:
  - op: is
    path: event/protoPayload/serviceName
    value: storage.googleapis.com
  - op: contains
    path: event/protoPayload/methodName
    value: setIamPermissions

# Response
- action: report
  name: GCS Bucket Permissions Changed
  metadata:
    bucket: "{{ .event.protoPayload.resourceName }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

**Detect Public Bucket Exposure**:
```yaml
# Detection
event: storage.setIamPermissions
op: and
rules:
  - op: is
    path: event/protoPayload/serviceName
    value: storage.googleapis.com
  - op: or
    rules:
      - op: contains
        path: event/protoPayload/request
        value: allUsers
      - op: contains
        path: event/protoPayload/request
        value: allAuthenticatedUsers

# Response
- action: report
  name: GCS Bucket Made Public
  metadata:
    severity: critical
    bucket: "{{ .event.protoPayload.resourceName }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

### Detect Compute Instance Created

**Threat**: Unauthorized instance creation can indicate compromise, cryptojacking, or resource abuse.

```yaml
# Detection
event: v1.compute.instances.insert
op: is
path: event/protoPayload/methodName
value: v1.compute.instances.insert

# Response
- action: report
  name: GCP Compute Instance Created
  metadata:
    instance: "{{ .event.protoPayload.resourceName }}"
    zone: "{{ .event.resource.labels.zone }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

**Detect High-Cost Instance Types**:
```yaml
# Detection
event: v1.compute.instances.insert
op: and
rules:
  - op: is
    path: event/protoPayload/methodName
    value: v1.compute.instances.insert
  - op: or
    rules:
      - op: contains
        path: event/protoPayload/request/machineType
        value: n1-highmem
      - op: contains
        path: event/protoPayload/request/machineType
        value: n1-highcpu
      - op: contains
        path: event/protoPayload/request/machineType
        value: a2-
      - op: contains
        path: event/protoPayload/request/machineType
        value: g2-

# Response
- action: report
  name: High-Cost GCP Instance Created
  metadata:
    severity: high
    instance: "{{ .event.protoPayload.resourceName }}"
    machine_type: "{{ .event.protoPayload.request.machineType }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

### Detect Firewall Rule Changes

**Threat**: Firewall changes can expose services to internet or enable lateral movement.

```yaml
# Detection
op: or
rules:
  - event: v1.compute.firewalls.insert
    op: exists
    path: event/protoPayload
  - event: v1.compute.firewalls.delete
    op: exists
    path: event/protoPayload
  - event: v1.compute.firewalls.patch
    op: exists
    path: event/protoPayload

# Response
- action: report
  name: GCP Firewall Rule Modified
  metadata:
    rule: "{{ .event.protoPayload.resourceName }}"
    action: "{{ .event.protoPayload.methodName }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

**Detect Allow-All Firewall Rules**:
```yaml
# Detection
event: v1.compute.firewalls.insert
op: and
rules:
  - op: exists
    path: event/protoPayload/request/allowed
  - op: or
    rules:
      - op: contains
        path: event/protoPayload/request/sourceRanges
        value: 0.0.0.0/0
      - op: contains
        path: event/protoPayload/request/sourceRanges
        value: ::/0

# Response
- action: report
  name: GCP Firewall Rule Created with Internet Access
  metadata:
    severity: high
    rule: "{{ .event.protoPayload.resourceName }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

### Detect Service Account Key Creation

**Threat**: Service account keys can be exfiltrated and used for persistent access.

```yaml
# Detection
event: google.iam.admin.v1.CreateServiceAccountKey
op: is
path: event/protoPayload/methodName
value: google.iam.admin.v1.CreateServiceAccountKey

# Response
- action: report
  name: GCP Service Account Key Created
  metadata:
    account: "{{ .event.protoPayload.request.name }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

### Detect Project-Level IAM Changes

**Threat**: Project-level permissions grant broad access and are high-value targets.

```yaml
# Detection
event: SetIamPolicy
op: and
rules:
  - op: contains
    path: event/protoPayload/methodName
    value: SetIamPolicy
  - op: starts with
    path: event/protoPayload/resourceName
    value: projects/

# Response
- action: report
  name: GCP Project IAM Policy Modified
  metadata:
    severity: high
    project: "{{ .event.protoPayload.resourceName }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

### Detect VPC Network Changes

**Threat**: VPC changes can impact network isolation and security.

```yaml
# Detection
op: or
rules:
  - event: v1.compute.networks.insert
    op: exists
    path: event/protoPayload
  - event: v1.compute.networks.delete
    op: exists
    path: event/protoPayload
  - event: v1.compute.networks.patch
    op: exists
    path: event/protoPayload

# Response
- action: report
  name: GCP VPC Network Modified
  metadata:
    network: "{{ .event.protoPayload.resourceName }}"
    action: "{{ .event.protoPayload.methodName }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

### Detect Cloud SQL Instance Creation or Modification

**Threat**: Database instances contain sensitive data and require protection.

```yaml
# Detection
op: or
rules:
  - event: cloudsql.instances.create
    op: exists
    path: event/protoPayload
  - event: cloudsql.instances.update
    op: exists
    path: event/protoPayload

# Response
- action: report
  name: GCP Cloud SQL Instance Modified
  metadata:
    instance: "{{ .event.protoPayload.resourceName }}"
    operation: "{{ .event.protoPayload.methodName }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

### Detect BigQuery Dataset Permission Changes

**Threat**: BigQuery datasets often contain sensitive business data.

```yaml
# Detection
event: google.iam.v1.IAMPolicy.SetIamPolicy
op: and
rules:
  - op: is
    path: event/protoPayload/serviceName
    value: bigquery.googleapis.com
  - op: contains
    path: event/protoPayload/resourceName
    value: datasets/

# Response
- action: report
  name: BigQuery Dataset Permissions Modified
  metadata:
    dataset: "{{ .event.protoPayload.resourceName }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

### Detect GKE Cluster Creation or Deletion

**Threat**: GKE clusters are complex and can be expensive; unauthorized changes are significant.

```yaml
# Detection
op: or
rules:
  - event: io.k8s.core.v1.nodes.create
    op: exists
    path: event/protoPayload
  - event: io.k8s.core.v1.nodes.delete
    op: exists
    path: event/protoPayload

# Response
- action: report
  name: GKE Cluster Node Modified
  metadata:
    cluster: "{{ .event.resource.labels.cluster_name }}"
    location: "{{ .event.resource.labels.location }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

### Detect Cloud Function Deployment

**Threat**: Cloud Functions can be used for data exfiltration or C2.

```yaml
# Detection
op: or
rules:
  - event: google.cloud.functions.v1.CloudFunctionsService.CreateFunction
    op: exists
    path: event/protoPayload
  - event: google.cloud.functions.v1.CloudFunctionsService.UpdateFunction
    op: exists
    path: event/protoPayload

# Response
- action: report
  name: GCP Cloud Function Deployed
  metadata:
    function: "{{ .event.protoPayload.resourceName }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
```

### Detect Secret Manager Access

**Threat**: Secrets contain credentials and sensitive data.

```yaml
# Detection
event: secretmanager.googleapis.com.SecretVersion.Access
op: is
path: event/protoPayload/methodName
value: google.cloud.secretmanager.v1.SecretManagerService.AccessSecretVersion

# Response
- action: report
  name: GCP Secret Accessed
  metadata:
    secret: "{{ .event.protoPayload.resourceName }}"
    user: "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
  suppression:
    is_global: false
    keys:
      - "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
      - "{{ .event.protoPayload.resourceName }}"
    max_count: 1
    period: 3600
```

## Complete GCP Setup

### Step 1: Plan Your Log Strategy

**Determine Scope**:
- Single project vs organization-wide
- Which services to monitor
- Volume expectations
- Compliance requirements

**Cost Considerations**:
- Admin Activity Logs: Free
- System Event Logs: Free
- Policy Denied Logs: Free
- Data Access Logs: Paid (can be expensive at scale)

**Recommended Starting Point**:
- Enable Admin Activity Logs (free)
- Exclude high-volume services (Kubernetes, Compute read operations)
- Add Data Access Logs selectively for critical services

### Step 2: Configure Cloud Audit Logs

**Organization-Wide Setup**:
1. Navigate to IAM & Admin > Audit Logs
2. Select services to log
3. Configure log types:
   - Admin Read: Optional
   - Admin Write: Recommended
   - Data Read: Selective
   - Data Write: Selective

**Project-Level Setup**:
Same as above, but at project scope.

**Enable Data Access Logs for Critical Services**:
- Cloud Storage (selective buckets)
- BigQuery (high business value datasets)
- Cloud SQL (production databases)
- Secret Manager (all access)

### Step 3: Create Log Sink

See "Step 1: Create a Log Sink" above for detailed instructions.

**Recommended Filter for Security Monitoring**:
```
logName:cloudaudit.googleapis.com AND (
  protoPayload.methodName:"SetIamPolicy" OR
  protoPayload.methodName:"CreateServiceAccountKey" OR
  protoPayload.methodName:"DeleteServiceAccountKey" OR
  protoPayload.methodName:("storage.*.setIamPermissions") OR
  protoPayload.methodName:("v1.compute.firewalls.*") OR
  protoPayload.methodName:("v1.compute.instances.insert") OR
  protoPayload.methodName:("v1.compute.instances.delete") OR
  protoPayload.methodName:("cloudsql.instances.*") OR
  protoPayload.methodName:("google.cloud.secretmanager.*")
)
```

### Step 4: Create Pub/Sub Resources

See "Step 2: Create Subscription" above.

### Step 5: Create Service Account

See "Step 3: Create Service Account" above.

### Step 6: Deploy Adapter

**Deployment Options**:

1. **On-Premises / Cloud VM**:
   - Download adapter binary
   - Use service account JSON key
   - Run as systemd service

2. **GCE Instance** (Recommended):
   - Create small instance (e.g., e2-micro)
   - Attach service account
   - Use default credentials
   - Configure auto-restart

3. **Cloud Run** (Advanced):
   - Containerize adapter
   - Deploy to Cloud Run
   - Use Cloud Scheduler for keep-alive

4. **GKE** (Enterprise):
   - Deploy as Kubernetes deployment
   - Use Workload Identity
   - Configure resource limits

**Example GCE Deployment**:
```bash
# Create instance
gcloud compute instances create limacharlie-adapter \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --service-account=limacharlie-pubsub-reader@YOUR_PROJECT.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/pubsub \
  --image-family=debian-11 \
  --image-project=debian-cloud

# SSH to instance
gcloud compute ssh limacharlie-adapter --zone=us-central1-a

# Install adapter (on instance)
curl -L https://downloads.limacharlie.io/adapter/linux/64 -o lc_adapter
chmod +x lc_adapter
sudo mv lc_adapter /usr/local/bin/

# Create systemd service (see Step 5 above)
# Start service
sudo systemctl start lc-gcp-adapter
```

### Step 7: Deploy Detection Rules

Implement GCP-specific rules focusing on:
1. IAM policy changes
2. Service account key creation
3. Firewall modifications
4. GCS bucket permissions
5. Compute instance creation
6. VPC network changes
7. Project-level changes

### Step 8: Configure Outputs

Set up outputs to your SIEM, Slack, or incident response platform.

### Step 9: Validate Setup

**Check Adapter Connectivity**:
1. Navigate to Sensors in LimaCharlie
2. Verify adapter is online
3. Check last event time

**Generate Test Events**:
1. Create a test firewall rule in GCP
2. Verify event appears in LimaCharlie Timeline
3. Delete the test firewall rule

**Test Detection Rules**:
1. Create a service account key (test)
2. Verify alert generated
3. Check output delivery
4. Delete test key

### Step 10: Monitor and Tune

**Monitor Costs**:
- Check Pub/Sub metrics (messages, throughput)
- Review Cloud Logging costs
- Adjust log filters if needed

**Tune Detection Rules**:
- Review alerts for false positives
- Add suppression where appropriate
- Exclude known service accounts

## GCP Best Practices

### Critical Events to Monitor

**High Priority**:
- IAM policy modifications (project/org level)
- Service account key creation
- Firewall rule changes
- GCS bucket public access
- Compute instance creation (especially GPU/high-memory)
- VPC network modifications
- Project-level configuration changes

**Medium Priority**:
- Cloud SQL instance changes
- BigQuery dataset permissions
- Secret Manager access
- Cloud Function deployment
- GKE cluster operations
- Load balancer modifications

**Context-Dependent**:
- Compute instance start/stop
- Snapshot creation/deletion
- Image creation
- Disk attachment
- IP address allocation

### Cost Management

**Reduce Logging Costs**:
1. Start with Admin Activity only (free)
2. Add Data Access selectively
3. Exclude read-only operations
4. Filter high-volume services
5. Use log exclusions for known-safe activity

**Example Exclusion Filter**:
```
# Exclude Kubernetes read operations
resource.type="k8s_cluster"
protoPayload.methodName=~"^get"

# Exclude GCS object reads
resource.type="gcs_bucket"
protoPayload.methodName="storage.objects.get"
```

**Optimize Pub/Sub Costs**:
- Right-size subscription retention (7 days is usually enough)
- Monitor subscription backlog
- Ensure adapter is consuming messages
- Use single subscription per adapter (not multiple)

**Monitor Adapter Resource Usage**:
- Track CPU/memory on adapter host
- Scale horizontally if needed (multiple subscriptions)
- Use appropriate instance size

### Security Hygiene

**Protect Credentials**:
```yaml
# Store service account JSON in Hive
service_account_creds: "hive://secret/gcp-service-account"
```

**Principle of Least Privilege**:
- Grant only Pub/Sub Subscriber role
- Use resource-level permissions where possible
- Separate service accounts per project/function
- Audit service account usage quarterly

**Service Account Key Management**:
- Rotate keys annually
- Use Workload Identity instead of keys when possible
- Monitor key age and usage
- Delete unused keys

**Monitor the Monitors**:
```yaml
# Detect adapter disconnection
target: deployment
event: sensor_disconnected
op: is platform
name: gcp

# Response
- action: report
  name: GCP Log Adapter Disconnected
  metadata:
    severity: high
```

### Rule Tuning

**Baseline Normal Activity**:
- Identify service accounts and their actions
- Document regular admin operations
- Map CI/CD service accounts
- Track deployment patterns

**Use Suppression for Expected High Volume**:
```yaml
# Response
- action: report
  name: Compute Instance Created
  suppression:
    is_global: false
    keys:
      - "{{ .event.protoPayload.authenticationInfo.principalEmail }}"
      - "{{ .event.resource.labels.zone }}"
    max_count: 5
    period: 3600
```

**Exclude Known Automation**:
```yaml
# Detection
event: v1.compute.instances.insert
op: and
rules:
  - op: exists
    path: event/protoPayload
  - op: not in
    path: event/protoPayload/authenticationInfo/principalEmail
    values:
      - terraform@your-project.iam.gserviceaccount.com
      - jenkins@your-project.iam.gserviceaccount.com
```

### Multi-Project Strategies

**Centralized Logging (Recommended)**:
1. Create dedicated security project
2. Create organization-level log sink
3. Route all logs to central Pub/Sub topic
4. Deploy single adapter in security project
5. Benefits: Centralized monitoring, easier management, cost visibility

**Per-Project Adapters**:
1. Create log sink in each project
2. Deploy adapter per project
3. Use project-specific sensor seed keys
4. Tag sensors with project ID
5. Benefits: Project isolation, fine-grained control

**Hybrid Approach**:
1. Organization-level sink for critical logs
2. Per-project sinks for high-volume projects
3. Aggregate in LimaCharlie
4. Unified detection rules

### Organization-Level Configuration

**Create Organization Log Sink**:
```bash
gcloud logging sinks create limacharlie-org-logs \
  pubsub.googleapis.com/projects/SECURITY_PROJECT/topics/limacharlie-logs \
  --organization=YOUR_ORG_ID \
  --log-filter='logName:cloudaudit.googleapis.com' \
  --include-children
```

**Grant Permissions**:
The log sink will create a service account. Grant it Pub/Sub Publisher role:
```bash
gcloud pubsub topics add-iam-policy-binding limacharlie-logs \
  --member="serviceAccount:SERVICE_ACCOUNT_FROM_SINK" \
  --role="roles/pubsub.publisher" \
  --project=SECURITY_PROJECT
```

## GCP Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#gcp) for GCP-specific troubleshooting guidance.

## Additional Resources

- [Cloud Audit Logs Documentation](https://cloud.google.com/logging/docs/audit)
- [Cloud Pub/Sub Documentation](https://cloud.google.com/pubsub/docs)
- [Log Router Documentation](https://cloud.google.com/logging/docs/routing/overview)
- [LimaCharlie GCP Adapter Documentation](/docs/adapter-types-google-cloud-pubsub)
- [GCP IAM Best Practices](https://cloud.google.com/iam/docs/using-iam-securely)
