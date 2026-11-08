# Fusion ERP – File Tracking System (FTS)
# Workflow Specifications — Final v1.3

| Project | Fusion ERP |
| :--- | :--- |
| **Module Code** | FTS |
| **Module** | File Tracking System (FTS) |
| **Artifact** | Workflow Specifications |
| **Version** | v1.3 |
| **Date** | 2026-08-30 |
| **Basis** | v1.2 synchronized baseline + DIRECT_FINAL_v2 capsule |
| **Status** | FINAL |
| **Basis Workflows** | 8 |
| **Composite Workflows** | 2 |
| **Complete Workflow** | Not forced |

---

### 1. Workflow Re-derivation Note
DIRECT_FINAL_v2 defines a workflow by meaningful connected progression through business states, not by a minimum actor count. Therefore the prior v1.2 exclusion of state-changing new-file/draft progression is no longer justified. Existing BW-FTS-01..04 and CW-FTS-01 IDs are retained; new BW-FTS-05..08 and CW-FTS-02 are appended. Informational viewing UCs, generic API handoff, and role-context/governance operations remain outside the WF layer because the baseline does not define a necessary connected business-state progression for them.

---

### 2. Legacy Workflow Disposition

| Legacy WF | Final Disposition | Replacement | Reason |
| :--- | :--- | :--- | :--- |
| **FTS-WF-001** | Reconstructed | BW-FTS-05..08; CW-FTS-02 | Recognizes connected Draft → Edit/Discard/Circulate progression. |
| **FTS-WF-002** | Reconstructed | BW-FTS-01, BW-FTS-02; CW-FTS-01 | Forwarding remains explicit holder-state progression. |
| **FTS-WF-003** | Reconstructed | BW-FTS-03; CW-FTS-01 | Return remains an explicit state transition to previous sender. |
| **FTS-WF-004** | Retired | N/A | Inbox/Outbox viewing is informational; does not change state. |
| **FTS-WF-005** | Retired | N/A | History viewing is informational. |
| **FTS-WF-006** | Reconstructed | BW-FTS-04; CW-FTS-01 | Archival is a lifecycle-closing transition. |
| **FTS-WF-007** | Retired | N/A | Role selection does not form a connected file progression. |
| **FTS-WF-008** | Retired | N/A | Generic API handoff does not define a persistent FTS state progression. |

---

### 3. Workflow Registry

| WF ID | Workflow Name | Type | Participants | Constituent Workflows |
| :--- | :--- | :--- | :--- | :--- |
| **BW-FTS-01** | Forward File to Recipient — Zero Onward Traversal | Basis | Sender; Recipient | N/A |
| **BW-FTS-02** | Onward Forwarding — One Loop Traversal | Basis | Current Holder; Next Recipient | N/A |
| **BW-FTS-03** | Return File to Previous Sender | Basis | Current Recipient; Previous Sender | N/A |
| **BW-FTS-04** | Archive Completed Circulated File | Basis | File Owner; Affected Employees | N/A |
| **BW-FTS-05** | Prepare and Circulate New File — Zero Draft-Edit Traversal | Basis | Creator/Sender; Recipient | N/A |
| **BW-FTS-06** | Prepare and Circulate New File — One Draft-Edit Traversal | Basis | Creator/Sender; Recipient | N/A |
| **BW-FTS-07** | Create and Discard Draft — Zero Draft-Edit Traversal | Basis | Creator | N/A |
| **BW-FTS-08** | Edit Once and Discard Draft — One Draft-Edit Traversal | Basis | Creator | N/A |
| **CW-FTS-01** | Collaborative File Circulation and Completion | Composite | Sender, Current Holder, Previous Sender, File Owner | BW-FTS-01, 02, 03, 04 |
| **CW-FTS-02** | New File Preparation and Initial Outcome | Composite | Creator/Sender; Recipient | BW-FTS-05, 06, 07, 08 |

---

### 4. Canonical Workflow Specifications

#### BW-FTS-01 — Forward File to Recipient — Zero Onward Traversal
* **Type:** Basis
* **Trigger:** Authorized current holder chooses Send/Forward.
* **Participants:** Institute Employee (Sender); Recipient Institute Employee.
* **Authoritative State-Transition:**
  - *From State:* Prepared/Draft or Active file held by Sender
  - *Actor:* Institute Employee (Sender)
  - *Use Case:* FTS-UC-003 (Send / Forward File to Employee)
  - *Guard / Outcome:* Sender authorized; file not archived; valid Institute Employee recipient; mandatory movement comment present. Movement/history/audit updated; notification event triggered.
  - *Resulting State:* **Active / Circulated file held by Recipient**
  - *BR References:* BR-FTS-001, 005, 006, 007, 008, 010, 011, 012, 013.

#### BW-FTS-02 — Onward Forwarding — One Loop Traversal
* **Type:** Basis
* **Trigger:** Current recipient chooses to forward received file onward.
* **Participants:** Current Holder; Next Recipient.
* **Authoritative State-Transition:**
  - *From State:* Active / Circulated file held by Current Recipient
  - *Actor:* Current Holder
  - *Use Case:* FTS-UC-003 (Send / Forward File to Employee)
  - *Guard / Outcome:* Current holder authorized; file not archived; valid next recipient; mandatory comment present. Movement/history/audit updated; notification triggered.
  - *Resulting State:* **Active / Circulated file held by Next Recipient**
  - *BR References:* BR-FTS-001, 006, 007, 008, 010, 011, 012, 013.

#### BW-FTS-03 — Return File to Previous Sender
* **Type:** Basis
* **Trigger:** Current recipient chooses Return.
* **Participants:** Current Recipient; Previous Sender.
* **Authoritative State-Transition:**
  - *From State:* Active / Circulated file held by Recipient; previous sender known
  - *Actor:* Recipient
  - *Use Case:* FTS-UC-004 (Return Received File)
  - *Guard / Outcome:* Recipient authorized; active file; mandatory comment present. Return/history/audit updated; return notification triggered.
  - *Resulting State:* **Active / Circulated file held by Previous Sender**
  - *BR References:* BR-FTS-006, 007, 008, 010, 011, 012, 013.

#### BW-FTS-04 — Archive Completed Circulated File
* **Type:** Basis
* **Trigger:** File owner selects Archive after collaborative objective complete.
* **Participants:** File Owner; Affected Users.
* **Authoritative State-Transition:**
  - *From State:* Active / Circulated file; objective complete
  - *Actor:* File Owner
  - *Use Case:* FTS-UC-007 (Archive Completed File)
  - *Guard / Outcome:* Requester is file owner; file not already archived; objective complete. Archive/audit recorded; archive notification triggered.
  - *Resulting State:* **Archived / Read-only / Permanently retained**
  - *BR References:* BR-FTS-009, 010, 011, 012, 013.

#### BW-FTS-05 — Prepare and Circulate New File — Zero Draft-Edit Traversal
* **Type:** Basis
* **State Progression:**
  1. *[No FTS record]* → `FTS-UC-001 Create New File` (Creator, mandatory initial comment) → **Draft / Pre-circulation file**
  2. *[Draft file]* → `FTS-UC-003 Send / Forward File` (Sender, valid recipient, mandatory comment) → **Active / Circulated file held by Recipient**

#### BW-FTS-06 — Prepare and Circulate New File — One Draft-Edit Traversal
* **Type:** Basis
* **State Progression:**
  1. *[No FTS record]* → `FTS-UC-001 Create New File` → **Draft / Pre-circulation file**
  2. *[Draft file]* → `FTS-UC-002 Edit Draft File` (Creator edits and saves) → **Updated Draft / Pre-circulation file**
  3. *[Updated Draft file]* → `FTS-UC-003 Send / Forward File` → **Active / Circulated file held by Recipient**

#### BW-FTS-07 — Create and Discard Draft — Zero Draft-Edit Traversal
* **Type:** Basis
* **State Progression:**
  1. *[No FTS record]* → `FTS-UC-001 Create New File` → **Draft / Pre-circulation file**
  2. *[Draft file]* → `FTS-UC-002 Discard Draft` (Creator chooses Discard) → **Discarded / No active file retained**

#### BW-FTS-08 — Edit Once and Discard Draft — One Draft-Edit Traversal
* **Type:** Basis
* **State Progression:**
  1. *[No FTS record]* → `FTS-UC-001 Create New File` → **Draft / Pre-circulation file**
  2. *[Draft file]* → `FTS-UC-002 Edit Draft` → **Updated Draft / Pre-circulation file**
  3. *[Updated Draft file]* → `FTS-UC-002 Discard Draft` → **Discarded / No active file retained**

---

### 5. Composite Workflows

#### CW-FTS-01 — Collaborative File Circulation and Completion
Combines initial send (`BW-FTS-01`), onward forwarding (`BW-FTS-02`), return (`BW-FTS-03`), and owner archival (`BW-FTS-04`).

#### CW-FTS-02 — New File Preparation and Initial Outcome
Integrates file creation (`FTS-UC-001`), draft editing/discard (`FTS-UC-002`), and initial submission into circulation (`FTS-UC-003`).

---

### 6. Workflow Layer Exclusions
Informational use cases (`FTS-UC-005` view inbox/outbox, `FTS-UC-006` view tracking history), role context selection (`FTS-UC-008`), administration (`FTS-UC-009`), and generic API handoff (`FTS-UC-010`) remain valid UCs without forced standalone workflow mappings.
