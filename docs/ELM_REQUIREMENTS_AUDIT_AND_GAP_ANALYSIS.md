# Employee Leave Management (ELM): Comprehensive Requirements Audit & Gap Analysis
## Phase 1 & Phase 2 Codebase Audit against Synchronized Baseline v1.4

### 1. Executive Audit Summary
* **Total Business Rules Evaluated:** 38 (BR-EL-001 to BR-EL-038)
* **Fully Compliant (Implemented & Verified):** 36
* **Retired Identifiers (Per Official Specification):** 2 (`BR-EL-021`, `BR-EL-026`)
* **Missing or Non-Compliant Rules:** 0
* **Automated Test Coverage:** 18 passing backend test cases covering all lifecycles.
* **Frontend Verification:** Production build verified with zero errors (`npm run build`).

---

### 2. Comprehensive Business Rules Traceability Matrix

| Rule ID | Rule Title | Audit Status | Implementation in Codebase | Compliance Notes |
| :--- | :--- | :---: | :--- | :--- |
| **BR-EL-001** | Supported leave-category eligibility | ✅ **COMPLIANT** | `LeaveType` model defines CL, RH, SCL, EL, VL, COL. Validated in serializer & `leave_service.py`. | Category applicability enforced per institutional baseline. |
| **BR-EL-002** | Casual Leave entitlement and lapse | ✅ **COMPLIANT** | `LeaveBalance` credits 8 days CL. `process_year_end_rollover` lapses unconsumed CL completely. | No carry-forward of CL across calendar years. |
| **BR-EL-003** | Restricted Holiday entitlement and applicability | ✅ **COMPLIANT** | `HolidayCalendar` stores declared Restricted Holidays. Single-day constraint and date verification enforced. | Unavailed RH lapses at year end. |
| **BR-EL-004** | Special Casual Leave entitlement and admissibility | ✅ **COMPLIANT** | 15 days SCL per calendar year tracked. Admissibility judged by authority; unavailed SCL lapses. | Complies with institutional threshold. |
| **BR-EL-005** | Non-faculty Earned Leave credit and carry-forward | ✅ **COMPLIANT** | 30 days annual quota. Unused EL carries forward, subject to statutory 300-day accumulation cap. | Ceiling enforced in `process_year_end_rollover`. |
| **BR-EL-006** | Faculty Vacation Leave entitlement and vacation-period applicability | ✅ **COMPLIANT** | 60 days annual VL quota for faculty. Validated against declared vacation windows. | Vacation leave restricted to faculty. |
| **BR-EL-007** | VL-to-EL year-end conversion | ✅ **COMPLIANT** | `process_year_end_rollover` converts unconsumed VL to EL at 2:1 ratio (50%). | VL itself does not carry forward. |
| **BR-EL-008** | Treatment of EL created by VL conversion | ✅ **COMPLIANT** | Converted EL credited directly to applicant's EL `LeaveBalance` under statutory 300-day ceiling. | Converted quota usable in subsequent years. |
| **BR-EL-009** | Commuted Leave entitlement and treatment | ✅ **COMPLIANT** | 20 days COL per year. Unused balance carries forward across calendar year boundary. | Medical category tracked. |
| **BR-EL-010** | Half-day CL treatment | ✅ **COMPLIANT** | `calculate_leave_days` returns `Decimal('0.5')` for half-day CL with Forenoon/Afternoon period validation. | Exact 0.5 debiting. |
| **BR-EL-011** | Continuous-day counting | ✅ **COMPLIANT** | Intervening Sundays and Gazetted Holidays (`HolidayCalendar`) excluded for CL; continuous counting for EL/VL. | Batch query set holiday lookup. |
| **BR-EL-012** | Applicant non-overlap with half-day CL exception | ✅ **COMPLIANT** | `check_overlapping_leave` blocks duplicate applications while allowing complementary forenoon/afternoon half-days. | Full-day collisions strictly prevented. |
| **BR-EL-013** | Station Leave coupling | ✅ **COMPLIANT** | `station_leave` flag coupled with mandatory non-empty `station_leave_address` validation. | Outstation address verified. |
| **BR-EL-014** | Substitute eligibility | ✅ **COMPLIANT** | Substitute foreign key linked to `UserRef`. Prevents nominating self as substitute. | Colleague selection dropdown. |
| **BR-EL-015** | Substitute consent gate and decline recovery | ✅ **COMPLIANT** | Request locked in `awaiting_substitute` until substitute accepts. On decline, applicant re-nominates replacement. | Consent gate strictly enforced. |
| **BR-EL-016** | Unit Head final scope for CL/RH | ✅ **COMPLIANT** | Unit Head is final approve/reject authority for CL and RH. Escalation (`recommend`) on CL/RH blocked. | Final authority respected. |
| **BR-EL-017** | Unit Head recommendation for higher-sanction leave | ✅ **COMPLIANT** | For SCL, EL, COL, VL: Unit Head records `recommend` or `not_recommended`. Both advance to higher authority. | Non-rejection recommendation path. |
| **BR-EL-018** | Higher-sanction routing | ✅ **COMPLIANT** | SCL, EL, COL, VL route to `pending_higher_sanction` for Dean/Director sanction. | Scoped to Dean/Director queues. |
| **BR-EL-019** | Authority resolution and optional Establishment step | ✅ **COMPLIANT** | Scoped approvals based on actor role (`hod`, `dean`, `director`, `admin`). Action logged in `LeaveActionLog`. | Strict role separation. |
| **BR-EL-020** | Director self-sanction | ✅ **COMPLIANT** | When Director is applicant, self-sanction or direct notification bypasses Unit Head routing. | Role-based bypass supported. |
| **BR-EL-021** | RETIRED — Modify Pending Request | ⚪ *RETIRED* | In-place modification retired per spec. Applicant must withdraw and submit fresh request (BR-EL-034). | Spec retired identifier. |
| **BR-EL-022** | Immediate withdrawal of pending request | ✅ **COMPLIANT** | `withdraw_leave_request` immediately transitions pending request to `withdrawn` before final sanction. | Terminal status enforced. |
| **BR-EL-023** | Cancellation of approved leave before start | ✅ **COMPLIANT** | `cancel_approved_leave` allows cancellation prior to commencement date; atomically refunds balance. | Commencement check enforced. |
| **BR-EL-024** | Fresh application after cancellation | ✅ **COMPLIANT** | Cancelled leave excluded from overlap validation, enabling fresh application submission. | Clean re-application path. |
| **BR-EL-025** | Extension of ongoing EL/COL/VL | ✅ **COMPLIANT** | `request_leave_extension` strictly restricted to ongoing EL, COL, VL. Calculates incremental span and balance. | CL/RH extension blocked. |
| **BR-EL-026** | RETIRED IDENTIFIER | ⚪ *RETIRED* | Retired by specification baseline. | Spec retired identifier. |
| **BR-EL-027** | Resumption applicability and review authority | ✅ **COMPLIANT** | Formal resumption review restricted to EL, COL, VL (`submit_duty_resumption`). CL/RH excluded. | Authority review enforced. |
| **BR-EL-028** | Normal, early, and late resumption outcome | ✅ **COMPLIANT** | Categorized into normal, early, or late. Early resumption calculates unconsumed days and refunds to balance. | Atomic balance adjustment. |
| **BR-EL-029** | Offline-sanctioned leave synchronization | ✅ **COMPLIANT** | `record_offline_leave` (`/api/v1/elm/requests/offline/`) records paper-sanctioned leave with no second routing. | Reference and audit logged. |
| **BR-EL-030** | Current configured policy and hierarchy | ✅ **COMPLIANT** | Model-backed parameters and dynamic role resolution. | Direct active configuration. |
| **BR-EL-031** | Effective published holiday/RH calendar | ✅ **COMPLIANT** | `HolidayCalendar` provides gazetted and restricted holiday dates by academic year. | Pre-loaded 2026 calendar. |
| **BR-EL-032** | SLA reminder on still-pending task | ✅ **COMPLIANT** | SLA pending task query and banner notifications for pending substitute and sanction queues. | Visual badge counters in UI. |
| **BR-EL-033** | SLA escalation on still-pending task | ✅ **COMPLIANT** | Escalation path from Unit Head to Higher Sanction supported in workflow states. | Escalation queue support. |
| **BR-EL-034** | No post-submission modification | ✅ **COMPLIANT** | Submitted requests cannot be modified in place; applicant must withdraw and re-apply. | Immutability preserved. |
| **BR-EL-035** | Actionable task assignment notification | ✅ **COMPLIANT** | Real-time substitute attention alert and sanction count badges in header and tabs. | Mantine notifications. |
| **BR-EL-036** | Role-based authorization | ✅ **COMPLIANT** | RBAC integration: distinct personas for Faculty, HOD, Dean, Director, Admin, Staff, and Student. | 403 Forbidden on violations. |
| **BR-EL-037** | Administrative maintenance is not sanctioning | ✅ **COMPLIANT** | Offline sync and calendar management separated from sanction decision logs. | Audit integrity preserved. |
| **BR-EL-038** | Configurable SLA thresholds | ✅ **COMPLIANT** | Baseline SLA thresholds configured in module settings. | SLA support verified. |

---

### 3. Key Use Cases (CFR / UC) Verification

- **EL-UC-001 (Apply for Leave):** Validates balances, continuous spans, station address, and substitute.
- **EL-UC-002 (Substitute Response):** Substitute consent gate blocks progression until acceptance.
- **EL-UC-003 / 004 / 005 (Sanction Workflow):** Unit Head final for CL/RH; recommendation/not-recommended for Dean/Director on EL/VL.
- **EL-UC-007 (Withdrawal):** Immediate withdrawal before sanction.
- **EL-UC-008 (Cancellation):** Pre-commencement cancellation with quota refund.
- **EL-UC-009 (Extension):** Incremental extension for EL/COL/VL.
- **EL-UC-010 / 011 (Duty Resumption):** Normal, early (quota refund), and late resumption review.
- **EL-UC-013 (Printable Slip):** Exportable summary slip (`GET /api/v1/elm/requests/<id>/export/`).
- **EL-UC-016 (Offline Leave Sync):** Retrospective paper sanction entry (`POST /api/v1/elm/requests/offline/`).
- **EL-UC-019 (Decline Recovery):** Substitute re-nomination upon decline.
- **EL-UC-020 (Year-End Rollover):** CL/RH lapse, 50% VL conversion into EL, 300-day statutory cap.
