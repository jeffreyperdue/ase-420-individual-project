# Individual Project - StressSpec

## A.I Option: Vibe-Coding

### Features

1. **Input Ingestion**: Accepts .txt or .md requirements (one per line/bullet)  
2. **Requirement Parsing & Labeling**  
3. **Risk Detection Modules**  
4. **Configurable Rules**  
5. **Reporting (Markdown, CSV, JSON)**  
6. **Severity Scoring**  

---

## Requirements

### Epic Requirement

As a project manager,  
I want to analyze requirement documents for hidden risks,  
so that I can improve requirement quality and reduce project failures before development begins.

### Sub-Requirements

**2. Input Ingestion**  
As a developer,  
I want to upload a .txt or .md file containing requirements (one per line or bullet),  
so that the tool can process them automatically.

**3. Requirement Parsing & Labeling**  
As a QA engineer,  
I want to see each requirement assigned an ID and line number,  
so that I can trace flagged risks back to the original text.

**4. Risk Detection Modules**  
As a business analyst,  
I want to run checks for ambiguity, missing details, security gaps, and conflicts,  
so that unclear or problematic requirements are highlighted for revision.

**5. Configurable Rules**  
As a compliance officer,  
I want to edit a rules.json file to add or change detection terms,  
so that the tool adapts to different domains (e.g., finance, healthcare).

**6. Reporting**  
As a project manager,  
I want to generate reports in Markdown, CSV, and JSON formats,  
so that I can share results with the team in multiple ways.

**7. Severity Scoring**  
As a team lead,  
I want to see each flagged risk assigned a severity level (High, Medium, Low),  
so that I can prioritize which requirements need attention first.

---

## What is the Problem?

Most software project failures stem from unclear, unrealistic, or incomplete requirements.  
Studies show fixing requirement defects late can cost 5–10x more, and around 37% of enterprise project failures are linked to poor requirements.  

Current tools help write or clarify requirements, but they don’t stress-test them for hidden risks like ambiguity, conflicts, compliance gaps, or scalability issues.  
Teams often only discover these problems after coding begins, when fixing them is expensive and disruptive.

---

## Why is it Important?

Catching requirement problems early:

- Saves time and money by preventing costly rework later in development.  
- Improves quality by ensuring requirements are testable, realistic, and aligned with regulations.  
- Supports collaboration between project managers, analysts, developers, and QA by providing traceable, prioritized risk reports.  
- **Recruiter/industry relevance**: A tool like this demonstrates practical application of AI/rule-based analysis to real-world software engineering challenges.

---

## How Will You Solve It (Design Overview)?

The solution is a Python-based Requirements Stress Tester that acts like a “wind tunnel” for requirements:

- **Input Ingestion**: Accept .txt or .md files with one requirement per line.  
- **Requirement Parsing & Labeling**: Assign each requirement an ID (e.g., R001) and line number for traceability.  
- **Risk Detection Modules**: Run checks in categories such as ambiguity, availability, performance, security, privacy, conflicts, and scope. Each check is modular, keyword/regex-driven, and returns flags.  
- **Configurable Rules**: Store detection rules in rules.json so users can update keywords/conditions without editing code.  
- **Severity Scoring**: Assign each flag a severity (High/Medium/Low) and calculate totals to rank risky requirements.  
- **Reporting**: Generate outputs in Markdown (human-readable), CSV (sortable), and JSON (machine-readable). Reports link each flag back to its requirement ID and evidence.

---

## Milestones

### Sprint 1 (4 Weeks) → MVP Completed

- **Feature #1: Input Ingestion**  
  - Requirement #1: The system shall accept .txt or .md files with one requirement per line or bullet.  
  - *Plan*: Implement in Week 1 — set up CLI, file loader, and error handling.

- **Feature #2: Requirement Parsing & Labeling**  
  - Requirement #2: The system shall parse lines into requirement objects with IDs (R001…) and line numbers.  
  - *Plan*: Implement in Week 1–2 — build parser module, verify output with sample files.

- **Feature #3: Risk Detection Modules (initial)**  
  - Requirement #3: The system shall flag risks in at least 4 categories: Ambiguity, Availability, Performance, Security.  
  - *Plan*: Implement in Week 2–3 — create separate check modules, confirm they detect sample terms.

- **Feature #4: Configurable Rules (basic)**  
  - Requirement #4: The system shall load detection rules from rules.json so categories can be updated without code changes.  
  - *Plan*: Implement in Week 3 — JSON-driven configuration, connected to check modules.

- **Feature #5: Reporting (Markdown + CSV + JSON)**  
  - Requirement #5: The system shall generate report.md, report.csv, and risk_log.json with traceable requirement IDs.  
  - *Plan*: Implement in Week 4 — report writer module, validate outputs match findings.

- **Feature #6: Severity Scoring (basic)**  
  - Requirement #6: The system shall assign a default severity (High, Medium, Low) to each category.  
  - *Plan*: Implement in Week 4 — simple severity mapping per flag.

**Milestone Deliverable (End of Sprint 1):** MVP end-to-end flow from input → risk detection → multi-format reports with severity scoring.

---

### Sprint 2 (5 Weeks) → Expansion & Polish

- **Feature #3: Risk Detection Modules (expanded)**  
  - Requirement #7: The system shall add Privacy, Traceability, Scope, and Conflicts checks.  
  - *Plan*: Implement in Week 5–6 — new check modules + updated rules.json.

- **Feature #6: Severity Scoring (expanded)**  
  - Requirement #8: The system shall calculate totals by category/severity and highlight the “Top 5 riskiest requirements.”  
  - *Plan*: Implement in Week 7 — scoring aggregation + summary generator.

- **Feature #5: Reporting (enhanced)**  
  - Requirement #9: The system shall improve Markdown/CSV/JSON with summary totals and add optional HTML/visualization output.  
  - *Plan*: Implement in Week 8–9 — Jinja2 template for HTML + bar/radar chart for visualization.

- **Feature #4: Configurable Rules (extended)**  
  - Requirement #10: The system shall allow multiple domain rule profiles (e.g., healthcare, fintech).  
  - *Plan*: Implement in Week 9 — separate JSON profiles, selectable with CLI flag.

**Milestone Deliverable (End of Sprint 2):** Completed tool with all 8 risk categories, summary scoring, polished reporting, and at least one stretch feature (HTML or visualization).
