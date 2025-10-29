🗓 Week 7 Plan – StressSpec (Sprint 2)

Sprint 2 Theme: 8-Category Completion
Focus: Implement Traceability & Scope Risk Detection
Duration: ~5–6 hours

🎯 Week 7 Objectives

Add Remaining Risk Detection Modules

Implement Traceability and Scope detectors to complete the original 8-category detection goal.

Integrate new detectors into the existing detector_factory.py and update the rules.json file accordingly.

Maintain consistency with the modular structure used in the six existing detectors.

Update and Expand Test Coverage

Add unit and integration tests for both new detectors.

Ensure coverage of positive, negative, and edge-case scenarios.

Verify new detectors integrate smoothly into the main analysis pipeline.

Preserve and Validate 100% Test Pass Rate

Re-run full test suite after new detector integration.

Confirm that all 63+ tests (including new ones) pass consistently.

Perform minor refactors if needed for compatibility or maintainability.

Documentation Updates

Add sections for Traceability and Scope detection to project documentation (README.md or HOWTO.md).

Include examples of flagged requirements and sample report snippets.

Key Design Decisions (User-friendly and Permissive)

Traceability (be forgiving, helpful):
- Accept common ID formats: R### (parser-generated), REQ-#, US-#, FR-#, and generic alphanumeric-with-dash (e.g., ABC-123). Presence of any ID-like token counts as traceability present.
- Acceptance criteria markers: treat any of the following as valid signals: "Given/When/Then", "Acceptance Criteria", "AC:", checklists/bullets under a requirement.
- Test references: recognize "TC-", "Test Case", "Unit Test", "Integration Test", "verification", "validated by", "QA" as valid cues.
- Severity posture: default High for complete absence of all traceability signals; downgrade to Medium when at least one signal (ID, AC, or test ref) is present but others are missing. Messaging favors guidance over penalties.

Scope (pragmatic and non-noisy):
- Focus on clear scope creep or undefined boundaries (e.g., "support all platforms", "integrate with any API", external system commitments without constraints). Avoid duplicating ambiguity detector behavior.
- Severity posture: default Medium; escalate to High for explicit boundary violations that imply significant delivery risk (e.g., "support all third-party payment providers" with no constraints).

🧩 Planned Tasks
Task	Description	Est. Time	Priority
T1: Traceability Detector	Create traceability_detector.py using BaseRiskDetector; detect missing IDs/AC/test references with permissive heuristics and rule-level severity downgrades for partial signals.	2.5h	High
T2: Scope Detector	Create scope_detector.py for identifying boundary violations or obvious scope creep; keyword/pattern-based only, tuned to minimize false positives.	2.5h	High
T3: Wire Categories & Rules	Update RiskCategory enum with TRACEABILITY and SCOPE; register detectors in detector_factory.py; add detectors.traceability and detectors.scope in data/rules.json with severities and rules enabled.	0.5h	High
T4: Write New Tests	Add tests under tests/test_traceability_detector.py and tests/test_scope_detector.py (positive/negative/edge, including permissive traceability cases).	1h	High
T5: Regression Testing	Run full pytest suite to confirm all previous and new tests pass without regressions.	0.5h	Critical
T6: Documentation Refresh	Update README/HOWTO to reflect 8-category system with examples for traceability and scope.	0.5h	Medium

Rules.json Additions (high level)

Traceability rules (enabled: true, default severity: high):
- missing_requirement_id: patterns for common ID formats.
- missing_acceptance_criteria: keywords ["Given", "When", "Then", "Acceptance Criteria", "AC:"] and simple list detection.
- missing_test_reference: keywords ["TC-", "Test Case", "Unit Test", "Integration Test", "verification", "validated by", "QA"].
Implementation note: detector will downgrade severity to medium when any other traceability signal is present.

Scope rules (enabled: true, default severity: medium):
- out_of_scope_terms: keywords indicating unlimited breadth (e.g., "any API", "all platforms", "every browser").
- undefined_system_boundary: references to external systems/services without constraints.
- third_party_dependency_without_spec: triggers ["integrate", "connect", "sync"] with required_with constraints (e.g., "specific provider", "version", "protocol").

✅ End-of-Week Success Criteria

 traceability_detector.py and scope_detector.py implemented following the base detector pattern with user-friendly messaging.

 rules.json updated with new risk categories, enabled flags, severities, and rules.

 RiskCategory enum and RiskDetectorFactory updated; factory loads all 8 categories.

 100% test pass rate maintained (including new tests) with low false-positive rates.

 Documentation reflects 8-category system and includes example outputs.