# AWS SQS Specific Docs: https://docs.limacharlie.io/docs/adapter-types-sqs

sensor_type: "sqs"
sqs:
  queue_url: "https://sqs.us-east-1.amazonaws.com/123456789012/your-security-logs-queue"
  aws_access_key_id: "hive://secret/aws-access-key-id"
  aws_secret_access_key: "hive://secret/aws-secret-access-key"
  aws_region: "us-east-1"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_SQS"
    platform: "json"
    sensor_seed_key: "aws-sqs-sensor"
    mapping:
      sensor_hostname_path: "source.instance_id"
      event_type_path: "detail.eventName"
      event_time_path: "time"
    indexing: []
  # Optional SQS-specific configuration
  max_messages: 10                       # Default: 10 (max messages per poll)
  wait_time_seconds: 20                  # Default: 20 (long polling)
  visibility_timeout: 300                # Default: 300 seconds
  delete_after_processing: true          # Default: true
```

## API Doc

See the [official documentation](https://aws.amazon.com/sqs/).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Amazon Web Services

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.