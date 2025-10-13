# AWS S3 Specific Docs: https://docs.limacharlie.io/docs/adapter-types-s3
# For cloud sensor deployment, store credentials as hive secrets:

#   access_key: "hive://secret/aws-access-key"
#   secret_key: "hive://secret/aws-secret-key"

sensor_type: "s3"
s3:
  bucket_name: "your-s3-bucket-name-for-logs"
  access_key: "hive://secret/aws-s3-access-key"
  secret_key: "hive://secret/aws-s3-secret-key"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_S3"
    hostname: "aws-s3-adapter"
    platform: "json"
    sensor_seed_key: "s3-log-processor"
    mapping:
      sensor_hostname_path: "source_host"
      event_type_path: "event_category"
      event_time_path: "timestamp"
    indexing: []
  # Optional S3-specific configuration
  prefix: "logs/application_xyz/"              # Filter by object prefix
  parallel_fetch: 5                           # Parallel downloads
  single_load: false                          # Continuous processing
```

## API Doc

See the [official documentation](https://aws.amazon.com/s3/).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Amazon Web Services

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.