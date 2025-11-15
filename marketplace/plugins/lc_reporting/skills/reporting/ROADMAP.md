# LimaCharlie Reporting Skill - Development Roadmap

## Overview
This document tracks the development status of all planned report templates.

**Last Updated**: 2025-11-12
**Templates Completed**: 3 / 9 (33%)

---

## ✅ Completed Templates

### 1. Comprehensive MSSP Report
**File**: `templates/mssp_comprehensive_report.py`
**Status**: ✅ Production-ready
**Completed**: 2025-11-12

**Features**:
- Organization metadata with sensor version
- Sensor health by platform (with human-readable platform names)
- Security detection analysis (10,000 limit)
  - Detection categories with counts
  - Top triggered rules
  - Detection timeline by day
- Usage statistics over time period
- Configuration overview (rules, outputs, tags, users, API keys)
- Interactive HTML with Chart.js graphs
- Output formats: HTML, Markdown, JSON

**Key Innovations**:
- Two-pass platform naming for human-readable categories
- Proper detection rule name extraction from `source_rule` field
- Mixed data type handling (platform codes, timestamps, generators)

**Usage**:
```bash
python3 templates/mssp_comprehensive_report.py <OID> [days] [format]
# Example: 30-day HTML report
python3 templates/mssp_comprehensive_report.py 8cbe27f4-bfa1-4afb-ba19-138cd51389cd 30 html
```

---

### 2. Multi-Tenant Billing Report
**File**: `templates/multi_tenant_billing_report.py`
**Status**: ✅ Production-ready
**Completed**: 2025-11-12

**Features**:
- Cross-tenant summary dashboard
  - Total sensors across all orgs
  - Total events, data output, rule evaluations
  - Aggregated estimated monthly costs
- Organization overview table
  - Sensor count vs quota per org
  - Activity metrics per org
  - Cost comparison across tenants
- Detailed per-organization breakdown
  - Key metrics (events, output GB, evaluations)
  - Sensor utilization (active vs quota)
  - Last 7 days daily activity
  - Cost estimation with transparent formulas
- Interactive HTML with Chart.js cost visualization
- Multi-format output (HTML, Markdown, JSON)

**Key Innovations**:
- Automatic org discovery via `Manager.userAccessibleOrgs()`
- Usage-based cost estimation with transparent formulas
- Graceful handling of inactive organizations
- Date range filtering across 90-day usage history

**Cost Formula**:
```
Estimated Monthly Cost =
  (Sensor Count × $5) +           # Base sensor cost
  (Output GB × $0.20) +            # Data egress
  (Evaluations ÷ 1000 × $0.001)   # Rule evaluations
```

**Usage**:
```bash
python3 templates/multi_tenant_billing_report.py [days]
# Example: 30-day billing report across all accessible orgs
python3 templates/multi_tenant_billing_report.py 30
```

---

### 3. Sensor Health Report
**File**: `templates/sensor_health_report.py`
**Status**: ✅ Production-ready
**Completed**: 2025-11-12

**Features**:
- Executive summary with key metrics
  - Total sensors, online/offline counts
  - Overall availability percentage
  - Platform and tag counts
- Platform distribution analysis
  - Sensors by platform with human-readable names
  - Online/offline status per platform
  - Availability percentage per platform
  - Sample hostnames for each platform type
- Tag-based sensor grouping
  - Sensors per tag with status
  - Identification of untagged sensors
- Stale sensor detection
  - Offline 1-7 days
  - Offline 7-30 days
  - Offline >30 days
  - Last seen timestamps
- Sensor version distribution (top 10)
- Actionable recommendations
- Interactive HTML with stacked bar charts
- Multi-format output (HTML, Markdown, JSON)

**Key Innovations**:
- Two-pass platform naming for human-readable categories
- Automatic stale sensor categorization by offline duration
- Version distribution analysis for compliance checking
- Comprehensive tagging analysis and recommendations
- Real-time online/offline status tracking

**Usage**:
```bash
python3 templates/sensor_health_report.py <OID> [format]
# Example: HTML health report
python3 templates/sensor_health_report.py 8cbe27f4-bfa1-4afb-ba19-138cd51389cd html
```

---

## 📝 Planned Templates

### 4. Executive Summary Report
**File**: `templates/executive_summary.py`
**Status**: 📝 Basic implementation exists, needs enhancement
**Priority**: High
**Estimated Effort**: 2-3 hours

**Planned Features**:
- High-level organizational overview
- Online vs offline sensor ratio
- Detection summary (last 7/30 days)
- Top detection categories
- Usage trend highlights
- Critical alerts or issues
- Executive-friendly language and visualizations
- 1-2 page summary format

**Data Sources**:
- Organization info
- Sensor status
- Historic detections (limited to recent period)
- Usage statistics

**Target Audience**: Management, executives, non-technical stakeholders

---

### 5. Security Detections Report
**File**: `templates/security_detections.py`
**Status**: 📝 Planned
**Priority**: High
**Estimated Effort**: 4-5 hours

**Planned Features**:
- Total detections by time period
- Detections by category
- Detections by sensor (top offenders)
- Top triggered rules with context
- Trends and patterns over time
- Unresolved high-severity detections
- Detection velocity (rate of change)
- False positive indicators
- Recommended response actions

**Data Sources**:
- Historic detections via `m.getHistoricDetections()`
- D&R rules for context
- Sensor info for affected hosts

**Advanced Features**:
- Anomaly detection (unusual spike/drop patterns)
- Rule effectiveness analysis
- Detection heat map by time of day
- Correlation with deployment events

**Use Cases**:
- Security posture assessment
- Incident triage and prioritization
- Rule tuning guidance
- Threat hunting starting points

---

### 6. Configuration Audit Report
**File**: `templates/config_audit.py`
**Status**: 📝 Planned
**Priority**: Medium
**Estimated Effort**: 3-4 hours

**Planned Features**:
- D&R rules summary
  - Total rules by namespace
  - Recently modified rules
  - Disabled rules
  - Rules without tags
- Output configurations
  - Output types and destinations
  - Data routing summary
- YARA rules summary
- Tags in use and their purposes
- Installation keys (active/inactive)
- API keys (active, last used, permissions)
- Users and permissions audit
- Extension subscriptions

**Data Sources**:
- D&R rules via `m.rules()`
- Outputs via MCP tools
- YARA rules, tags, installation keys, API keys, users
- Organization info

**Use Cases**:
- Compliance audits
- Configuration documentation
- Security review
- Change tracking baseline

---

### 7. Incident Investigation Report
**File**: `templates/incident_investigation.py`
**Status**: 📝 Planned
**Priority**: Medium
**Estimated Effort**: 5-6 hours

**Planned Features**:
- Timeline of relevant events
- Affected sensors with context
- Related detections
- IOC search results
- Lateral movement analysis
- Process tree visualization
- Network connections
- File system activity
- Remediation actions taken
- Recommendations for containment

**Data Sources**:
- Historic events (requires Insight)
- Historic detections
- IOC search functionality
- Sensor info

**Input Parameters**:
- Time range
- Affected sensor(s)
- IOCs to search for
- Detection categories to focus on

**Use Cases**:
- Incident response documentation
- Post-incident analysis
- Forensic investigation
- Threat hunting campaigns

---

### 8. MITRE ATT&CK Coverage Report
**File**: `templates/mitre_coverage.py`
**Status**: 📝 Planned
**Priority**: Medium
**Estimated Effort**: 4-5 hours

**Planned Features**:
- Tactics coverage percentage
- Techniques coverage by tactic
- Coverage gaps identified
- Recommended improvements
- Rule mapping to MITRE techniques
- Heat map visualization
- Comparison to industry baseline (if available)
- Detection maturity assessment

**Data Sources**:
- MITRE coverage via `m.getMitreReport()`
- D&R rules with MITRE tags
- Detection history mapped to techniques

**Use Cases**:
- Security program assessment
- Gap analysis
- Investment justification
- Maturity modeling

---

### 9. Custom Report Framework
**Approach**: Ad-hoc, user-defined reports
**Status**: 📝 Pattern/framework to be documented
**Priority**: Low
**Estimated Effort**: 2-3 hours (documentation)

**Framework Components**:
1. Template for custom report structure
2. Data source selection guide
3. Common aggregation patterns
4. Output formatting utilities

**Process**:
1. Consult `data-catalog.yaml` for available data
2. Determine required data sources
3. Use `utils/report_helpers.py` for data collection
4. Format output as requested (HTML, Markdown, JSON, CSV)

**Use Cases**:
- One-off analysis
- Specialized compliance reports
- Customer-specific requirements
- Research and experimentation

---

## 🔧 Utility Development

### Completed Utilities

1. **utils/branding.py** ✅
   - Dynamic brand extraction from company domains
   - LimaCharlie default branding
   - Business domain detection
   - Generic email filtering

### Planned Utilities

1. **utils/report_helpers.py**
   - Common data collection functions
   - Aggregation utilities
   - Time range handling
   - Status**: 📝 Planned

2. **utils/data_collectors.py**
   - Specialized collectors for each data type
   - Caching mechanisms
   - Parallel collection support
   - **Status**: 📝 Planned

3. **utils/formatters.py**
   - HTML template rendering
   - Markdown generation
   - JSON/CSV export
   - **Status**: 📝 Planned

4. **utils/visualizations.py**
   - Chart.js integration
   - Common chart patterns
   - Interactive visualizations
   - **Status**: 📝 Planned

---

## 📊 Development Progress

| Category | Complete | Planned | Total | Progress |
|----------|----------|---------|-------|----------|
| Report Templates | 2 | 7 | 9 | 22% |
| Utilities | 1 | 4 | 5 | 20% |
| **Overall** | **3** | **11** | **14** | **21%** |

---

## 🎯 Next Steps

### Immediate Priorities (Week 1-2)
1. **Sensor Health Report** - High demand, straightforward implementation
2. **Security Detections Report** - Core security functionality
3. **Executive Summary** - Enhance existing basic implementation

### Medium-term Goals (Week 3-4)
4. **Configuration Audit Report** - Compliance and documentation
5. **MITRE ATT&CK Coverage** - Security maturity assessment

### Long-term Objectives (Month 2+)
6. **Incident Investigation Report** - Complex, requires careful design
7. **Utility Development** - Refactor common patterns into utilities
8. **Custom Report Framework** - Documentation and examples

---

## 💡 Lessons Learned

### Technical Discoveries
1. **Two-pass platform naming** - Essential for human-readable sensor categories
2. **Detection rule name extraction** - Always use `source_rule` field
3. **Multi-tenant access** - Use `Manager.userAccessibleOrgs()` for org discovery
4. **Usage stats structure** - Primary source for billing metrics (90-day history)
5. **Generator handling** - Can't use `len()`, must iterate and count

### Best Practices
1. **Pre-aggregate during collection** - More efficient than post-processing
2. **Cache sensor lists** - Avoid repeated expensive queries
3. **Graceful degradation** - Continue on errors in multi-tenant scenarios
4. **Always use `.get()` with defaults** - Handle missing data safely
5. **Test with small datasets first** - Validate before running on production data

### Performance Optimizations
1. Limit detection queries to 1000-10000 to avoid timeouts
2. Filter date ranges from 90-day usage stats
3. Use generators for large sensor lists
4. Batch organization queries in multi-tenant reports

---

## 📚 Resources

- **Skill Documentation**: `skill.md`
- **Data Catalog**: `data-catalog.yaml`
- **Template Examples**: `templates/mssp_comprehensive_report.py`, `templates/multi_tenant_billing_report.py`
- **LimaCharlie Python SDK**: https://github.com/refractionPOINT/python-limacharlie
- **LimaCharlie Docs**: https://doc.limacharlie.io/

---

**Maintained by**: Claude Code AI Agent
**Repository**: `.claude/skills/limacharlie-reporting/`
