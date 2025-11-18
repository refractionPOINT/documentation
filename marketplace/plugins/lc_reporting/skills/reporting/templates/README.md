# LimaCharlie Reporting Framework

A comprehensive, reusable framework for creating custom LimaCharlie security reports.

## Quick Links

- **[Quick Start Guide](QUICK_START.md)** - Get started in 30 seconds
- **[Custom Reports Guide](CUSTOM_REPORTS_GUIDE.md)** - Complete guide with examples
- **[Framework Summary](FRAMEWORK_SUMMARY.md)** - Architecture and metrics

## What's Included

### ✅ Core Utilities (`utils/`)

- **`data_collectors.py`** - LimaCharlie SDK data collection (detections, sensors, rules)
- **`report_helpers.py`** - Time parsing, aggregation, filtering utilities
- **`formatters.py`** - Multi-format rendering (HTML, Markdown, JSON)
- **`base_report.py`** - Base classes for standardized reports

**Total: 1,065 lines of reusable code**

### ✅ Example Reports

- **`incident_investigation_v2.py`** - Production example using framework (228 lines)
- **`examples/simple_threat_report.py`** - Minimal custom report example

### ✅ Documentation

- **`README.md`** - This file
- **`QUICK_START.md`** - 30-second quick start
- **`CUSTOM_REPORTS_GUIDE.md`** - Complete usage guide
- **`FRAMEWORK_SUMMARY.md`** - Framework overview and metrics

## Installation

No installation needed! Just use the utilities.

## Framework Benefits

- **44% less code** per report
- **Reusable utilities** for common tasks  
- **Standard patterns** to follow
- **Multiple output formats** (HTML, Markdown, JSON)

See **[FRAMEWORK_SUMMARY.md](FRAMEWORK_SUMMARY.md)** for complete details.
