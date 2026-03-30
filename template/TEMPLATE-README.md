# Mission App Template

A starter template for building Mission Apps—purpose-built, single-use data exploration tools.

## Quick Start

1. **Copy this folder** to create a new mission:
   ```bash
   cp -r mission-template mission-xyz
   cd mission-xyz
   ```

2. **Edit `generator.py`** — customize the configuration section at the top:
   - Define your entity types (what kinds of records you have)
   - Define fields to display for each entity
   - Define relationships between entities (optional)

3. **Prepare your data** as an Excel file with one sheet per entity type

4. **Generate the Mission App**:
   ```bash
   python generator.py data.xlsx output.html "Review Title"
   ```

5. **Deliver** the HTML file to your stakeholder

---

## Configuration Guide

### Entity Configuration

At the top of `generator.py`, define your entities:

```python
ENTITY_CONFIG = {
    'entities': [
        {
            'name': 'products',        # Internal name (lowercase, plural)
            'label': 'Products',       # Display label
            'sheet': 'Products',       # Excel sheet name
            'color': '#1976d2',        # Badge text color
            'bg_color': '#e3f2fd',     # Badge background color
        },
        {
            'name': 'orders',
            'label': 'Orders',
            'sheet': 'Orders',
            'color': '#7b1fa2',
            'bg_color': '#f3e5f5',
        },
    ],
    'title': 'Inventory Review Tool',
    'heading': 'Inventory Review',
    'subtitle': 'Search and explore products and orders',
}
```

### Field Configuration

Define which fields to display for each entity:

```python
FIELD_CONFIG = {
    'products': [
        {'field': 'Name', 'label': 'Product Name', 'is_title': True},
        {'field': 'SKU', 'label': 'SKU'},
        {'field': 'Price', 'label': 'Price'},
        {'field': 'Category', 'label': 'Category'},
        {'field': 'InStock', 'label': 'In Stock'},
    ],
    'orders': [
        {'field': 'OrderID', 'label': 'Order ID', 'is_title': True},
        {'field': 'Customer', 'label': 'Customer'},
        {'field': 'Date', 'label': 'Order Date'},
        {'field': 'Total', 'label': 'Total'},
        {'field': 'Status', 'label': 'Status'},
    ],
}
```

- `field`: The column name in your Excel data
- `label`: How it displays in the UI
- `is_title`: Set to `True` for the main display name (one per entity)

### Relationships (Optional)

If entities relate to each other, define the relationships:

```python
RELATIONSHIPS = [
    {'from': 'orders', 'to': 'products', 'field': 'ProductID', 'label': 'Product'},
    {'from': 'orders', 'to': 'customers', 'field': 'CustomerID', 'label': 'Customer'},
]
```

> Note: The current template doesn't auto-generate relationship UI from this config yet. For complex relationships, you may need to customize the render functions manually.

---

## Excel Data Format

Your Excel file should have:
- One sheet per entity type
- Sheet names matching the `sheet` value in your config
- First row as column headers
- Data starting from row 2

Example structure:
```
data.xlsx
├── Products (sheet)
│   └── Name, SKU, Price, Category, InStock
├── Orders (sheet)
│   └── OrderID, Customer, Date, Total, Status
```

---

## Customization Zones

The generator script has clearly marked sections:

| Section | Purpose | When to Modify |
|---------|---------|----------------|
| `CUSTOMIZE: Configuration` | Entity types, titles | Always |
| `REUSABLE: HTML Template` | Page structure, CSS | Rarely (colors, branding) |
| `REUSABLE: Core JavaScript` | Flag/export logic | Rarely |
| `CUSTOMIZE: Render Functions` | How records display | Sometimes (complex layouts) |
| `REUSABLE: Excel Reading` | Data loading | Only if changing data source |

---

## Common Modifications

### Change the color scheme

In `HTML_TEMPLATE`, find the gradient:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

Replace with your preferred colors.

### Add more fields to export

In `CORE_JAVASCRIPT`, find the export function and add fields to the report format.

### Use a different data source

Replace the `read_excel_data` function with one that reads CSV, JSON, or calls an API.

---

## What You Get

The generated HTML file includes:

- **Welcome modal** — Orients the user, explains the tool's purpose
- **Search** — Real-time filtering across field values only (not field names)
- **Search highlighting** — Matched text highlighted in yellow
- **Type filters** — Show only specific entity types
- **Stats cards** — Live "X of Y" counts that update as you search; clickable to filter
- **Record cards** — Display each record with its fields
- **Clickable relationships** — Navigate between related records
- **Clear button** — Reset search and filters, scroll to top
- **Flag system** — Mark records with issues, add notes
- **Export** — Download flagged records as a text report

### Navigation Features

- **Click relationship tags** to navigate to related records
- **Click stats cards** to filter to that entity type
- **Clear button** appears when searching; resets everything

---

## Processing Reports

When stakeholders return flagged records reports (`.md` files), use `process_report.py` to verify and analyze them. The processor generates a formatted markdown report file.

### Usage

```bash
# Creator report (full detail) - default
python process_report.py flagged_records.md

# Coordinator report (action-focused)
python process_report.py flagged_records.md --coordinator

# Custom output filename
python process_report.py flagged_records.md -o my_report.md
```

### Report Modes

| Mode | Flag | Audience | Contents |
|------|------|----------|----------|
| **Creator** | `--creator` (default) | You (the builder) | Full integrity verification, session analytics, complete record data, detailed actions |
| **Coordinator** | `--coordinator` | Person applying changes | Summary table, action checklist with checkboxes, minimal detail |

### What It Does

| Section | Creator | Coordinator |
|---------|---------|-------------|
| **Integrity Check** | Full table with all fingerprints | One-line status |
| **Session Analytics** | Complete activity breakdown | — |
| **Flagged Records** | Full data tables per record | Checklist format |
| **Recommended Actions** | Detailed per-record suggestions | Inline with checklist |

### Requirements

- The report's `.manifest.json` file must be in the current directory or the report's directory
- The manifest is created automatically when you generate the Mission App

### Sample Creator Output

```markdown
# Mission Report: CRM Data Review

**Report Type:** Creator (Full Detail)
**Processed:** 2026-01-18 08:43:50
**Records Flagged:** 3

---

## Integrity Verification

| Check | Report Value | Manifest Value | Status |
|-------|--------------|----------------|--------|
| Mission ID | `crm-review-20260118-a3fcfe` | `crm-review-20260118-a3fcfe` | ✅ PASS |

> ✅ **INTEGRITY VERIFIED** - Report matches source Mission App

---

## Session Analytics

**Duration:** 2 minutes

| Activity | Count |
|----------|-------|
| Searches | 7 |
| Flag/Unflag Actions | 3 |

### Search Queries

- "ash" → 11 results
- "man" → 88 results
```

### Sample Coordinator Output

```markdown
# Action Items: CRM Data Review

**Report Type:** Coordinator (Action-Focused)
**Records to Review:** 3

> ✅ Report integrity verified

---

## Items Requiring Action

| Type | Count |
|------|-------|
| accounts | 2 |
| opportunities | 1 |
| **Total** | **3** |

### Action Checklist

- [ ] **accounts:** Beta Technologies Corp
  - Issue: Wrong industry classification
  - Action: Verify and correct

- [ ] **opportunities:** Support Contract
  - Issue: Amount seems too high
  - Action: Review
```

### Extending for Mission-Specific Analysis

The base `process_report.py` is generic. For missions with complex data relationships (like the real estate example with Leases → Properties → Tenants), copy the script to your mission folder and add cross-reference logic:

```python
def cross_reference_records(flagged_records, source_data):
    """Add mission-specific relationship lookups here"""
    # Example: Look up related records by ID
    # lease = find_by_id(source_data['Leases'], record['Lease_ID'])
    pass
```

---

## Example Missions

See the `mission-acs` folder for a complete example of the ACS Data Review tool built using this pattern (though it predates this template).

---

## Expiration (Self-Destruct)

Mission Apps can include a built-in expiration mechanism to enforce their temporary nature.

### Basic Usage

```bash
# No expiration (default) - for testing
python generator.py data.xlsx review.html "Q1 Review"

# With expiration window
python generator.py data.xlsx review.html "Q1 Review" \
    --active-from "2026-01-21 09:00" \
    --active-until "2026-01-23 17:00"
```

### Options

| Option | Description | Example |
|--------|-------------|---------|
| `--active-from` | When the app becomes active | `"2026-01-21 09:00"` |
| `--active-until` | When the app expires | `"2026-01-23 17:00"` |
| `--no-expiration` | Explicitly disable (same as default) | — |

### Date Formats

Supported formats:
- `YYYY-MM-DD HH:MM:SS` (e.g., `"2026-01-21 09:00:00"`)
- `YYYY-MM-DD HH:MM` (e.g., `"2026-01-21 09:00"`)
- `YYYY-MM-DD` (e.g., `"2026-01-21"` - defaults to midnight)
- `MM/DD/YYYY` variants also supported

### Workflow Example

**Scenario:** Building app on Saturday, Coordinator sends Tuesday, Consumer has until Thursday.

```bash
# Saturday: Generate for testing (no expiration)
python generator.py data.xlsx review_test.html "Q1 Review"

# Saturday: Generate final version with expiration
python generator.py data.xlsx review_final.html "Q1 Review" \
    --active-from "2026-01-21 09:00" \
    --active-until "2026-01-23 17:00"
```

### What Happens

| State | User Experience |
|-------|----------------|
| **Before active window** | "Not Yet Active" screen with activation countdown |
| **During active window** | Normal app with countdown banner showing time remaining |
| **After expiration** | "Mission Complete" self-destruct screen with export option |

### Features

- **Welcome modal** shows expiration date prominently
- **Countdown banner** updates in real-time (changes color when < 1 hour left)
- **Graceful expiration** with amusing "self-destruct" animation
- **Export after expiration** — Users can still export flagged records from the expiration screen
- **Manifest file** includes expiration info for tracking

---

## Tips

1. **Start simple** — Get one entity working before adding more
2. **Test with sample data** — Don't wait for the full dataset
3. **Keep field counts reasonable** — 4-6 fields per entity is usually enough
4. **Name files descriptively** — `marketing_q1_2026.html` not `output.html`
5. **Use expiration for production** — Keep testing versions without expiration, add it for final delivery
