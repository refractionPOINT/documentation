# Config Hive

The Config Hive is LimaCharlie's hierarchical configuration store. It provides a centralized way to manage configurations that can be referenced across the platform.

## Hive Types

- [D&R Rules](dr-rules.md) - Detection and response rule storage
- [Lookups](lookups.md) - Key-value lookup tables for enrichment
- [Secrets](secrets.md) - Secure credential management
- [YARA](yara.md) - YARA rule storage and management
- [Cloud Sensors](cloud-sensors.md) - Cloud sensor configurations
- [Investigation](investigation.md) - Investigation data storage

## Usage

Hive records can be:

- Referenced in D&R rules using the `hive://` prefix
- Managed via the web interface, CLI, or API
- Version controlled using the Git Sync extension

---

## See Also

- [D&R Rules](dr-rules.md)
- [Secrets Manager](secrets.md)
- [Lookups](lookups.md)
