# Billing Reporter Examples

This document provides detailed examples of common billing investigation workflows with real data and step-by-step analysis.

---

## Common Investigation Workflows

### Workflow 1: "Why is my bill higher this month?"

**Steps**:
1. Get current usage stats for the organization
2. Compare key metrics:
   - Sensor count (online vs quota)
   - Output data volume
   - Event volume processed
   - Query usage
   - New extensions added
3. Identify the largest increase
4. Investigate the specific area
5. Suggest optimizations

**Example Analysis**:
"Your output data increased from 50GB to 200GB this month. I see you're forwarding the 'event' stream to Splunk. Switching to 'detection' stream would reduce this by ~90% while still sending all alerts."

---

### Workflow 2: "Which org is costing the most?"

**Steps**:
1. Get usage stats for all organizations
2. Calculate estimated costs per org
3. Sort by total cost
4. Present as ranked table
5. Highlight outliers
6. Investigate top spenders

**Example Analysis**:
"Organization 'Production-US' ($1,250/mo) is your highest cost at 45% of total spend. It has 300 sensors with high output volume (500GB/mo). Would you like me to analyze optimization opportunities?"

---

### Workflow 3: "Can I reduce costs without losing security?"

**Steps**:
1. Analyze current usage patterns
2. Identify optimization opportunities:
   - Sensor culling (inactive sensors)
   - Output optimization (stream types, GCP same-region)
   - Query optimization (time ranges, filters)
   - Extension audit (unused or underutilized)
   - Performance modes (low mode for low-risk endpoints)
3. Estimate savings for each opportunity
4. Prioritize by impact vs effort
5. Provide implementation guidance

**Example Analysis**:
"I found 3 quick wins:
1. 40 sensors offline for >90 days (save ~$200/mo via culling)
2. GCS output in us-west1, LC in us-central1 (save ~$150/mo by switching to us-central1)
3. Event stream to S3 could be detection stream (save ~$300/mo, 95% volume reduction)

Total potential savings: ~$650/mo (43% reduction) with minimal security impact."

---

### Workflow 4: "Forecast next month's costs"

**Steps**:
1. Get current usage statistics
2. Identify trending metrics (if historical data available)
3. Calculate current run-rate
4. Project next month based on:
   - Quota settings
   - Current usage patterns
   - Planned changes (if any)
5. Provide estimate with breakdown
6. Flag any concerning trends

**Example Analysis**:
"Based on current usage:
- Sensors: 100 quota × $5 = $500
- Output data: 120GB @ $0.10/GB = $12
- Queries: 50M events @ $1/100M = $0.50
- Extensions: $25

Estimated next month: ~$537

Note: Output volume is trending up 15%/week. If this continues, you might hit $20 in output costs."

---

### Workflow 5: "Set up proactive cost monitoring"

**Steps**:
1. Identify key cost thresholds
2. Guide setup of Usage Alerts extension
3. Configure alerts for each critical SKU
4. Set up alert routing (Slack, email, etc.)
5. Recommend review cadence

**Example Setup**:
"I'll help you set up usage alerts:
1. Output data: Alert at 100GB/30 days
2. Query events: Alert at 100M events/7 days
3. Sensor quota: Alert at 90% utilization

These will create detections you can route to your team via Slack."

---

### Workflow 6: "Download invoices for finance team"

**Steps**:
1. Identify which months/years need invoices
2. Use `limacharlie:get_org_invoice_url` for each month
3. Provide direct download links
4. Explain invoice format and contents

**Example Interaction**:
User: "I need to download invoices for Q1 2025"
Assistant: "I'll generate download links for January, February, and March 2025..."

*Uses `limacharlie:get_org_invoice_url` for each month*

"Here are your Q1 2025 invoice download links:
- January 2025: [Direct download link]
- February 2025: [Direct download link]
- March 2025: [Direct download link]

These links go directly to your Stripe invoices in PDF format. They're ready to share with your finance team."

---

### Workflow 7: "What is this charge on my invoice?"

**Steps**:
1. User identifies an unfamiliar SKU or charge
2. Use `limacharlie:get_sku_definitions` to look up the SKU
3. Explain what the service does
4. Show current usage from `limacharlie:get_usage_stats`
5. Suggest optimization if applicable

**Example Interaction**:
User: "What is 'USP Telemetry Processed' on my invoice?"
Assistant: "Let me look that up..."

*Uses `limacharlie:get_sku_definitions`*

"'USP Telemetry Processed' is for the Universal Security Platform - this tracks telemetry ingested from non-endpoint sources like cloud logs, network devices, and third-party security tools. It's measured per GB processed at $15/GB.

Looking at your current usage, you've processed 23GB this cycle. This suggests you're ingesting external logs through USP adapters. Would you like me to show which adapters are consuming the most data?"

---

### Workflow 8: "What payment method am I using?"

**Steps**:
1. Use `limacharlie:get_billing_details` to fetch Stripe customer data
2. Extract payment method information
3. Present card details (masked) and status
4. Check for any payment issues

**Example Interaction**:
User: "What credit card do I have on file?"
Assistant: "Let me check your billing details..."

*Uses `limacharlie:get_billing_details`*

"Your payment method on file:
- Card type: Visa
- Last 4 digits: 9463
- Expiration: 10/2027
- Status: Valid

Your account is in good standing with no payment issues."

---

## Usage Analysis Examples

### Example 1: High Output Costs

**Data from `limacharlie:get_usage_stats`**:
```json
{
  "output_data": {
    "bytes_tx": 537824829440,  // ~500GB
    "cost_usd": 50.12
  }
}
```

**Analysis**:
"Your output data is your primary cost driver at $50/month. This is 500GB transmitted. Let me investigate your output configurations..."

**Recommendations**:
1. Check if you're sending `event` stream (high volume) vs `detection` stream (low volume)
2. Verify output destinations and regions
3. Consider GCP same-region outputs (free)
4. Enable compression if not already active
5. Review if all outputs are still needed

---

### Example 2: Sensor Over-Utilization

**Data from `limacharlie:get_usage_stats` & `limacharlie:get_org_info`**:
```json
{
  "quota": 100,
  "sensors_online": 125,
  "sensor_overage_hours": 1800
}
```

**Analysis**:
"You're running 125 sensors against a quota of 100. You have 25 sensors over quota (125% utilization). This causes service degradation - those over-quota sensors will experience spotty/unreliable connectivity. This is a reliability issue, not a cost issue (there are no overage charges)."

**Recommendations**:
1. Increase quota to 125-135 to match actual deployment and provide headroom
2. OR cull inactive sensors to reduce total count below 100
3. Review which sensors are critical and prioritize them within quota
4. Consider usage-based billing if sensor count varies significantly (avoids quota limits entirely)

---

### Example 2b: Low Quota Utilization (Wasteful)

**Data from `limacharlie:get_usage_stats` & `limacharlie:get_org_info`**:
```json
{
  "quota": 15,
  "sensors_online": 1
}
```

**Analysis**:
"You're using only 1 sensor out of a quota of 15 (7% utilization). This means you're paying for 14 sensors that you're not using. This is a significant waste of budget."

**Cost Impact**:
```
Current cost: 15 sensors × $5/sensor = $75/month
Optimized cost: 2-3 sensors × $5/sensor = $10-15/month
Potential savings: $60-65/month (80-87% reduction)
```

**Recommendations**:
1. **Reduce quota to 2-3 sensors** - This provides 100-200% headroom for growth while eliminating waste
2. If this is a development/test org with variable sensor count, consider usage-based billing instead of quota-based
3. If you genuinely plan to deploy 15 sensors soon, keep the quota but set a reminder to monitor utilization monthly
4. Consider if this org could be consolidated with another low-utilization org

**Key Insight**: Low quota utilization is NOT efficient - it represents wasted money. Optimal utilization is 75-95%, not 0-50%.

---

### Example 3: Query Cost Optimization

**Data from `limacharlie:get_usage_stats`**:
```json
{
  "query_events": 5000000000,  // 5 billion events scanned
  "cost_usd": 50.00
}
```

**Analysis**:
"Your queries scanned 5 billion events this cycle, costing $50. This suggests either very broad queries (30-day scans) or frequent searches."

**Recommendations**:
1. Narrow time ranges to minimum needed (use -4h instead of -30d)
2. Add platform filters early in queries (`plat == windows`)
3. Use specific event types instead of `*`
4. Save frequently-used queries
5. Use aggregations (COUNT, GROUP BY) instead of raw results

---

### Example 4: Multi-Org Cost Comparison

**Data from multiple `limacharlie:get_usage_stats` calls**:

| Organization | Sensors | Output | Events | Total Est. |
|--------------|---------|--------|--------|-----------|
| Prod-US | 300 | 500GB | 150M | $1,250 |
| Prod-EU | 200 | 250GB | 80M | $850 |
| Dev | 50 | 10GB | 5M | $175 |
| Test | 20 | 2GB | 1M | $85 |

**Analysis**:
"You're running 4 organizations with estimated monthly costs of $2,360. Prod-US accounts for 53% of total spend. The production orgs have different per-sensor costs due to output volume differences."

**Recommendations**:
1. Consider unified billing to consolidate invoices
2. Prod-US has 2x the output per sensor vs Prod-EU - investigate why
3. Dev/Test orgs are well-optimized - consider replicating patterns
4. Potential for cross-org policies on sensor performance modes

---

### Example 5: SKU Catalog Lookup

**Using `limacharlie:get_sku_definitions`**:

When a user asks "What extensions can I use?" or "What services does LimaCharlie charge for?", fetch the SKU catalog and present relevant services:

```json
{
  "sku_id": "extension_ext-strelka:bytes_scanned",
  "label": "Strelka File Analysis",
  "description": "Deep file analysis and metadata extraction. Recursively extracts and analyzes files to identify file types, extract embedded content, and generate security-relevant metadata.",
  "unit_label": "per GB scanned",
  "pricing": {
    "unit_amount": 10,
    "currency": "usd"
  }
}
```

**Presentation**:
"Strelka File Analysis is available as an extension. It performs deep file analysis and metadata extraction, perfect for malware analysis and threat hunting. It's priced at $10 per GB of data scanned. Would you like help setting this up?"

---

### Example 6: Subscription Status Check

**Using `limacharlie:get_billing_details`**:

```json
{
  "subscriptions": {
    "data": [{
      "status": "active",
      "billing_cycle_anchor": 1706922510,
      "current_period_start": 1735891310,
      "current_period_end": 1738569710
    }]
  }
}
```

**Analysis**:
"Your subscription is active. Current billing cycle:
- Started: January 3, 2025
- Ends: February 3, 2025

Your next invoice will be generated on February 3rd."

---

### Example 7: Comparing Actual Invoice to Estimates

**Workflow**:
1. User says their invoice is different from estimates
2. Use `limacharlie:get_org_invoice_url` to fetch the actual invoice
3. Use `limacharlie:get_billing_details` to see subscription and proration details
4. Compare against current usage stats
5. Explain the differences

**Example**:
"I see the difference. Your invoice shows $637 but current usage suggests ~$500. Here's why:

1. **Pre-paid items**: Your sensor quota for February ($500) is included
2. **Usage from January**: Output data and queries are billed in arrears ($125)
3. **Proration**: You increased quota mid-cycle (+$12 prorated)

The $637 total is correct: $500 (next month sensors) + $125 (last month usage) + $12 (proration) = $637"

---

## Best Practices for Billing Investigations

### General Principles

1. **Start with the Goal**: Understand what question you're trying to answer
2. **Gather Data First**: Use MCP tools to get actual usage before theorizing
3. **Focus on Top Drivers**: 80% of costs typically come from 20% of sources
4. **Compare Periods**: Look for changes vs previous cycles
5. **Validate Findings**: Cross-check data across tools (MCP, UI, API)
6. **Provide Context**: Explain what the numbers mean, not just the raw data
7. **Suggest Actions**: Don't just report problems, offer solutions
8. **Estimate Impact**: Quantify savings for optimization recommendations

### Analysis Workflow

1. **Understand Scope**: Single org, multi-org, specific time period
2. **Fetch Data**: Use MCP tools systematically
3. **Calculate Metrics**: Costs, trends, per-unit costs
4. **Identify Patterns**: What's normal vs unusual
5. **Investigate Anomalies**: Dig into unexpected findings
6. **Recommend Actions**: Prioritized list of optimizations
7. **Document Findings**: Clear summary of analysis
8. **Follow Up**: Track implementation and results

### Communication Tips

**Be Clear**:
- Use concrete numbers, not just percentages
- Provide context (is $500/month high or low?)
- Compare to benchmarks when possible

**Be Actionable**:
- Every finding should have a next step
- Prioritize by impact and effort
- Provide implementation guidance

**Be Honest**:
- If data is unclear, say so
- Note assumptions and limitations
- Admit when you need more information

---

## Multi-Organization Strategies

### Listing Accessible Organizations

**Use `limacharlie:list_user_orgs`** to get all accessible organizations:

```json
{
  "orgs": {
    "c82e5c17-d519-4ef5-a4ac-c454a95d31ca": {
      "name": "Home Maxime",
      "created": 1523273557
    },
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890": {
      "name": "Production US",
      "created": 1609459200
    }
  }
}
```

Then use `limacharlie:get_usage_stats` for each OID to get their usage data.

### Filtering Organizations

**By Name Pattern**:
"I can help you filter organizations by name. For example, only those starting with 'Prod-' or containing 'customer-'."

**By Usage Threshold**:
"I can filter to show only organizations with:
- More than X sensors
- Output data above Y GB
- Estimated costs above $Z"

**By Billing Model**:
- Quota-based organizations only
- Usage-based organizations only
- Organizations on custom plans

### Aggregating Multi-Org Data

When analyzing multiple organizations:

1. **Fetch data for each org** using MCP tools
2. **Aggregate metrics**:
   - Total sensors across all orgs
   - Combined output data
   - Total event volume
   - Sum of estimated costs
3. **Calculate percentages**:
   - Each org's % of total cost
   - Each org's % of total sensors
4. **Identify patterns**:
   - Cost per sensor by org
   - Output efficiency (GB per sensor)
   - Organizations above/below average
5. **Present insights**:
   - Highest cost orgs
   - Most efficient orgs
   - Outliers requiring investigation
