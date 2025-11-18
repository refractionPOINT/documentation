# LimaCharlie Reporting Framework - Changelog

## [Unreleased] - 2025-11-17

### Added - Collapsible Tables Pattern

#### New Features
- **Collapsible tables**: Tables with >10 rows now automatically become collapsible in HTML reports
- **Reusable macros**: Created `jinja2/html/macros.j2` with reusable UI components
- **Documentation**: Added `COLLAPSIBLE_PATTERN.md` explaining the pattern and best practices

#### Implementation Details

**Pattern:**
- Tables automatically collapse when they have more than 10 items
- Start in "collapsed" state to keep reports clean and scannable
- Native HTML5 `<details>` element (no JavaScript required)
- Visual feedback with color changes on expand/collapse
- Print-friendly and accessible

**Files Modified:**
1. `jinja2/html/incident_investigation.j2`
   - Added collapsible CSS styles
   - Made detection details table collapsible when >10 detections
   - Tested with 1,136 detections - works perfectly

2. `jinja2/html/security_detections.j2`
   - Added collapsible CSS styles
   - Made high severity detections table collapsible when >10 detections

**Files Created:**
1. `jinja2/html/macros.j2` (280 lines)
   - `collapsible_table()` macro - for table-specific collapsing
   - `collapsible_section()` macro - for any content type
   - `severity_badge()` macro - standardized severity badges
   - `status_badge()` macro - online/offline, enabled/disabled badges
   - `kpi_card()` macro - consistent KPI cards
   - `collapsible_styles()` macro - CSS includes

2. `COLLAPSIBLE_PATTERN.md`
   - Pattern documentation
   - Usage examples
   - Implementation checklist
   - Best practices
   - Future enhancement ideas

#### Benefits

**User Experience:**
- Improved page load performance with large datasets
- Less overwhelming for users viewing long reports
- Easy to scan section headers and expand as needed
- Native HTML elements work with screen readers

**Developer Experience:**
- Reusable macros reduce code duplication
- Consistent UI patterns across all reports
- Easy to implement: just add threshold check
- No JavaScript dependencies

#### Testing

Tested with real data:
- ✅ Incident investigation report with 1,136 detections
- ✅ Collapsible section appears correctly
- ✅ Starts in expanded state
- ✅ Click to collapse/expand works
- ✅ Visual styling changes on expand/collapse

#### Next Steps

Apply pattern to remaining reports:
- [ ] Config Audit report (configuration items)
- [ ] Sensor Status report (sensor list)
- [ ] Rule Coverage report (rules list)
- [ ] Multi-tenant Billing report (tenant list)

---

## Previous Changes

See `STATE.md` for full development history including:
- 8 report types implemented
- Utility framework built (1,065 lines)
- 4 bugs fixed (Insight add-on, detection limits, chart data, billing costs)
- All reports generated in HTML, Markdown, and JSON formats
