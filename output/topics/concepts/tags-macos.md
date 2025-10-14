# macOS

This topic covers macOS-related functionality in LimaCharlie, including agent installation, configuration, event ingestion, and management.

## Overview

LimaCharlie provides comprehensive endpoint detection and response (EDR) capabilities for macOS systems through its endpoint agent. The agent supports various macOS versions and can be deployed through multiple methods including MDM solutions like Jamf Now.

## macOS Agent Installation

### Latest Versions (macOS 15 Sequoia and newer)

For macOS 15 Sequoia and later versions, the installation process has been updated to accommodate Apple's enhanced security requirements. These newer versions require specific configuration and permissions to enable full EDR capabilities.

**Last Updated:** 11 Jul 2025

Refer to: [macOS Agent Installation - Latest Versions](/docs/en/clone-macos-agent-installation-latest-versions-macos-15-sequoia-and-newer)

### Older Versions (macOS 10.15 Catalina to macOS 14 Sonoma)

Installation for macOS versions from 10.15 Catalina through macOS 14 Sonoma follows a different process than the latest versions. These versions have established security requirements that are well-documented and supported.

**Last Updated:** 11 Jul 2025

Refer to: [macOS Agent Installation - Older Versions (10.15-14)](/docs/en/macos-agent-installation-latest-os-versions)

### Older Versions (macOS 10.14 and prior)

Legacy macOS versions (10.14 Mojave and earlier) require specific installation procedures due to differences in security frameworks and system architecture.

**Last Updated:** 10 Dec 2024

Refer to: [macOS Agent Installation - Older Versions (10.14 and prior)](/docs/en/macos-agent-installation-older-versions)

### MDM Configuration Profiles

LimaCharlie agents can be deployed and configured using Mobile Device Management (MDM) configuration profiles. This approach is particularly useful for enterprise deployments where centralized management is required.

**Last Updated:** 16 Mar 2025

Refer to: [macOS Agent Installation - MDM Configuration Profiles](/docs/en/macos-agent-installation-mdm-configuration-profiles)

### Installation via Jamf Now

Jamf Now is a popular MDM solution for macOS devices. LimaCharlie provides specific guidance for deploying agents through Jamf Now.

**Last Updated:** 01 Nov 2024

Refer to: [macOS Agent Installation via Jamf Now](/docs/en/installing-macos-agents-via-jamf-now)

### General Installation Guide

For general installation information applicable across macOS versions:

**Last Updated:** 01 Nov 2024, 07 Jul 2025

Refer to:
- [macOS Agent Installation](/docs/en/macos-agent-installation)
- [Endpoint Agent Installation](/docs/en/endpoint-agent-installation)

## Ingesting MacOS Unified Logs

macOS uses a unified logging system that consolidates system and application logs. LimaCharlie can ingest these logs for analysis and correlation with EDR events.

**Last Updated:** 07 Oct 2025

Refer to:
- [Ingesting MacOS Unified Logs](/docs/en/ingesting-macos-unified-logs)
- [Mac Unified Logging Adapter](/docs/en/adapter-types-mac-unified-logging) (16 Jul 2025)

## Endpoint Agent Management

### Agent Commands

The LimaCharlie endpoint agent supports various commands for tasking, configuration, and investigation on macOS systems.

**Last Updated:** 07 Aug 2025, 18 Apr 2025

Refer to:
- [Reference: Endpoint Agent Commands](/docs/en/reference-endpoint-agent-commands)
- [Endpoint Agent Commands](/docs/en/endpoint-agent-commands)

### Agent Uninstallation

Proper uninstallation procedures ensure complete removal of the agent and its components from macOS systems.

**Last Updated:** 05 Oct 2024

Refer to: [Endpoint Agent Uninstallation](/docs/en/endpoint-agent-uninstallation)

### Endpoint Agent Overview

General information about the LimaCharlie endpoint agent architecture and capabilities.

**Last Updated:** 01 Nov 2024

Refer to: [Endpoint Agent](/docs/en/endpoint-agent)

## Events and Telemetry

### EDR Events

The macOS agent generates comprehensive telemetry events covering process execution, network activity, file operations, and more.

**Last Updated:** 22 Sep 2025

Refer to:
- [Reference: EDR Events](/docs/en/reference-edr-events)
- [Endpoint Agent Events Overview](/docs/en/endpoint-agent-events-overview) (10 Dec 2024)

### Payloads

Payloads represent the data structures and event formats used by the agent when reporting telemetry.

**Last Updated:** 05 Oct 2024

Refer to: [Payloads](/docs/en/payloads)

## Related Articles

The following articles contain macOS-specific information or cross-platform guidance applicable to macOS:

* Ingesting MacOS Unified Logs
* Reference: EDR Events
* Reference: Endpoint Agent Commands
* Mac Unified Logging
* macOS Agent Installation - Latest Versions (macOS 15 Sequoia and newer)
* macOS Agent Installation - Older Versions (macOS 10.15 Catalina to macOS 14 Sonoma)
* macOS Agent Installation - MDM Configuration Profiles
* macOS Agent Installation - Older Versions (macOS 10.14 and prior)
* macOS Agent Installation via Jamf Now
* Payloads
* Endpoint Agent Uninstallation
* Endpoint Agent Installation
* macOS Agent Installation
* Endpoint Agent Commands
* Endpoint Agent
* Endpoint Agent Events Overview