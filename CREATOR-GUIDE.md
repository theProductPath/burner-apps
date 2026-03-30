# Creator Guide: Building and Deploying Burner Apps
*The Product Path*

This guide documents the complete workflow for building a Burner App from scratch and processing the reports that come back. Read the Charter first if you haven't — this guide assumes you understand the philosophy. This is the how.

---

## Quick Reference

```
OUTBOUND: Dataset → generator.py → Burner App + Manifest → Coordinator → Consumer
INBOUND:  Consumer → Report → Coordinator → process_report.py → Analysis
```

---

## Part 1: Building a Burner App

### Step 1: Set Up the Engagement Folder

Each Burner App engagement gets its own folder. Keep it separate from the template.

```bash
# Create a new engagement folder
mkdir burner-{client}-{purpose}
cd burner-{client}-{purpose}

# Copy the generator and report processor from the template
cp ../template/generator.py .
cp ../template/process_report.py .
```

### Step 2: Understand Your Dataset

Before configuring, get clear on what you're working with:

```bash
# See what sheets exist in an Excel file
python3 -c "
import zipfile, xml.etree.ElementTree as ET
with zipfile.ZipFile('your_data.xlsx', 'r') as zf:
    workbook = ET.parse(zf.open('xl/workbook.xml'))
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    for sheet in workbook.findall('.//main:sheet', ns):
        print(f'  - {sheet.get(\"name\")}')
"
```

Ask yourself:
- What entity types are in this data? (accounts, contacts, orders, candidates, etc.)
- What relationships exist between them?
- What does the Consumer need to *do* with it? (review, flag, validate, assess?)
- What does "done" look like for them?

### Step 3: Configure the Generator

Edit `generator.py`. The top of the file has a clearly marked configuration section — everything you need to customize is there.

```python
ENTITY_CONFIG = {
    'entities': [
        {
            'name': 'accounts',        # Internal name — lowercase, no spaces
            'label': 'Accounts',       # Display label in the UI
            'sheet': 'Accounts',       # Excel sheet name (case-sensitive)
            'color': '#1565c0',        # Badge text color
            'bg_color': '#e3f2fd',     # Badge background color
        },
        {
            'name': 'contacts',
            'label': 'Contacts',
            'sheet': 'Contacts',
            'color': '#6a1b9a',
            'bg_color': '#f3e5f5',
        },
    ],
    
    # App header
    'title': 'Q1 Account Review',
    'heading': 'Account Data Review',
    'subtitle': 'Review and flag data quality issues before migration',
    
    # Welcome modal — this is what orients the Consumer
    # Write this as if you're briefing them in person
    'burner_context': '''
        You're reviewing account and contact records for data quality 
        before our CRM migration. Your job is to flag anything that 
        looks wrong — wrong industry, duplicate entries, missing contacts. 
        When you're done, click Export and send the report back to [Coordinator].
        This tool will be active until [date].
    ''',
    
    # Feature highlights shown in the welcome modal
    'welcome_features': [
        {'icon': '🔍', 'title': 'Search Everything', 'desc': 'Filter across all fields in real time'},
        {'icon': '🚩', 'title': 'Flag Issues', 'desc': 'Mark problems with notes — they\'re saved as you go'},
        {'icon': '📤', 'title': 'Export Report', 'desc': 'One click sends a structured report back'},
        {'icon': '🔗', 'title': 'See Relationships', 'desc': 'Click through from accounts to their contacts'},
    ],
}

FIELD_CONFIG = {
    'accounts': [
        {'field': 'Account_Name', 'label': 'Account', 'is_title': True},
        {'field': 'Industry', 'label': 'Industry'},
        {'field': 'Revenue', 'label': 'Revenue', 'format': 'currency'},
        {'field': 'Owner', 'label': 'Account Owner'},
    ],
    'contacts': [
        {'field': 'Full_Name', 'label': 'Name', 'is_title': True},
        {'field': 'Title', 'label': 'Title'},
        {'field': 'Email', 'label': 'Email'},
        {'field': 'Account_Name', 'label': 'Account'},
    ],
}

RELATIONSHIPS = [
    # Contacts link to their parent Account
    {'from': 'contacts', 'to': 'accounts', 'via': 'Account_Name', 'match': 'Account_Name'},
]
```

**Field format options:** `currency`, `date`, `phone`, or leave blank for plain text.

### Step 4: Test With Sample Data

Always test before using real data:

```bash
# Generate with a small sample dataset
python generator.py sample.xlsx test_review.html "Test Run"
```

Open `test_review.html` in a browser. Check:
- Does the welcome modal explain the task clearly?
- Are the right fields showing for each entity type?
- Do relationships navigate correctly?
- Does the flag/export flow work?

Iterate until it feels right. This is Phase 2 work — get it working well before generating the real version.

### Step 5: Generate the Real Burner App

```bash
python generator.py client_data.xlsx client_review.html "Client Name — Purpose"
```

Output:
- `client_review.html` — the Burner App (send to Coordinator)
- `client_review.manifest.json` — keep this; needed for report verification

**Optional: Add an expiration window**

```bash
python generator.py client_data.xlsx client_review.html "Client Name — Purpose" \
    --active-from "2026-04-01 09:00" \
    --active-until "2026-04-05 17:00"
```

The app will show a countdown to the Consumer and self-destruct gracefully when time runs out. Consumers can still export their flagged records from the expiration screen.

### Step 6: Deliver to the Coordinator

Send the Coordinator:
- The `.html` file
- The Burner App ID (shown in the generator output) for tracking

Keep locally:
- The `.manifest.json` file (needed for report verification later)
- The source data file

---

## Part 2: Processing Reports

When reports come back from the Coordinator:

### Step 1: Save the Report File

Save the `.md` report file in the same engagement folder as the manifest.

### Step 2: Run the Report Processor

```bash
# Full Creator analysis (default)
python process_report.py flagged_records.md

# Coordinator-friendly summary (action items, checkboxes)
python process_report.py flagged_records.md --coordinator

# Save to file instead of console
python process_report.py flagged_records.md -o analysis_output.md
```

### Step 3: What You Get Back

**Creator mode (default):**
- Full integrity verification (fingerprints confirmed against manifest)
- Session analytics (what the Consumer searched, filtered, how long they spent)
- Complete flagged record data with context
- Recommended actions per record

**Coordinator mode:**
- One-line integrity status
- Checklist of flagged items with action items
- Formatted for sharing with the client team

### Step 4: Verify Integrity

The first thing the processor does is verify fingerprints. Every Burner App carries:

| Fingerprint | What It Verifies |
|---|---|
| `burner_id` | Unique ID for this specific engagement |
| `data_fingerprint` | Hash of the input data — confirms the Consumer reviewed the dataset you sent |
| `app_fingerprint` | Hash of config + data — confirms the app wasn't modified |

If fingerprints match: ✅ INTEGRITY VERIFIED — the report is authentic.
If they don't match: investigate before proceeding.

---

## Part 3: The Report Structure

Every exported report contains two sections:

### Human-Readable (Markdown)

```markdown
# Flagged Records Report

**Burner App ID:** `acme-account-review-20260401-c2c63e`
**App Fingerprint:** `18a0397eb3c2bbd2`

## Session Analytics
| Metric | Value |
|--------|-------|
| Duration | 12 minutes |
| Searches | 14 |
| Records flagged | 7 |

## Flagged Records
### 1. Account: Acme Corp
**Issue:** Wrong industry — should be Manufacturing, not Technology
```

### Machine-Readable (JSON)

```json
{
  "burner_id": "acme-account-review-20260401-c2c63e",
  "data_fingerprint": "86cfbc53f7fbc561",
  "app_fingerprint": "18a0397eb3c2bbd2",
  "analytics": {
    "session_duration_minutes": 12,
    "searches": [...],
    "flags": [...]
  },
  "flagged": [
    {
      "id": "accounts-ACME_001",
      "title": "Acme Corp",
      "note": "Wrong industry — should be Manufacturing",
      "data": { ... }
    }
  ]
}
```

The JSON block enables programmatic processing. You can extract flagged records, compare across multiple reports, or feed the data into downstream systems without manual re-entry.

---

## Part 4: Expiration

The expiration mechanic enforces the temporary nature of the app at the technical level.

| State | Consumer Experience |
|---|---|
| Before active window | "Not Yet Active" screen with countdown to activation |
| During active window | Normal app with countdown banner showing time remaining |
| After expiration | "This Burner App has completed its mission" screen with final export option |

The countdown banner changes color when under 1 hour remains. The expiration screen allows one final export so Consumers who waited until the last minute can still submit their work.

**When to use expiration:**
- Production engagements — add it to reinforce the temporary nature and create urgency
- Sensitive data — ensures the file can't be used beyond its intended window
- Multi-stakeholder reviews — set a common deadline

**When to skip it:**
- Testing and iteration — easier to work without a ticking clock

---

## Part 5: Naming Conventions

Consistent naming makes Burner Apps feel professional and prevents confusion.

**File names:** `{client}-{purpose}-{date}.html`
```
acme-account-review-2026-04-01.html
heartland-candidate-review-spring-2026.html
```

**Burner App IDs** (auto-generated): `{purpose-slug}-{date}-{random}`
```
account-review-20260401-c2c63e
candidate-review-20260415-a8f231
```

**Engagement folders:**
```
burner-acme-account-review/
burner-heartland-recruiting/
burner-cpi-onboarding-q2/
```

---

## Part 6: File Structure (Per Engagement)

```
burner-{client}-{purpose}/
├── generator.py              # Configured for this engagement
├── process_report.py         # Report processor (copied from template)
├── {name}.html               # The Burner App (distribute this)
├── {name}.manifest.json      # Keep — needed for verification
├── flagged_records_*.md      # Incoming reports
├── analysis_output.md        # Processed analysis for Coordinator
└── (source data files)       # Keep secure — don't distribute
```

---

## Success Criteria

A Burner App is done when:

- [ ] Opens immediately in any browser — no setup, no login, no waiting
- [ ] Consumer understands what to do within 30 seconds of opening
- [ ] Completes the defined job
- [ ] Produces a structured, processable report
- [ ] Required no support tickets or follow-up explanations
- [ ] Can be deleted without consequence
- [ ] Was faster than any alternative approach

---

## Tips From the Field

1. **Write the welcome text like you're briefing them in person.** If you wouldn't say it in a kickoff meeting, don't put it in the modal.
2. **Test with real data before your first engagement.** The sample datasets in `demos/` are safe starting points.
3. **Keep the field count to 4-6 per entity.** More than that and the cards get cluttered.
4. **Name files descriptively.** `acme-q1-account-review.html` not `output.html`.
5. **Always use expiration for production.** It reinforces the Burner App contract and creates the right sense of urgency.
6. **The Coordinator sets expectations.** The app is only as clear as the mission brief the Coordinator writes. Work with them on the `burner_context` text.

---

*Creator Guide — The Product Path Burner Apps*
*See also: CHARTER.md (philosophy), archetypes/ (patterns), template/ (generator + processor)*
