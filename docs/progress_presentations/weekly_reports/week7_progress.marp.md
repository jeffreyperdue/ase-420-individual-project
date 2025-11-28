---
marp: true
size: 16:9
paginate: true
theme: default
---

<!-- _class: lead -->
# StressSpec Week 7 Progress Report
## Sprint 2 – 8-Category Completion (Traceability + Scope)

**Individual Project – Jeffrey Perdue**  
**Week 7: New Detectors, Rules, UI polish, Tests**

---

## 🎯 Week 7 Highlights

- ✅ Added two new detectors: **Traceability** and **Scope**
- ✅ Updated `RiskCategory` enum and **Factory** registry (now 8 categories)
- ✅ Extended `data/rules.json` with new rules and severities
- ✅ Implemented user‑friendly Traceability heuristics + severity downgrades
- ✅ Implemented Scope high‑severity escalation for explicit boundary violations
- ✅ Added unit + integration tests; full suite passing
- ✅ Web UI: Category filter updated to include Traceability/Scope
- ✅ Example file to trigger all 8 categories

---

## 📦 Code Changes (Core)

- `src/models/risk.py`: add `TRACEABILITY`, `SCOPE` to `RiskCategory`
- `src/factories/detector_factory.py`: register `TraceabilityDetector`, `ScopeDetector`
- `src/detectors/traceability_detector.py`: permissive signals (IDs, AC, test refs); downgrade to Medium when any signal present
- `src/detectors/scope_detector.py`: scope‑creep, undefined boundary, third‑party w/o spec; escalate to High for explicit phrases and missing constraints
- `data/rules.json`: add `traceability` + `scope` sections (enabled)

---

## 🔍 Detection Logic (Summary)

### Traceability 
- Signals: Requirement ID (`R###`, `REQ-#`, `US-#`, `FR-#`, `ABC-123`), Acceptance Criteria ("Given/When/Then", "Acceptance Criteria", "AC:"), Test refs ("TC-", "Test Case", "validated by", "QA")
- No signals ⇒ single High (default). Partial signals ⇒ remaining gaps flagged Medium

### Scope 
- Scope‑creep terms (e.g., "any API", "all platforms", "every browser")
- Undefined external dependency boundaries
- Third‑party integration without provider/version/protocol/SLA ⇒ High

---

## 🧪 Testing

- Unit tests:
  - `tests/test_traceability_detector.py`
  - `tests/test_scope_detector.py`
- Integration:
  - `tests/test_integration_new_detectors.py` asserts `traceability` and `scope` categories appear end‑to‑end
- Result: **72 passed, 0 failed** (14 warnings)

---

## 🌐 Web UI Updates

- Results page category filter now includes:
  - `Traceability`, `Scope` (in addition to existing 6)
- Risk rendering and category summaries are data‑driven; new categories auto‑appear

---

## 📁 Example File (All 8 Categories)

- `example_files/all_categories_sample_requirements.txt`
- Uses `---` separators to avoid over‑merging by structured parser
- Triggers: Ambiguity, Missing Detail, Security, Conflict, Performance, Availability, Traceability, Scope

---

## ▶️ How to Run (Web UI)

```powershell
cd ase-420-individual-project
python -m venv .venv; . .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DEBUG="True"; python web\main.py
```

- Open `http://127.0.0.1:8000/`
- Upload the example file above and view detected categories

---

## ✅ Week 7 Deliverables Status

- Traceability & Scope detectors implemented
- Factory + Enum wired for 8 categories
- Rules added/enabled; severities set (user‑friendly defaults)
- High‑severity escalation for explicit scope violations
- Tests: unit + integration, full suite passing
- Web UI filter updated; example file added

---

## 📌 Next Steps (Minor)

- Documentation refresh (README / project docs) with examples for the 2 new categories
- Optional: further tune structured parsing continuation heuristics

---

## 🏁 Week 7 Outcome

**8‑Category system completed and verified**  
Detectors integrated, tests passing, UI updated, and example provided for demo.


