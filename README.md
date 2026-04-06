# Burner Apps
**A product of theProductPath**
*Added to tPP portfolio: 2026-03-23*

---

## What This Is

Burner Apps is a software delivery methodology and client enablement offering built by theProductPath. It's the answer to a problem every enterprise has but nobody builds for: the bounded, time-limited problem that's too important for a spreadsheet and too small to justify a real application.

A Burner App is a purpose-built, single-use tool designed to solve one clearly defined problem — and then disappear. Like a burner phone: purpose-built, disposable, no strings attached. You use it for what you need, and when you're done, it's gone.

**The impermanence is the feature, not the limitation.**

**Public landing page:** <a href="https://burner-apps.theproductpath.com/" target="_blank" rel="noopener noreferrer">burner-apps.theproductpath.com</a>

*Last refreshed: 2026-04-06*

---

## The Problem It Solves

Every enterprise runs into problems that sit in an awkward middle ground:

- Existing tools are too raw — the information is there but the interface doesn't match how people think about the problem
- A real application is too much — too slow to build, too expensive to maintain, too permanent for a temporary need
- Nothing gets built — people suffer through workarounds, lose insights, make worse decisions

Burner Apps fill that gap. In hours or days, not weeks. Bespoke for the specific people, specific content, and specific moment. And when the job is done, it disappears — leaving no orphaned software, no maintenance burden, no one asking "who owns this?" six months later.

---

## What Goes In

A Burner App is generated from structured content — whatever form that takes for the problem at hand:

- **Spreadsheet data** — Excel, CSV, tabular records (the most common starting point)
- **Documents** — PDFs, Word files, text files processed and embedded
- **Transcripts and notes** — voice memos, interview notes, call transcripts converted to structured input
- **Any combination** — the generator is configured per engagement; the input format is whatever the problem requires

The generator's job is to take that content and produce a self-contained HTML file that a Consumer can open in any browser — no installation, no login, no setup.

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

**1. Generate** — A Python script takes your content and produces a self-contained HTML file. Everything is embedded: the data, the logic, the interface. No server. No database. No installation.

**2. Distribute** — The HTML file goes to the people who need it. They open it in a browser. They see their content, organized for their specific task. They do their work.

**3. *(Mode 2 only)* Collect** — The Consumer exports a structured report containing their flags, notes, and annotations — plus a cryptographic fingerprint verifying the report came from the exact content that was distributed.

**4. *(Mode 2 only)* Process** — The Creator or Coordinator runs `process_report.py` to turn the raw feedback into structured analysis. Decisions, updates, next steps — whatever the mission requires.

**5. Retire** — The file is deleted. Mission complete.

```
One command:
python generator.py source-data/ review.html "Q1 Account Review"

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
| **Creator** | The builder | Configures and runs the generator, processes reports — accepts complexity in exchange for power |
| **Coordinator** | The project lead | Defines the job, distributes the app, collects reports — bridges capability and business need |
| **Consumer** | The end user | Opens a file, does their work, exports a report — never sees the build process |

The separation matters: complexity stays with the Creator. The Consumer experiences only simplicity.

---

## What a Burner App Includes

Every Burner App ships with:

- **Welcome orientation** — built-in, explains exactly what to do
- **Search and filtering** — find what matters across all content
- **Navigation** — move through connected records and relationships
- **Flag and annotate** — mark issues, add notes, capture assessments
- **Structured export** — one-click report download in human-readable + machine-readable format
- **Integrity fingerprinting** — cryptographic verification that the report came from the exact content distributed
- **Session analytics** — how the user engaged: searches, flags, time spent
- **Optional expiration** — built-in self-destruct window so the app can't outlive its purpose

---

## When to Use a Burner App

**Reach for a Burner App when:**
- The problem is bounded — there's a clear definition of done
- The timeline is short — days or weeks, not months
- The audience is known — specific people with a specific need
- The content is a snapshot — point-in-time, not live or continuously updating
- Existing tools are overkill or underpowered for this specific task
- You need to move fast — no time for procurement or sprint planning

**Don't use a Burner App when:**
- The tool needs to run indefinitely
- Multiple users need to collaborate in real time
- Real-time data integration is essential
- Compliance or audit trails require permanent systems
- Enterprise infrastructure integration is required

---

## The tPP Offering

Burner Apps is delivered in two ways. Public-facing site and marketing assets live in the companion repo: <a href="https://github.com/theProductPath/burner-apps-site" target="_blank" rel="noopener noreferrer">burner-apps-site</a>.

Burner Apps is delivered in two ways:

### We Build It For You
Steven Jones builds a bespoke Burner App for a client's specific problem. The client defines the job, provides the content, distributes to their team, and receives clean analysis back. Fast, high-impact, zero ongoing cost to the client.

**The pitch:** *"Tell me the problem. I'll have something in your hands by end of week."*

### We Teach You To Build Them
Steven Jones teaches a client team to build and deploy Burner Apps themselves. Includes the methodology, the tooling, and hands-on practice with their own content. The team leaves able to spin up Burner Apps independently for future bounded problems.

**The pitch:** *"Your team already has the problems. We'll give them the capability."*

---

## Folder Structure

```
Burner-Apps/
├── README.md                     ← This file. Start here.
├── CHARTER.md                    ← Philosophy, principles, and the Burner App mindset
├── CREATOR-GUIDE.md              ← Step-by-step build and deployment guide
├── template/                     ← The generator and report processor (production-ready)
│   ├── generator.py              ← Python script: content → standalone HTML Burner App
│   └── process_report.py         ← Python script: report → verified analysis (Mode 2 only)
└── examples/                     ← Working Burner Apps built from real content
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
- **Not limited to spreadsheets** — The generator works with any structured content: data files, documents, transcripts, or combinations
- **Not permanent software** — By design, every Burner App has a defined end of life

The product is the methodology and the execution capability. The generator is a means to an end.

---

## Status

The framework is production-tested across multiple real client engagements. The generator, report processor, and three-role workflow have been validated across data review, candidate evaluation, and other enterprise use cases.

**Burner Apps is ready to sell.**

---

*Burner Apps is a theProductPath methodology. Built by Steven Jones, refined through client work, ready for the next engagement.*
