# Fusion ERP – File Tracking System (FTS)
# Use Case Specifications — Final v1.3

| Project | Fusion ERP |
| :--- | :--- |
| **Module Code** | FTS |
| **Module** | File Tracking System (FTS) |
| **Artifact** | Use Case Specifications |
| **Version** | v1.3 |
| **Date** | 2026-08-30 |
| **Basis** | v1.2 synchronized baseline + DIRECT_FINAL_v2 capsule |
| **Status** | FINAL |
| **Active Use Cases** | 10 |
| **Retired Legacy Use Cases** | 1 |
| **UC Trigger Types** | All active UCs are Actor-triggered; no separate SF artifact is used |

---

### 1. Use Case Index

| UC ID | Name | UC Type | Primary Actor | Related Workflow(s) |
| :--- | :--- | :--- | :--- | :--- |
| **FTS-UC-001** | Create New File | Actor-triggered | Institute Employee | BW-FTS-05, BW-FTS-06, BW-FTS-07, BW-FTS-08, CW-FTS-02 |
| **FTS-UC-002** | Edit or Discard Draft File | Actor-triggered | Institute Employee | BW-FTS-06, BW-FTS-07, BW-FTS-08, CW-FTS-02 |
| **FTS-UC-003** | Send / Forward File to Employee | Actor-triggered | Institute Employee (Sender / Current Holder) | BW-FTS-01, BW-FTS-02, BW-FTS-05, BW-FTS-06, CW-FTS-01, CW-FTS-02 |
| **FTS-UC-004** | Return Received File | Actor-triggered | Institute Employee (Recipient / Current Holder) | BW-FTS-03, CW-FTS-01 |
| **FTS-UC-005** | View Inbox, Outbox, and Open Files | Actor-triggered | Institute Employee | N/A |
| **FTS-UC-006** | View File Tracking History | Actor-triggered | Institute Employee | N/A |
| **FTS-UC-007** | Archive Completed File | Actor-triggered | Institute Employee / File Owner | BW-FTS-04, CW-FTS-01 |
| **FTS-UC-008** | Select Assigned Role Context for FTS | Actor-triggered | Institute Employee | N/A |
| **FTS-UC-009** | Administer FTS User Access Context | Actor-triggered | System Admin | N/A |
| **FTS-UC-010** | Use FTS Workflow-Support APIs | Actor-triggered | Authorized Consuming Fusion Module | N/A |

*Note: Notification, audit, and history-maintenance effects remain subordinate system behavior within the triggering actor services and BRs; they are not promoted into synthetic standalone UCs.*

---

### 2. Detailed Use Case Specifications

#### FTS-UC-001 — Create New File
* **Primary Actor:** Institute Employee
* **Goal / Description:** Create a new FTS file under an assigned role with the required initial comment and optional attachments, leaving a valid pre-circulation file that may be retained as a draft or subsequently sent through FTS-UC-003.
* **Trigger:** Employee selects Create File from the Fusion/FTS interface.
* **Preconditions:** Employee is authenticated, has an assigned role context, and is authorized to create files.
* **Main Success Scenario:**
  1. Employee opens the file-creation function.
  2. Employee enters the initial mandatory comment.
  3. Employee optionally adds attachments.
  4. Employee saves the created file as a draft/pre-circulation file.
  5. FTS validates the required comment, persists the file object and records creation/comment/attachment audit information.
* **Alternative Flows:**
  - If employee chooses immediate circulation instead of retaining draft, proceeds directly to FTS-UC-003.
  - If no attachment is supplied, creation proceeds (attachments are optional).
* **Exception Flows:**
  - If initial comment is missing, FTS blocks save.
  - If selected role is not authorized, FTS denies action.
* **Success Postcondition:** Valid file exists in draft/pre-circulation state with initial comment and attachments preserved.
* **Related Business Rules:** BR-FTS-001, BR-FTS-003, BR-FTS-004, BR-FTS-005, BR-FTS-010, BR-FTS-011.

#### FTS-UC-002 — Edit or Discard Draft File
* **Primary Actor:** Institute Employee
* **Goal / Description:** Edit a saved draft before circulation or discard that draft before submission.
* **Trigger:** Employee opens an existing draft file.
* **Preconditions:** File exists as a draft/pre-circulation file and employee is authorized to edit it.
* **Main Success Scenario (Edit):**
  1. Employee opens an authorized draft.
  2. Employee edits draft comment and/or attachments.
  3. Employee saves updated draft.
  4. FTS persists updates and records audit/version info.
* **Alternative Flow (Discard):** Employee chooses Discard instead of Save; FTS removes the draft because it has not yet been submitted/circulated.
* **Exception Flows:**
  - If file has already been submitted/circulated, FTS denies discard.
  - If employee is not authorized for the draft, FTS denies access.
* **Success Postcondition:** Draft is either updated and retained or discarded before circulation.
* **Related Business Rules:** BR-FTS-005, BR-FTS-010, BR-FTS-011.

#### FTS-UC-003 — Send / Forward File to Employee
* **Primary Actor:** Institute Employee (Sender / Current Holder)
* **Supporting Actor:** Recipient Institute Employee
* **Goal / Description:** Send an active file to another Institute Employee, including initial circulation or onward forwarding of a received file.
* **Trigger:** Authorized employee selects Send/Forward on an actionable file.
* **Preconditions:** File exists and is not archived; sender is authorized to act; valid recipient Institute Employee is selected.
* **Main Success Scenario:**
  1. Sender opens actionable file and selects a recipient Institute Employee.
  2. Sender enters mandatory movement comment.
  3. Sender optionally adds attachments for this movement stage.
  4. Sender confirms Send/Forward.
  5. FTS validates authorization, file state, recipient, and mandatory comment.
  6. FTS records sender, receiver, timestamp, movement comment, and attachments chronologically; updates current holder/pending recipient; records audit/version info.
  7. FTS triggers file-forwarded/file-received notification events.
* **Exception Flows:**
  - Missing mandatory movement comment: forwarding blocked.
  - Invalid recipient: forwarding blocked.
  - Unauthorized action or archived file: forwarding blocked.
* **Success Postcondition:** File remains active/circulated and is held by recipient; history/audit updated; notifications triggered.
* **Related Business Rules:** BR-FTS-001, BR-FTS-003, BR-FTS-005, BR-FTS-006, BR-FTS-007, BR-FTS-008, BR-FTS-010, BR-FTS-011, BR-FTS-012, BR-FTS-013.

#### FTS-UC-004 — Return Received File
* **Primary Actor:** Institute Employee (Recipient / Current Holder)
* **Supporting Actor:** Previous Sender Institute Employee
* **Goal / Description:** Return an active received file to its sender with the required movement comment and optional attachment.
* **Trigger:** Recipient selects Return on a received actionable file.
* **Preconditions:** File is active, associated with recipient, has known sender for current movement, recipient authorized.
* **Main Success Scenario:**
  1. Recipient opens received file and selects Return.
  2. Recipient enters mandatory movement comment.
  3. Recipient optionally adds attachments for this movement stage.
  4. Recipient confirms Return.
  5. FTS validates authorization, active file state, and mandatory comment.
  6. FTS records return chronologically; updates current holder to previous sender; records audit/version info.
  7. FTS triggers file-returned notification event.
* **Exception Flows:**
  - Missing mandatory movement comment: return blocked.
  - Unauthorized action or archived file: return blocked.
* **Success Postcondition:** File returned to previous sender; history/audit updated; notification triggered.
* **Related Business Rules:** BR-FTS-006, BR-FTS-007, BR-FTS-008, BR-FTS-010, BR-FTS-011, BR-FTS-012, BR-FTS-013.

#### FTS-UC-005 — View Inbox, Outbox, and Open Files
* **Primary Actor:** Institute Employee
* **Goal / Description:** View received and sent files and open files the employee is authorized to access.
* **Trigger:** Employee opens Inbox or Outbox.
* **Preconditions:** Employee is authenticated in an FTS role context.
* **Main Success Scenario:**
  1. Employee opens Inbox or Outbox.
  2. FTS lists received files in Inbox and sent files in Outbox, subject to authorization.
  3. Employee selects an authorized file.
  4. FTS displays file contents, comments, attachments, status, and permitted actions.
* **Alternative Flow:** Archived file is displayed as read-only.
* **Exception Flows:**
  - Unauthorized file: FTS denies access.
* **Success Postcondition:** File information displayed; viewing alone does not change business state.
* **Related Business Rules:** BR-FTS-009, BR-FTS-010, BR-FTS-012.

#### FTS-UC-006 — View File Tracking History
* **Primary Actor:** Institute Employee
* **Goal / Description:** View complete chronological tracking history of an authorized associated file.
* **Trigger:** Employee selects View History for a file.
* **Preconditions:** File exists and employee is authorized/associated with it.
* **Main Success Scenario:**
  1. Employee selects an associated file and requests tracking history.
  2. FTS retrieves chronological history from creation onward.
  3. FTS displays movement events with sender, receiver, timestamp, comments, and attachments.
* **Exception Flows:** Unauthorized access denied.
* **Success Postcondition:** Tracking history displayed without state change.
* **Related Business Rules:** BR-FTS-008, BR-FTS-010, BR-FTS-011.

#### FTS-UC-007 — Archive Completed File
* **Primary Actor:** Institute Employee / File Owner
* **Supporting Actor:** Associated Institute Employees
* **Goal / Description:** Archive a completed circulated file as its owner, ending collaborative movement while retaining permanent read access for authorized users.
* **Trigger:** File owner selects Archive after intended collaborative objective is complete.
* **Preconditions:** File has been circulated, is not already archived, actor is file owner, objective complete.
* **Main Success Scenario:**
  1. Owner opens active circulated file and selects Archive.
  2. FTS verifies ownership and authorization.
  3. FTS changes file to Archived / Read-only state.
  4. FTS prevents subsequent modification and forwarding, while retaining permanent read access.
  5. FTS records archival audit/version event and triggers file-archived notification event.
* **Exception Flows:**
  - Non-owner archival attempt denied.
  - Already archived: presents existing read-only state.
* **Success Postcondition:** File is Archived / Read-only, permanently retained for reading, closed to movement.
* **Related Business Rules:** BR-FTS-009, BR-FTS-010, BR-FTS-011, BR-FTS-012, BR-FTS-013.

#### FTS-UC-008 — Select Assigned Role Context for FTS
* **Primary Actor:** Institute Employee
* **Supporting Actor:** Fusion dashboard / role context service
* **Goal / Description:** Use FTS under a selected assigned institutional role without changing existing file ownership or historical audit identity.
* **Trigger:** Employee switches or selects assigned role context.
* **Preconditions:** Employee has at least one assigned role.
* **Main Success Scenario:**
  1. Employee selects assigned role context through Fusion.
  2. FTS applies selected role context to determine permitted access/actions.
  3. FTS preserves existing file ownership and previously recorded audit history across switch.
* **Success Postcondition:** Selected role context governs subsequent FTS authorization; existing ownership and history unchanged.
* **Related Business Rules:** BR-FTS-002, BR-FTS-010.

#### FTS-UC-009 — Administer FTS User Access Context
* **Primary Actor:** System Admin
* **Supporting Actor:** Institute Employee; Fusion identity services
* **Goal / Description:** Administer role/access context used by FTS and perform governance oversight without participating in operational file processing.
* **Trigger:** System Admin opens FTS/Fusion governance function.
* **Preconditions:** System Admin has administrative privileges.
* **Main Success Scenario:**
  1. System Admin assigns/reassigns FTS roles or reviews FTS usage/security/audit logs.
  2. FTS applies role/access context for authorization and triggers role assignment notifications.
  3. System Admin does not create, forward, return, comment on, or archive operational files.
* **Exception Flows:** Operational file action attempted by System Admin is denied.
* **Success Postcondition:** FTS governance context updated; operational file processing remains with employees.
* **Related Business Rules:** BR-FTS-001, BR-FTS-010, BR-FTS-011, BR-FTS-013.

#### FTS-UC-010 — Use FTS Workflow-Support APIs
* **Primary Actor:** Authorized Consuming Fusion Module
* **Supporting Actor:** Fusion identity/RBAC and audit context
* **Goal / Description:** Invoke FTS-supported file/workflow tracking APIs for a consuming Fusion module while keeping domain-specific approval policy in the consuming module.
* **Trigger:** Authorized consuming module invokes FTS API.
* **Main Success Scenario:**
  1. Consuming module calls FTS API for workflow support, approval-chain support, or request tracking.
  2. FTS validates authorization and RBAC context.
  3. FTS performs file/workflow tracking service within FTS boundary and logs audit record.
  4. FTS returns service response to consuming module.
* **Exception Flows:** Consuming module domain-specific approval rules are not defined by FTS.
* **Success Postcondition:** Authorized FTS service operation completed and audited.
* **Related Business Rules:** BR-FTS-010, BR-FTS-011, BR-FTS-014.

---

### Appendix A — Retired Legacy Use Case
**FTS-UC-011 (Receive FTS Notifications)** remains retired. Its prior content is represented as cross-cutting notification effects of source actor UCs plus BR-FTS-013.
