# File Tracking System (FTS) — Specification Bundle Index
## Fusion ERP Module: File Tracking System (FTS)

This directory contains the canonical synchronized requirements and design specifications for the **File Tracking System (FTS)** module in Fusion ERP.

---

### Artifact Index

| File | Artifact Title | Version | Scope / Purpose |
| :--- | :--- | :---: | :--- |
| [`01_FTS_Problem_Statement_v1.2.md`](file:///C:/Fusion/Fusion-Integrated/docs/fts/01_FTS_Problem_Statement_v1.2.md) | **Problem Statement** | v1.2 | Domain overview, Institute Employee vs System Admin actors, operational boundaries. |
| [`02_FTS_Two_Level_Requirement_Registry_CFR_AFR_v1.3_FINAL.md`](file:///C:/Fusion/Fusion-Integrated/docs/fts/02_FTS_Two_Level_Requirement_Registry_CFR_AFR_v1.3_FINAL.md) | **Two-Level Requirements Registry** | v1.3 | 12 Coherent Functional Requirements (CFRs) decomposed into 72 Atomic Functional Requirements (AFRs). |
| [`03_FTS_Use_Case_Specifications_v1.3_FINAL.md`](file:///C:/Fusion/Fusion-Integrated/docs/fts/03_FTS_Use_Case_Specifications_v1.3_FINAL.md) | **Use Case Specifications** | v1.3 | 10 actor-triggered use cases (`FTS-UC-001` to `FTS-UC-010`) covering creation, circulation, return, and archival. |
| [`04_FTS_Business_Rule_Specifications_v1.3_FINAL.md`](file:///C:/Fusion/Fusion-Integrated/docs/fts/04_FTS_Business_Rule_Specifications_v1.3_FINAL.md) | **Business Rule Specifications** | v1.3 | 14 core business rules (`BR-FTS-001` to `BR-FTS-014`) governing persistence, comments, movements, and RBAC. |
| [`06_FTS_Workflow_Specifications_v1.3_FINAL.md`](file:///C:/Fusion/Fusion-Integrated/docs/fts/06_FTS_Workflow_Specifications_v1.3_FINAL.md) | **Workflow Specifications** | v1.3 | 8 Basis Workflows (`BW-FTS-01..08`) and 2 Composite Workflows (`CW-FTS-01`, `CW-FTS-02`). |

---

### Key Domain Principles & Constraints

1. **Persistent Composite Object (`BR-FTS-003`):**
   - An FTS file consists of metadata, an owner, a current holder, mandatory movement comments, and optional file attachments.
   - Once submitted into circulation, file contents and history are strictly append-only and cannot be deleted.

2. **Draft Boundary (`BR-FTS-005`):**
   - Pre-submission drafts may be saved, edited, or discarded.
   - Once circulated, draft-discard behavior is permanently disabled.

3. **Mandatory Movement Comments (`BR-FTS-004`, `BR-FTS-006`):**
   - Every file creation requires an initial mandatory comment.
   - Every forwarding or return action requires a mandatory movement comment from the acting user.

4. **Universal Routing & Return (`BR-FTS-007`):**
   - A file may be sent to any Institute Employee regardless of role.
   - A received file can be returned directly to the sender of that movement.

5. **Owner-Only Archival (`BR-FTS-012`):**
   - Only the original file owner can archive a circulated file upon completion of its collaborative objective.
   - Archived files remain permanently stored and readable, but modifiable/forwardable actions are locked.
