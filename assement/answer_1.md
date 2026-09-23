# Answer 1 — Incident Triage

## Question

A daily sales pipeline ran successfully at 6:00 AM, but the dashboard now shows revenue 40% lower than yesterday. You only have 30 minutes before the business team uses the dashboard in a meeting.

**Please answer in this format:**

1. What would you check first, second, and third?
2. What evidence would help you decide whether the problem comes from the source data, the transformation logic, or the dashboard layer?
3. Would you allow the dashboard to stay live, temporarily disable it, or add a warning message? Explain briefly.

## Answer

### 1. What to check — first, second, third

**Step 1 — Pipeline and data-quality monitoring**

Verify the 6:00 AM pipeline actually completed correctly — "ran successfully" doesn't mean "data is correct."

Check:

- Dashboard monitoring pipeline
- Pipeline/task status and logs
- Failed or retried tasks
- Source-to-warehouse data reconciliation
- Data-quality checks

**Step 2 — Trace the revenue metric backward from the dashboard**

Map how the revenue metric flows, then compare today vs. yesterday at each layer to find the **first point where the 40% gap appears**.

```text
Dashboard
    ↓
Dashboard query / semantic layer
    ↓
Final table / view related
    ↓
Transformation models
    ↓
Staging tables
    ↓
Source data
```

**Step 3 — Investigate the layer where the mismatch starts**

| Layer | What to look for |
|---|---|
| Source / ingestion | Missing records, late data, schema changes, incomplete extraction |
| Transformation | Joins, filters, date/timezone logic, aggregation, recent code changes |
| Dashboard | Incorrect filters, calculated fields, stale cache/extract, wrong underlying table/view |

---

### 2. Evidence: source data vs. transformation vs. dashboard

Use monitoring first, then trace backward from the dashboard until the first mismatch is found.

| Evidence | Likely issue |
|---|---|
| Pipeline task failed or source-to-warehouse reconciliation failed | Source / ingestion |
| Source and staging data are already 40% lower | Source / ingestion |
| Staging is correct but transformed table is 40% lower | Transformation |
| Transformation tests/data-quality checks fail | Transformation |
| Final warehouse table contains the correct $1M | Dashboard needs investigation |
| Dashboard SQL returns $1M but dashboard displays $600K | Dashboard layer |
| Dashboard has stale data, wrong filter, or incorrect calculated field | Dashboard layer |

The key question: **at which layer does the revenue first drop by 40%?** Finding that point focuses the investigation instead of checking the whole pipeline blindly.

---

### 3. Keep it live, disable it, or add a warning?

**Decision: keep the dashboard live, add a clear data-quality warning.**

> ⚠️ **Data quality issue:** Today's revenue data may be incomplete or inaccurate. The Data Engineering team is investigating.

Reasoning:

- Don't let users silently read the 40% drop as a confirmed business result.
- Surface the warning directly in the dashboard/data-quality status so all downstream consumers see it.
- Disabling entirely removes visibility the business may still need for unaffected metrics on the same view.

Response sequence:

```text
Detect → Locate first mismatch → Communicate warning → Fix → Validate → Remove warning
```

**Key point:** "pipeline succeeded" does not mean "data is correct." Pipeline monitoring confirms the workflow ran; reconciliation and data-quality checks confirm the resulting data can be trusted.
