# Burner Apps
**A product of The Product Path**
*Added to tPP portfolio: 2026-03-23*

---

## What This Is

Burner Apps is a software delivery methodology and client enablement offering built by The Product Path. It's the answer to a problem every enterprise has but nobody builds for: the bounded, time-limited problem that's too important for Excel and too small to justify a real application.

A Burner App is a purpose-built, single-use tool designed to solve one clearly defined problem — and then disappear. Like a burner phone: purpose-built, disposable, no strings attached. You use it for what you need, and when you're done, it's gone.

**The impermanence is the feature, not the limitation.**

---

## The Problem It Solves

Every enterprise runs into problems that sit in an awkward middle ground:

- Excel is too raw — the data is there but the interface doesn't match how people think
- A real application is too much — too slow to build, too expensive to maintain, too permanent for a temporary need
- Nothing gets built — people suffer through spreadsheets, lose insights, make worse decisions

Burner Apps fill that gap. In hours or days, not weeks. Bespoke for the specific people, specific data, and specific moment. And when the job is done, it disappears — leaving no orphaned software, no maintenance burden, no one asking "who owns this?" six months later.

---

## Two Modes

Not every Burner App needs to come back. There are two distinct modes:

**Mode 1 — One-Way**
The Creator builds the app to get information in front of the right people, clearly. The Consumer views, navigates, and acts on what they see. No report comes back. The app's job is done when the Consumer has done their work.

**Mode 2 — Round-Trip**
The Creator builds the app to collect structured input from the Consumer. The Consumer reviews, flags issues, adds notes, and exports a report. That report comes back to the Creator or Coordinator for processing. The full loop closes — without email chains, follow-up meetings, or inconsistent feedback formats.

`process_report.py` is only needed for Mode 2. If your Burner App is one-way, you don't need it.

---

## How It Works

Every Burner App follows the same core cycle — with an optional return leg for Mode 2:

**1. Generate** — A Python script takes a dataset (Excel, CSV, or other) and produces a self-contained HTML file. Everything is embedded: the data, the logic, the interface. No server. No database. No installation.

**2. Distribute** — The HTML file goes to the people who need it. They open it in a browser. They see their data, organized for their specific task. They do their review, make their decisions, or complete their workflow.

**3. *(Mode 2 only)* Collect** — The Consumer exports a structured report containing their flags, notes, and annotations — plus a cryptographic fingerprint verifying the report came from the exact dataset that was distributed.

**4. *(Mode 2 only)* Process** — The Creator or Coordinator runs `process_report.py` to turn the raw feedback into structured analysis. Tickets, updates, decisions — whatever the mission requires.

**5. Retire** — The file is deleted. Mission complete.

```
One command:
python generator.py data.xlsx review.html "Q1 Account Review"

Time from idea to delivery:  ~1 day
Training required:           Zero
Support tickets:             Zero
Software left behind:        Zero
```

---

## The Three Roles

Every Burner App engagement has three distinct roles:

| Role | Who They Are | Their Experience |
|---|---|---|
| **Creator** | The builder (Jones or a trained team member) | Runs scripts, configures templates, merges data — accepts complexity in exchange for power |
| **Coordinator** | The project lead | Bridges technical capability and business need — defines the job, distributes the app, collects reports |
| **Consumer** | The end user | Opens a file, does their work, exports a report — never sees the build process |

The separation matters: complexity stays with the Creator. The Consumer experiences only simplicity.

---

## What a Burner App Includes

Every Burner App ships with:

- **Welcome orientation** — built-in, explains exactly what to do
- **Real-time search and filtering** — across all data and record types
- **Relationship navigation** — click through connected records (e.g., account → contacts → sites)
- **Flag and annotate** — mark issues with notes
- **Structured export** — one-click report download in human-readable + machine-readable format
- **Integrity fingerprinting** — cryptographic verification that the report came from the exact dataset distributed
- **Session analytics** — how the user engaged: searches, flags, time spent
- **Optional expiration** — built-in self-destruct window so the app can't outlive its purpose

---

## The Feedback Loop

A Burner App isn't just a viewer — it's a round-trip system. When a Consumer exports their report, it contains:

- A human-readable summary (tables, issue descriptions, notes)
- A machine-readable JSON block with full record data, session analytics, and integrity fingerprints

Those fingerprints verify that the report was generated from the exact dataset that was distributed — no tampering, no version confusion. The Creator processes the report programmatically and returns a clean analysis to the Coordinator.

The whole cycle closes without a meeting, a follow-up email chain, or a shared spreadsheet.

---

## When to Use a Burner App

**Reach for a Burner App when:**
- The problem is bounded — there's a clear definition of done
- The timeline is short — days or weeks, not months
- The audience is known — specific people with a specific need
- The data is a snapshot — point-in-time, not a live dashboard
- Traditional tools are overkill — Excel is too raw, a full app is too much
- You need to move fast — no time for procurement or sprint planning

**Don't use a Burner App when:**
- The tool needs to run indefinitely
- Multiple users need to collaborate in real time
- Real-time data integration is essential
- Compliance or audit trails require permanent systems
- Enterprise infrastructure integration is required

---

## The Archetypes

Burner Apps work across a wide range of enterprise contexts. The portfolio is growing — each archetype is a tested, documented pattern ready to deploy.

| Archetype | Use Case | Status |
|---|---|---|
| **Data Review** | Stakeholders review, validate, or flag records from a dataset | ✅ Production-ready |
| **Candidate Interview** | Hiring teams review candidate profiles, share assessments | ✅ Production-ready |
| **Employee Onboarding** | New hire 30-day plan, shared between manager and employee | ✅ Production-ready |
| More coming | Board prep, project handoff, contract review, budget review... | Expanding |

See `archetypes/` for full documentation on each pattern.

---

## The tPP Offering

Burner Apps is delivered in two modes:

### Mode 1 — We Build It For You
Jones builds a bespoke Burner App for a client's specific problem. The client defines the job, provides the data, distributes to their team, and receives clean analysis back. Fast, high-impact, zero ongoing cost to the client.

**The pitch:** *"Tell me the problem. I'll have something in your hands by end of week."*

### Mode 2 — We Teach You To Build Them
Jones teaches a client team to build and deploy Burner Apps themselves. Includes the methodology, the tooling, and hands-on practice with their own data. The team leaves able to spin up Burner Apps independently for future bounded problems.

**The pitch:** *"Your team already has the problems. We'll give them the capability."*

---

## Folder Structure

```
Products/Burner-Apps/
├── README.md                     ← This file. Start here.
├── CHARTER.md                    ← Philosophy, principles, and the Burner App mindset
├── CREATOR-GUIDE.md              ← Step-by-step build and deployment guide
├── template/                     ← The generator and report processor (production-ready)
│   ├── generator.py              ← Python script: dataset → standalone HTML Burner App
│   └── process_report.py         ← Python script: report → verified analysis (Mode 2 only)
└── examples/                     ← Working Burner Apps built from real datasets
    ├── data-review-reference/    ← Data Review archetype documentation
    └── healthcare/               ← Complete Mode 2 example: healthcare data review
        ├── Healthcare_Sample_Data.xlsx
        ├── generator.py          ← Configured for healthcare dataset
        ├── healthcare_review.html ← Generated Burner App
        ├── README.md
        ├── DEMO_SCRIPT.md        ← Walkthrough for demos
        └── run-demo.sh           ← Regenerate the app from source data
```

---

## What This Is Not

- **Not a SaaS product** — There's no platform, no subscription, no hosted service
- **Not a code generator business** — The generator is a delivery mechanism, not the product
- **Not permanent software** — By design, every Burner App has a defined end of life

The product is the methodology and the execution capability. The generator is a means to an end.

---

## Status

The framework is production-tested across multiple real client engagements. The generator, report processor, and three-role workflow have been validated against real datasets in enterprise settings. What's new here is the tPP home, the cleaned-up documentation, and the formal positioning as a client offering.

**Burner Apps is ready to sell.**

---

*Burner Apps is a The Product Path methodology. Built by Jones, refined through client work, ready for the next engagement.*
