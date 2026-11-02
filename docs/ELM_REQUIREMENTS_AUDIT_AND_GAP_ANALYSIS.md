# Employee Leave Management (ELM): Comprehensive Requirements Audit & Gap Analysis
## Phase 1 & Phase 2 Codebase Audit against Synchronized Baseline v1.4

### 1. Executive Audit Summary
* **Total Business Rules Evaluated:** 38 (BR-EL-001 to BR-EL-038)
* **Fully Compliant (Implemented & Verified):** 10
* **Partially Implemented (Basic form present, edge cases missing):** 12
* **Completely Missing (Specification Gaps):** 14
* **Retired Identifiers:** 2

---

### 2. Comprehensive Business Rules Traceability & Gap Matrix

| Rule ID | Rule Title | Audit Status | Current Implementation in Repo | Identified Missing Specification / Gap | Priority |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **BR-EL-001** | Supported leave-category eligibility | ✅ **COMPLIANT** | LeaveType model defines CL, RH, SCL, EL, VL, COL. Validated in serializer & service. | None for basic submission; eligibility by staff kind (faculty vs staff) can be enhanced in validation. | **Low** |
| **BR-EL-002** | Casual Leave entitlement and lapse | ⚠️ **PARTIAL** | CL annual quota (8 days) credited in LeaveBalance. | Year-end lapse mechanism (unconsumed CL cannot carry forward to next year) needs automated year-end job. | **Medium** |
| **BR-EL-003** | Restricted Holiday entitlement and applicability | ❌ **MISSING** | RH is a leave type with quota (2 days). | Must validate requested date against published Restricted Holiday Calendar (HolidayCalendar model missing). | **High** |
| **BR-EL-004** | Special Casual Leave entitlement and admissibility | ⚠️ **PARTIAL** | SCL leave type supported in models and serializers. | Requires purpose admissibility validation and higher sanction approval workflow routing. | **Medium** |
| **BR-EL-005** | Non-faculty Earned Leave credit and carry-forward | ⚠️ **PARTIAL** | EL balance tracked per user. | Max accumulation ceiling (typically 300 days) and semi-annual credit rules not yet implemented. | **Medium** |
| **BR-EL-006** | Faculty Vacation Leave entitlement and vacation-period applicability | ❌ **MISSING** | VL leave type with is_vacation=True. | Must validate that VL dates fall strictly within declared Institute Summer/Winter vacation windows. | **High** |
| **BR-EL-007** | VL-to-EL year-end conversion | ❌ **MISSING** | None. | 50% unconsumed VL conversion into EL at end of calendar year (e.g. 30 unavailed VL -> 15 EL credited) missing. | **High** |
| **BR-EL-008** | Treatment of EL created by VL conversion | ❌ **MISSING** | None. | Tracking converted EL and applying carry-forward limits. | **Medium** |
| **BR-EL-009** | Commuted Leave entitlement and treatment | ⚠️ **PARTIAL** | COL leave type defined. | Medical certificate requirement flag and half-pay leave debit ratio (2 days HPL per 1 day COL) not enforced. | **Medium** |
| **BR-EL-010** | Half-day CL treatment | ✅ **COMPLIANT** | calculate_leave_days returns Decimal('0.5') for half-day CL with Forenoon/Afternoon period validation. | None. | **None** |
| **BR-EL-011** | Continuous-day counting | ⚠️ **PARTIAL** | calculate_leave_days calculates calendar days: (end_date - start_date).days + 1. | Intervening Sundays/Gazetted holidays should not count against CL balance, but DO count for EL continuous leaves. | **High** |
| **BR-EL-012** | Applicant non-overlap with half-day CL exception | ✅ **COMPLIANT** | check_overlapping_leave enforces strict date non-overlap while permitting non-colliding half-day periods. | None. | **None** |
| **BR-EL-013** | Station Leave coupling | ⚠️ **PARTIAL** | station_leave (bool) and station_leave_address (text) captured in model and serializer. | Station leave address mandatory validation when station_leave is True; station leave permission auto-coupling. | **Medium** |
| **BR-EL-014** | Substitute eligibility | ⚠️ **PARTIAL** | substitute foreign key linked to UserRef. | Substitute cannot be self, must belong to compatible discipline/department, and cannot have approved leave on same period. | **Medium** |
| **BR-EL-015** | Substitute consent gate and decline recovery | ⚠️ **PARTIAL** | substitute accept sets status to pending_unit_head/approved. | Substitute decline recovery: allow applicant to re-nominate an alternate substitute (EL-UC-019). | **High** |
| **BR-EL-016** | Unit Head final scope for CL/RH | ✅ **COMPLIANT** | Unit Head can approve CL and RH directly without routing to higher authority. | None. | **None** |
| **BR-EL-017** | Unit Head recommendation for higher-sanction leave | ✅ **COMPLIANT** | Unit head action='recommend' sets status to 'pending_higher_sanction'. | None. | **None** |
| **BR-EL-018** | Higher-sanction routing | ⚠️ **PARTIAL** | status supports pending_higher_sanction. | Routing to Dean / Director based on leave duration (>15 days EL requires Director sanction). | **Medium** |
| **BR-EL-019** | Authority resolution and optional Establishment step | ⚠️ **PARTIAL** | Role-based action recorded in LeaveActionLog. | Establishment section verification step for EL/COL leave balance certification. | **Low** |
| **BR-EL-020** | Director self-sanction | ❌ **MISSING** | None. | Director applicant bypasses Unit Head review directly into approved state with intimation logging. | **Medium** |
| **BR-EL-021** | RETIRED — Modify Pending Request | ⚪ *RETIRED* | N/A (Retired by spec). | None. | **None** |
| **BR-EL-022** | Immediate withdrawal of pending request | ✅ **COMPLIANT** | withdraw_leave_request immediately transitions pending request to 'withdrawn' and logs action. | None. | **None** |
| **BR-EL-023** | Cancellation of approved leave before start | ❌ **MISSING** | None. | Applicant can request cancellation of approved leave before start_date; restores deducted leave balance. | **High** |
| **BR-EL-024** | Fresh application after cancellation | ✅ **COMPLIANT** | Cancelled leave is excluded from overlap validation, allowing new application. | None. | **None** |
| **BR-EL-025** | Extension of ongoing EL/COL/VL | ❌ **MISSING** | None. | Request extension of an ongoing approved leave, chaining start_date to previous end_date + 1 day. | **High** |
| **BR-EL-026** | RETIRED IDENTIFIER | ⚪ *RETIRED* | N/A (Retired by spec). | None. | **None** |
| **BR-EL-027** | Resumption applicability and review authority | ❌ **MISSING** | None. | Mandatory resumption of duty submission for long leaves (EL/VL/COL). | **High** |
| **BR-EL-028** | Normal, early, and late resumption outcome | ❌ **MISSING** | None. | Early resumption must credit back unconsumed days to LeaveBalance; late resumption requires extension check. | **High** |
| **BR-EL-029** | Offline-sanctioned leave synchronization | ❌ **MISSING** | None. | Establishment operator endpoint to record leave sanctioned on paper files. | **Low** |
| **BR-EL-030** | Current configured policy and hierarchy | ⚠️ **PARTIAL** | LeaveType model holds quotas. | Dynamic policy configuration interface. | **Low** |
| **BR-EL-031** | Effective published holiday/RH calendar | ❌ **MISSING** | None. | Model HolidayCalendar to store Gazetted Holidays and Restricted Holidays per academic year. | **High** |
| **BR-EL-032** | SLA reminder on still-pending task | ❌ **MISSING** | None. | Automated Celery task or command sending reminder if pending > 3 days. | **Medium** |
| **BR-EL-033** | SLA escalation on still-pending task | ❌ **MISSING** | None. | Automated escalation to next level if pending > SLA threshold. | **Low** |
| **BR-EL-034** | No post-submission modification | ✅ **COMPLIANT** | Leave requests cannot be edited in-place; must withdraw or cancel and re-apply. | None. | **None** |
| **BR-EL-035** | Actionable task assignment notification | ⚠️ **PARTIAL** | Status indicators on dashboard. | Notification badges / emails. | **Low** |
| **BR-EL-036** | Role-based authorization | ✅ **COMPLIANT** | IAM Principal with active_role and permissions integrated. | None. | **None** |
| **BR-EL-037** | Administrative maintenance is not sanctioning | ✅ **COMPLIANT** | Clear separation between LeaveActionLog roles. | None. | **None** |
| **BR-EL-038** | Configurable SLA thresholds | ❌ **MISSING** | None. | Config table for SLA thresholds. | **Low** |

---

### 3. High-Priority Defect & Gap Clustering (Actionable Engineering Roadmap)

To achieve full production readiness without overloading local LLM context windows, the missing requirements are organized into **5 Atomic Sprints**:

#### **Sprint 1: Holiday & Calendar Awareness (`BR-EL-003`, `BR-EL-011`, `BR-EL-031`)**
* **Domain Gap:** Continuous counting currently counts all calendar days. Intervening Sundays and Gazetted Holidays should NOT be debited from Casual Leave (CL).
* **Missing Models:** `HolidayCalendar` (date, name, is_restricted, academic_year).
* **Validation Gap:** Restricted Holiday (RH) applications must strictly validate that the requested date is declared in `HolidayCalendar` with `is_restricted=True`.

#### **Sprint 2: Substitute Decline Recovery & Re-Nomination (`BR-EL-014`, `BR-EL-015`, `EL-UC-019`)**
* **Domain Gap:** If a nominee declines, the request currently remains blocked. The applicant must be able to nominate an alternate eligible substitute.
* **Eligibility Check:** Substitute cannot be self, cannot have conflicting leave, and must belong to active directory users.

#### **Sprint 3: Cancellation & Extension Lifecycle (`BR-EL-023`, `BR-EL-025`, `EL-UC-008`, `EL-UC-009`)**
* **Cancellation Before Start:** Applicant can cancel an approved leave before `start_date`. The system automatically reimburses/refunds the debited days back to `LeaveBalance`.
* **Leave Extension:** Applicant with an ongoing approved EL/VL/COL can request an extension. Extension must chain directly to `previous.end_date + 1 day`.

#### **Sprint 4: Resumption of Duty Workflow (`BR-EL-027`, `BR-EL-028`, `EL-UC-010`, `EL-UC-011`)**
* **Domain Gap:** Mandatory for long leaves (EL, VL, COL). Applicant must submit Resumption of Duty upon return.
* **Early Resumption:** If employee resumes duty earlier than `end_date`, unconsumed leave days are recalculated and credited back to `LeaveBalance`.
* **Missing Model:** `DutyResumption` (leave_request, actual_resumption_date, remarks, approved_by, status).

#### **Sprint 5: Year-End VL-to-EL Rollover (`BR-EL-006`, `BR-EL-007`, `BR-EL-008`, `EL-UC-020`)**
* **Domain Gap:** Faculty Vacation Leave (VL) is eligible for 50% conversion of unconsumed days into Earned Leave (EL) at year-end.
* **Calculation Rule:** `credited_el = floor(unconsumed_vl / 2)`. Unconsumed CL lapses entirely.
* **Engineering Target:** Standalone idempotent management command `process_year_end_leaves`.

---

### 4. Implementation Protocol for Qwen 2.5 Coder (No Code Spoon-Feeding)
Every sprint prompt will follow the strict rule: **Specification & Rules Only, No Solution Code**:
1. State the exact Business Rule statements and Acceptance Criteria.
2. State the pre-conditions, post-conditions, and entity relations.
3. Prompt Qwen to reason, design the data models/methods, and generate the production implementation independently.
4. Verify generated code via automated test suite before committing to Git.