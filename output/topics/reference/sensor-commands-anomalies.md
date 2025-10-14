# Anomalies

## hidden_module_scan

Look for hidden modules in a process's (or all) memory. Hidden modules are DLLs or dylibs loaded manually (not by the OS).

**Platforms:**

**Response Event:**
[HIDDEN_MODULE_DETECTED](/v1/docs/reference-events-responses-anomalies#hiddenmoduledetected)

**Usage:**

```
usage: hidden_module_scan [-h] pid

positional arguments:
  pid         pid of the process to scan, or "-1" for ALL processes
```