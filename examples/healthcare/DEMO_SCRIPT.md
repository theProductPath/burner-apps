# Healthcare Burner App — Demo Script
*The Product Path*

**Duration:** 10-15 minutes
**Audience:** Stakeholders interested in Burner Apps
**Goal:** Show how a single dataset becomes a purpose-built review tool — and how user feedback comes back structured and ready to act on

---

## Setup Before Demo

1. Open this folder in your file explorer
2. Have a terminal ready in this directory
3. (Optional) Have the sample flagged report open to show at the end

**Files you'll reference:**
- `Healthcare_Sample_Data.xlsx` — the starting dataset
- `generator.py` — the configuration that defines the app
- `healthcare_review.html` — the generated burner app
- `healthcare_flagged_sample.md` — example of exported feedback

---

## Part 1: The Problem (2 min)

> "Imagine you're a clinical data manager. You have a spreadsheet with 200 patients, 30 doctors, 400 appointments, and dozens of prescriptions. You need your team to review this data for quality issues—missing fields, scheduling conflicts, prescription problems."

> "You could share the Excel file, but then you're dealing with version control, people accidentally changing data, and no structured way to collect feedback."

> "What if instead, you could give them a purpose-built review app that they just open in their browser? No login, no installation, no training. They flag issues, add notes, and export a structured report."

> "That's what Burner Apps do."

---

## Part 2: Show the Dataset (2 min)

**Action:** Open `Healthcare_Sample_Data.xlsx` briefly

> "Here's our starting point—a typical healthcare dataset with multiple related sheets."

Point out:
- **Patients** (200 records) — demographics, insurance, emergency contacts
- **Doctors** (30 records) — specializations, departments, licenses
- **Appointments** (400 records) — linked to patients and doctors
- **Prescriptions** (78 records) — medications with dosages and refill counts
- **Medical History** (210 records) — conditions and diagnoses

> "This is real-world messy data. Some fields might be missing, some prescriptions might need review, some appointments might have conflicts."

---

## Part 3: Generate the App (3 min)

**Action:** Show the generator command

```bash
python generator.py Healthcare_Sample_Data.xlsx healthcare_review.html "Patient Record Audit"
```

> "One command. It reads the Excel file, embeds all the data into a self-contained HTML file, and creates a manifest for integrity tracking."

**Run the command** (or show it was already run):

```
Reading data from Healthcare_Sample_Data.xlsx...
  Found 200 patients
  Found 30 doctors
  Found 400 appointments
  Found 78 prescriptions
  Found 210 medical history

Generating HTML...
Done! Created healthcare_review.html (387 KB)
  Mission ID: patient-record-audit-20260125-xxxxx
```

> "Notice it created a Mission ID and a manifest file. These are for integrity verification—we can prove the exported feedback came from this exact dataset."

---

## Part 4: Live Demo of the App (5 min)

**Action:** Open `healthcare_review.html` in a browser

### Welcome Screen
> "When the reviewer opens this, they see a quick orientation. What the app does, how to use it."

Click **"Let's Go"**

### Search & Filter
> "They can search across all record types. Let me search for 'diabetes'..."

Type "diabetes" in search

> "Instantly finds patients with diabetes in their history, appointments about diabetes management, related prescriptions."

### Show Filter Tabs
> "They can filter to just Prescriptions, just Appointments, etc."

Click the **Prescriptions** tab

### Flag a Record
> "Here's a prescription that looks concerning—let's say the refill count seems high for a controlled substance."

Click **"Flag Issue"** on any prescription

> "Now they can add a note explaining the issue."

Type: "Refills exceed typical limit for this medication class"

### Show Flagged Counter
> "Notice the counter updated. They can keep reviewing, flagging issues as they find them."

### Export
Click **"Export Flagged"**

> "When they're done, they export. This creates a Markdown report with both human-readable tables AND machine-readable JSON."

---

## Part 5: The Feedback Loop (2 min)

**Action:** Open `healthcare_flagged_sample.md`

> "Here's what an exported report looks like. The reviewer found 6 issues across prescriptions, appointments, and patient records."

Point out:
- **Human-readable section** — tables with issue descriptions
- **Machine-readable JSON** — includes the mission ID and data fingerprint

> "That fingerprint lets us verify this feedback came from the exact dataset we generated the app from. No tampering, no confusion about which version was reviewed."

> "This report can be processed programmatically to generate tickets, update the source system, or feed into a reconciliation workflow."

---

## Part 6: The "Burner" Concept (1 min)

> "Why 'burner app'? Because it's disposable. One dataset, one review session, one export. Then you throw it away."

> "Next month when you have fresh data, you generate a new app. No state to maintain, no users to manage, no database to back up."

> "The app is the interface. The export is the artifact. The original data stays untouched."

---

## Q&A Prompts

If asked about customization:
> "The generator.py file is where you configure what fields to show, how records display, what colors to use. For a new domain, you'd copy the template and customize these sections."

If asked about security:
> "The HTML file contains the data, so treat it like you'd treat the spreadsheet. It can be emailed, put on a shared drive, or hosted internally. No external dependencies."

If asked about scale:
> "We've tested with thousands of records. The app stays responsive because it's all client-side JavaScript with smart rendering."

---

## Reset for Next Demo

To start fresh:
```bash
rm healthcare_review.html healthcare_review.manifest.json
```

Then regenerate with the same command.

---

## Files in This Demo Folder

| File | Purpose |
|------|---------|
| `Healthcare_Sample_Data.xlsx` | Source dataset (synthetic data) |
| `generator.py` | Healthcare-specific app configuration |
| `generator_base.py` | Shared generation logic (don't modify) |
| `healthcare_review.html` | Generated burner app |
| `healthcare_review.manifest.json` | Integrity tracking |
| `healthcare_flagged_sample.md` | Example of exported feedback |
| `DEMO_SCRIPT.md` | This file |
