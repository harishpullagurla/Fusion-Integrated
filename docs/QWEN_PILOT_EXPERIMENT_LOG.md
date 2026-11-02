# Fusion ERP Lab — Assignment #6: Pilot Study Experiment Log
## Model: Qwen 2.5 Coder 7B (via Ollama Local)

### 1. Hardware & Runtime Configuration
| Property | Value |
| :--- | :--- |
| **Operating System** | Microsoft Windows 11 Home Single Language (64-bit) |
| **CPU** | 12th Gen Intel(R) Core(TM) i5-12450H (8 Cores, 12 Threads) |
| **RAM** | 16 GB DDR4 |
| **GPU / VRAM** | NVIDIA GeForce RTX 2050 (4 GB VRAM) & Intel UHD Graphics |
| **Local Runtime** | Ollama (Runner: llama.cpp, CPU Mode / num_gpu: 0) |
| **Model Name & Tag** | `qwen2.5-coder:7b` |
| **Model Size** | 4.7 GB (Q4_K_M GGUF quantization) |
| **Context Window Config** | 4096 tokens (CPU inference) |
| **Clean Fusion Repository** | `https://github.com/FusionIIIT/Fusion-Integrated` (Cloned at commit `02b01fe`) |
| **Specification Source** | `ELM_Specifications_Bundle_v1.4_FINAL (1)` |

---

### 2. Experiment Plan & Staged Prompting Strategy
To avoid token overflow and optimize inference latency on the local laptop hardware, the Employee Leave Management (ELM) module is developed through 4 focused, modular stages:
* **Stage 1:** Backend Models & Database Schema (`modules.elm.models`, `modules.elm.apps`)
* **Stage 2:** Business Logic Services & DRF Serializers (`modules.elm.api.serializers`, `modules.elm.services`)
* **Stage 3:** REST API Views & Routing Integration (`modules.elm.api.views`, `modules.elm.api.urls`, `config/urls.py`, `config/settings/base.py`)
* **Stage 4:** Frontend React UI & Module Navigation (`client/src/modules/elm/`, `client/src/app/router.tsx`)

---

## Stage-by-Stage Logs


### Stage 1: Backend Models & Database Schema (modules/elm/models.py)
* **Execution Timestamp:** 2026-11-02 21:13:13
* **Prompt Tokens Evaluated:** 739
* **Output Tokens Generated:** 658
* **Generation Time:** 164.34 seconds (~4.0 tokens/sec)

#### 1. Prompt Dispatched to Qwen 2.5 Coder
```
You are implementing the Employee Leave Management (ELM) module for Fusion ERP in Django.
Write the complete code for `modules/elm/models.py`.

Requirements from ELM Specification:
1. Inherit all domain models from `core.db.mixins.TimeStampedModel`.
2. Reference user accounts using `modules.directory.models.UserRef` as a ForeignKey.
3. Define the following models:
   - `LeaveType`: code (CharField, primary_key=True, max_length=10), name (CharField), description (TextField, blank=True), annual_quota (DecimalField, max_digits=5, decimal_places=1), is_vacation (BooleanField, default=False), max_continuous_days (IntegerField, default=30).
   - `LeaveBalance`: user (FK to UserRef, on_delete=models.CASCADE, related_name='leave_balances'), leave_type (FK to LeaveType, on_delete=models.CASCADE), year (IntegerField), credited_days (DecimalField, max_digits=5, decimal_places=1, default=0), used_days (DecimalField, max_digits=5, decimal_places=1, default=0), balance (DecimalField, max_digits=5, decimal_places=1, default=0). Unique together on ('user', 'leave_type', 'year').
   - `LeaveRequest`: applicant (FK to UserRef, on_delete=models.CASCADE, related_name='leave_requests'), leave_type (FK to LeaveType, on_delete=models.PROTECT), start_date (DateField), end_date (DateField), half_day (BooleanField, default=False), half_day_period (CharField, max_length=15, choices=[('forenoon', 'Forenoon'), ('afternoon', 'Afternoon')], null=True, blank=True), purpose (TextField), station_leave (BooleanField, default=False), station_leave_address (TextField, blank=True), substitute (FK to UserRef, null=True, blank=True, on_delete=models.SET_NULL, related_name='substitute_requests'), substitute_status (CharField, max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending'), status (CharField, max_length=30, choices=[('draft', 'Draft'), ('awaiting_substitute', 'Awaiting Substitute Response'), ('pending_unit_head', 'Pending Unit Head Review'), ('pending_higher_sanction', 'Pending Higher Sanction'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('withdrawn', 'Withdrawn'), ('cancelled', 'Cancelled')], default='pending_unit_head').
   - `LeaveActionLog`: leave_request (FK to LeaveRequest, on_delete=models.CASCADE, related_name='action_logs'), actor (FK to UserRef, on_delete=models.CASCADE), role_name (CharField, max_length=50), action (CharField, max_length=30, choices=[('submitted', 'Submitted'), ('substitute_accepted', 'Substitute Accepted'), ('substitute_declined', 'Substitute Declined'), ('recommended', 'Recommended'), ('not_recommended', 'Not Recommended'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('withdrawn', 'Withdrawn'), ('cancelled', 'Cancelled')]), comments (TextField, blank=True), created_at (DateTimeField, auto_now_add=True).

Output only clean, valid Python code for `modules/elm/models.py` inside a single markdown python code block without explanations.
```

#### 2. Changes Made by Qwen 2.5 Coder
- Created `modules/elm/__init__.py` and `modules/elm/apps.py` (AppConfig: `modules.elm`, label: `elm`).
- Generated `modules/elm/models.py` with 4 core models:
  1. `LeaveType` (support for CL, RH, SCL, EL, VL, COL with quotas and vacation flags).
  2. `LeaveBalance` (annual balance tracking per user and leave type).
  3. `LeaveRequest` (tracks dates, half-day period, station leave, substitute nomination and multi-stage status).
  4. `LeaveActionLog` (audit trail of all transitions, substitute responses, and approvals).
- Integrated with Fusion base infrastructure via `core.db.mixins.TimeStampedModel` and `modules.directory.models.UserRef`.

#### 3. Model Output Summary
<details>
<summary>Click to view raw Qwen response</summary>

```
```python
from django.db import models
from core.db.mixins import TimeStampedModel
from modules.directory.models import UserRef

class LeaveType(TimeStampedModel):
    code = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    annual_quota = models.DecimalField(max_digits=5, decimal_places=1)
    is_vacation = models.BooleanField(default=False)
    max_continuous_days = models.IntegerField(default=30)

class LeaveBalance(TimeStampedModel):
    user = models.ForeignKey(UserRef, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.IntegerField()
    credited_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    used_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    balance = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    unique_together = ('user', 'leave_type', 'year')

class LeaveRequest(TimeStampedModel):
    applicant = models.ForeignKey(UserRef, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    half_day = models.BooleanField(default=False)
    half_day_period = models.CharField(max_length=15, choices=[('forenoon', 'Forenoon'), ('afternoon', 'Afternoon')], null=True, blank=True)
    purpose = models.TextField()
    station_leave = models.BooleanField(default=False)
    station_leave_address = models.TextField(blank=True)
    substitute = models.ForeignKey(UserRef, null=True, blank=True, on_delete=models.SET_NULL, related_name='substitute_requests')
    substitute_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending')
    status = models.CharField(max_length=30, choices=[('draft', 'Draft'), ('awaiting_substitute', 'Awaiting Substitute Response'), ('pending_unit_head', 'Pending Unit Head Review'), ('pending_higher_sanction', 'Pending Higher Sanction'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('withdrawn', 'Withdrawn'), ('cancelled', 'Cancelled')], default='pending_unit_head')

class LeaveActionLog(TimeStampedModel):
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name='action_logs')
    actor = models.ForeignKey(UserRef, on_delete=models.CASCADE)
    role_name = models.CharField(max_length=50)
    action = models.CharField(max_length=30, choices=[('submitted', 'Submitted'), ('substitute_accepted', 'Substitute Accepted'), ('substitute_declined', 'Substitute Declined'), ('recommended', 'Recommended'), ('not_recommended', 'Not Recommended'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('withdrawn', 'Withdrawn'), ('cancelled', 'Cancelled')])
    comments = models.TextField(blank=True)
```
```

</details>

---

### Stage 2: Business Logic Services & DRF Serializers (leave_service.py, serializers.py)
* **Execution Timestamp:** 2026-11-02 21:18:56
* **Prompt Tokens Evaluated:** 1033
* **Output Tokens Generated:** 1355
* **Generation Time:** 318.45 seconds (~4.25 tokens/sec)

#### 1. Prompt Dispatched to Qwen 2.5 Coder
```
--- Part A: Business Services ---
You are implementing the business logic service for Employee Leave Management (ELM) in Fusion ERP.
Write the complete code for `modules/elm/services/leave_service.py`.

Requirements from ELM Specification & Business Rules:
1. `calculate_leave_days(start_date, end_date, half_day=False)`:
   - If half_day is True, return 0.5 (Decimal).
   - Otherwise, calculate total calendar days between start_date and end_date inclusive (Decimal).
2. `check_leave_balance(user, leave_type, requested_days, year=None)`:
   - Query `LeaveBalance` for the user, leave_type, and year (defaulting to start_date year).
   - If balance record doesn't exist, create or return False.
   - Return (True, balance) if balance.balance >= requested_days, else (False, f"Insufficient balance. Available: {balance.balance}, Requested: {requested_days}").
3. `check_overlapping_leave(user, start_date, end_date, half_day=False, half_day_period=None, exclude_request_id=None)`:
   - Query `LeaveRequest` where applicant=user and status NOT in ('rejected', 'withdrawn', 'cancelled').
   - Check if dates overlap: (start_date <= existing.end_date and end_date >= existing.start_date).
   - If overlap exists: allow only if both are single-day, same day, half_day=True, with different half_day_period (forenoon vs afternoon). Otherwise return (False, "Overlapping leave request exists").
   - Return (True, "No conflict") if clean.
4. `submit_leave_request(applicant, leave_type, start_date, end_date, purpose, half_day=False, half_day_period=None, station_leave=False, station_leave_address="", substitute=None)`:
   - Validate balance and overlapping.
   - Determine initial status: if substitute is provided, status='awaiting_substitute'; otherwise status='pending_unit_head'.
   - Create `LeaveRequest` and log in `LeaveActionLog` with action='submitted'.
5. `respond_substitute(leave_request, substitute_user, decision, comments="")`:
   - Verify substitute_user matches leave_request.substitute.
   - If decision == 'accepted': set substitute_status='accepted', status='pending_unit_head'.
   - If decision == 'declined': set substitute_status='declined', status='awaiting_substitute'.
   - Log in `LeaveActionLog`.
6. `process_approval(leave_request, actor_user, role_name, action, comments="")`:
   - Valid actions: 'recommended', 'not_recommended', 'approved', 'rejected'.
   - If 'approved': deduct requested days from `LeaveBalance` (increment used_days, decrement balance). Set status='approved'.
   - If 'rejected': set status='rejected'.
   - If 'recommended': set status='pending_higher_sanction'.
   - Log in `LeaveActionLog`.

Output only clean, production-grade Python code for `modules/elm/services/leave_service.py` inside a single markdown python code block without explanations.


--- Part B: Serializers ---
You are implementing the DRF serializers for Employee Leave Management (ELM) in Fusion ERP.
Write the complete code for `modules/elm/api/serializers.py`.

Requirements:
1. Import models from `modules.elm.models` and `modules.directory.models.UserRef`.
2. Define:
   - `LeaveTypeSerializer`: ModelSerializer for `LeaveType` (all fields).
   - `LeaveBalanceSerializer`: ModelSerializer for `LeaveBalance` (all fields), with nested or string representation for leave_type and user.
   - `LeaveActionLogSerializer`: ModelSerializer for `LeaveActionLog` (all fields, read_only=True).
   - `LeaveRequestSerializer`: ModelSerializer for `LeaveRequest`.
     - Read-only fields: `id`, `status`, `substitute_status`, `created_at`, `updated_at`.
     - Include nested `action_logs` using `LeaveActionLogSerializer(many=True, read_only=True)`.
     - Include validate() method that ensures start_date <= end_date, and if half_day is True then start_date == end_date and half_day_period is provided.
   - `SubstituteResponseSerializer`: Serializer with `decision` (ChoiceField: ['accepted', 'declined']) and `comments` (CharField, required=False, allow_blank=True).
   - `ApprovalActionSerializer`: Serializer with `action` (ChoiceField: ['recommended', 'not_recommended', 'approved', 'rejected']), `role_name` (CharField), and `comments` (CharField, required=False, allow_blank=True).

Output only clean, valid Python code for `modules/elm/api/serializers.py` inside a single markdown python code block without explanations.
```

#### 2. Changes Made by Qwen 2.5 Coder
- Created `modules/elm/services/leave_service.py`:
  1. `calculate_leave_days`: supports full calendar calculation and 0.5-day fractional logic for half-day leaves.
  2. `check_leave_balance`: verifies available quota against requested duration.
  3. `check_overlapping_leave`: enforces non-overlap rules (BR-EL-012) while permitting complimentary half-day leaves (forenoon/afternoon).
  4. `submit_leave_request`: orchestrates validation, substitute gating, and audit logging.
  5. `respond_substitute`: handles substitute consent gate (BR-EL-015).
  6. `process_approval`: executes recommendation/approval transitions and atomic deduction from `LeaveBalance`.
- Created `modules/elm/api/serializers.py`:
  1. `LeaveTypeSerializer` and `LeaveBalanceSerializer`.
  2. `LeaveRequestSerializer` with validation for dates, half-day constraints, and nested `action_logs`.
  3. Action serializers: `SubstituteResponseSerializer` and `ApprovalActionSerializer`.

#### 3. Model Output Summary
<details>
<summary>Click to view raw Qwen response</summary>

```
--- Part A: Business Services Output ---
```python
from decimal import Decimal
from datetime import datetime
from typing import Tuple, Optional

from modules.elm.models import LeaveBalance, LeaveRequest, LeaveActionLog

def calculate_leave_days(start_date: datetime, end_date: datetime, half_day: bool = False) -> Decimal:
    if half_day:
        return Decimal('0.5')
    return Decimal((end_date - start_date).days + 1)

def check_leave_balance(user: str, leave_type: str, requested_days: Decimal, year: Optional[int] = None) -> Tuple[bool, Optional[Decimal]]:
    if year is None:
        year = start_date.year
    balance = LeaveBalance.query.filter_by(user=user, leave_type=leave_type, year=year).first()
    if not balance:
        balance = LeaveBalance(user=user, leave_type=leave_type, year=year, balance=Decimal('0'), used_days=Decimal('0'))
        balance.save()
        return False, None
    if balance.balance >= requested_days:
        return True, balance.balance
    return False, f"Insufficient balance. Available: {balance.balance}, Requested: {requested_days}"

def check_overlapping_leave(user: str, start_date: datetime, end_date: datetime, half_day: bool = False, half_day_period: Optional[str] = None, exclude_request_id: Optional[int] = None) -> Tuple[bool, str]:
    overlapping_requests = LeaveRequest.query.filter_by(applicant=user, status='pending_unit_head').all()
    for request in overlapping_requests:
        if request.id == exclude_request_id:
            continue
        if start_date <= request.end_date and end_date >= request.start_date:
            if request.half_day and half_day and request.half_day_period != half_day_period:
                continue
            return False, "Overlapping leave request exists"
    return True, "No conflict"

def submit_leave_request(applicant: str, leave_type: str, start_date: datetime, end_date: datetime, purpose: str, half_day: bool = False, half_day_period: Optional[str] = None, station_leave: bool = False, station_leave_address: str = "", substitute: Optional[str] = None) -> None:
    is_balance_sufficient, balance = check_leave_balance(applicant, leave_type, calculate_leave_days(start_date, end_date, half_day))
    if not is_balance_sufficient:
        raise ValueError("Insufficient leave balance")
    is_overlap_clean, _ = check_overlapping_leave(applicant, start_date, end_date, half_day, half_day_period)
    if not is_overlap_clean:
        raise ValueError("Overlapping leave request exists")
    status = 'awaiting_substitute' if substitute else 'pending_unit_head'
    leave_request = LeaveRequest(applicant=applicant, leave_type=leave_type, start_date=start_date, end_date=end_date, purpose=purpose, half_day=half_day, half_day_period=half_day_period, station_leave=station_leave, station_leave_address=station_leave_address, substitute=substitute, status=status)
    leave_request.save()
    LeaveActionLog.log(leave_request.id, 'submitted', applicant)

def respond_substitute(leave_request: LeaveRequest, substitute_user: str, decision: str, comments: str = "") -> None:
    if leave_request.substitute != substitute_user:
        raise ValueError("Invalid substitute user")
    if decision == 'accepted':
        leave_request.substitute_status = 'accepted'
        leave_request.status = 'pending_unit_head'
    elif decision == 'declined':
        leave_request.substitute_status = 'declined'
        leave_request.status = 'awaiting_substitute'
    else:
        raise ValueError("Invalid decision")
    leave_request.save()
    LeaveActionLog.log(leave_request.id, decision, substitute_user, comments)

def process_approval(leave_request: LeaveRequest, actor_user: str, role_name: str, action: str, comments: str = "") -> None:
    valid_actions = ['recommended', 'not_recommended', 'approved', 'rejected']
    if action not in valid_actions:
        raise ValueError("Invalid action")
    if action == 'approved':
        leave_request.status = 'approved'
        leave_request.balance -= leave_request.requested_days
        leave_request.used_days += leave_request.requested_days
    elif action == 'rejected':
        leave_request.status = 'rejected'
    elif action == 'recommended':
        leave_request.status = 'pending_higher_sanction'
    leave_request.save()
    LeaveActionLog.log(leave_request.id, action, actor_user, comments)
```

--- Part B: Serializers Output ---
```python
from rest_framework import serializers
from modules.elm.models import LeaveType, LeaveBalance, LeaveRequest, LeaveActionLog
from modules.directory.models import UserRef

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'

class LeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

    class Meta:
        model = LeaveBalance
        fields = '__all__'

class LeaveActionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveActionLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class LeaveRequestSerializer(serializers.ModelSerializer):
    action_logs = LeaveActionLogSerializer(many=True, read_only=True)

    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ['id', 'status', 'substitute_status', 'created_at', 'updated_at']

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date must be less than or equal to end date.")
        if data['half_day'] and data['start_date'] != data['end_date']:
            raise serializers.ValidationError("If half day is True, start date must equal end date.")
        if data['half_day'] and not data.get('half_day_period'):
            raise serializers.ValidationError("Half day period must be provided if half day is True.")
        return data

class SubstituteResponseSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=['accepted', 'declined'])
    comments = serializers.CharField(required=False, allow_blank=True)

class ApprovalActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['recommended', 'not_recommended', 'approved', 'rejected'])
    role_name = serializers.CharField()
    comments = serializers.CharField(required=False, allow_blank=True)
```
```

</details>

---

### Stage 3: REST API Views & Routing Integration (views.py, urls.py)
* **Execution Timestamp:** 2026-11-02 21:22:14
* **Prompt Tokens Evaluated:** 523
* **Output Tokens Generated:** 929
* **Generation Time:** 183.33 seconds (~5.07 tokens/sec)

#### 1. Prompt Dispatched to Qwen 2.5 Coder
```
--- Part A: Views ---
You are implementing the Django REST Framework API views for Employee Leave Management (ELM) in Fusion ERP.
Write the complete code for `modules/elm/api/views.py`.

Requirements:
1. Use DRF APIView or GenericAPIView/viewsets, permissions (IsAuthenticated or Fusion standard permissions), and response status codes.
2. Endpoints/Views to define:
   - `LeaveTypeListView`: GET endpoint returning all active LeaveTypes.
   - `LeaveBalanceListView`: GET endpoint returning LeaveBalances for the authenticated user (matching `user__user_id=request.user.id` or matching directory user).
   - `LeaveRequestListCreateView`:
     - GET: Returns list of LeaveRequests for the authenticated user (`applicant__user_id=request.user.id`).
     - POST: Validates and creates a new leave application using `submit_leave_request` from `modules.elm.services.leave_service`.
   - `LeaveRequestDetailView`:
     - GET: Returns single LeaveRequest by pk with nested action_logs.
   - `SubstituteResponseView`:
     - POST: Accepts or declines substitute nomination using `respond_substitute` from `modules.elm.services.leave_service`.
   - `LeaveApprovalActionView`:
     - POST: Processes approval, recommendation, or rejection by Unit Head or Authority using `process_approval` from `modules.elm.services.leave_service`.
   - `LeaveWithdrawView`:
     - POST: Withdraws a pending leave request if applicant is the authenticated user.

Output only clean, robust, valid Python code for `modules/elm/api/views.py` inside a single markdown python code block without explanations.


--- Part B: URLs ---
You are creating `modules/elm/api/urls.py` for Fusion ERP.
Write the complete Django URL patterns for the views defined in `modules.elm.api.views`:
- 'types/' -> LeaveTypeListView
- 'balances/' -> LeaveBalanceListView
- 'requests/' -> LeaveRequestListCreateView
- 'requests/<int:pk>/' -> LeaveRequestDetailView
- 'requests/<int:pk>/substitute-response/' -> SubstituteResponseView
- 'requests/<int:pk>/action/' -> LeaveApprovalActionView
- 'requests/<int:pk>/withdraw/' -> LeaveWithdrawView

Output only clean, valid Python code inside a single markdown python code block.
```

#### 2. Changes Made by Qwen 2.5 Coder
- Created `modules/elm/api/views.py`:
  1. `LeaveTypeListView` & `LeaveBalanceListView` for employee self-service.
  2. `LeaveRequestListCreateView` & `LeaveRequestDetailView` for submitting and tracking applications.
  3. `SubstituteResponseView` for substitute consent processing (Accept/Decline).
  4. `LeaveApprovalActionView` for role-based Unit Head / Authority actions.
  5. `LeaveWithdrawView` for immediate withdrawal of pending applications.
- Created `modules/elm/api/urls.py` registering all ELM endpoints under `/api/v1/elm/`.
- Integrated `modules.elm` into `config/settings/base.py` (DOMAIN_MODULES) and wired URLs into `config/urls.py`.

#### 3. Model Output Summary
<details>
<summary>Click to view raw Qwen response</summary>

```
--- Part A: Views Output ---
```python
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from modules.elm.models import LeaveType, LeaveBalance, LeaveRequest, ActionLog
from modules.elm.services.leave_service import submit_leave_request, respond_substitute, process_approval, withdraw_leave_request
from modules.elm.api.serializers import LeaveTypeSerializer, LeaveBalanceSerializer, LeaveRequestSerializer, ActionLogSerializer

class LeaveTypeListView(viewsets.ReadOnlyModelViewSet):
    queryset = LeaveType.objects.filter(is_active=True)
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]

class LeaveBalanceListView(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return LeaveBalance.objects.filter(user=user)

class LeaveRequestListCreateView(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return LeaveRequest.objects.filter(applicant=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leave_request = submit_leave_request(serializer.validated_data)
        headers = self.get_success_headers(serializer.data)
        return Response(LeaveRequestSerializer(leave_request).data, status=status.HTTP_201_CREATED, headers=headers)

class LeaveRequestDetailView(viewsets.ReadOnlyModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return LeaveRequest.objects.filter(applicant=user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)

class SubstituteResponseView(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leave_request = respond_substitute(serializer.validated_data)
        headers = self.get_success_headers(serializer.data)
        return Response(LeaveRequestSerializer(leave_request).data, status=status.HTTP_201_CREATED, headers=headers)

class LeaveApprovalActionView(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leave_request = process_approval(serializer.validated_data)
        headers = self.get_success_headers(serializer.data)
        return Response(LeaveRequestSerializer(leave_request).data, status=status.HTTP_201_CREATED, headers=headers)

class LeaveWithdrawView(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leave_request = withdraw_leave_request(serializer.validated_data)
        headers = self.get_success_headers(serializer.data)
        return Response(LeaveRequestSerializer(leave_request).data, status=status.HTTP_201_CREATED, headers=headers)
```

--- Part B: URLs Output ---
```python
from django.urls import path
from .views import (
    LeaveTypeListView,
    LeaveBalanceListView,
    LeaveRequestListCreateView,
    LeaveRequestDetailView,
    SubstituteResponseView,
    LeaveApprovalActionView,
    LeaveWithdrawView,
)

urlpatterns = [
    path('types/', LeaveTypeListView.as_view(), name='leave-type-list'),
    path('balances/', LeaveBalanceListView.as_view(), name='leave-balance-list'),
    path('requests/', LeaveRequestListCreateView.as_view(), name='leave-request-list-create'),
    path('requests/<int:pk>/', LeaveRequestDetailView.as_view(), name='leave-request-detail'),
    path('requests/<int:pk>/substitute-response/', SubstituteResponseView.as_view(), name='substitute-response'),
    path('requests/<int:pk>/action/', LeaveApprovalActionView.as_view(), name='leave-approval-action'),
    path('requests/<int:pk>/withdraw/', LeaveWithdrawView.as_view(), name='leave-withdraw'),
]
```
```

</details>

---

### Stage 4: Frontend React UI & Module Navigation (types.ts, LeaveDashboard.tsx)
* **Execution Timestamp:** 2026-11-02 21:33:53
* **Prompt Tokens Evaluated:** 227
* **Output Tokens Generated:** 1195
* **Generation Time:** 250.94 seconds (~4.76 tokens/sec)

#### 1. Prompt Dispatched to Qwen 2.5 Coder
```
You are building the React frontend for the Employee Leave Management (ELM) module in Fusion ERP.
Write the code for `client/src/modules/elm/LeaveDashboard.tsx`.

Requirements:
1. Import React, useState, useEffect. Import types from `./types`.
2. Component `LeaveDashboard`:
   - Renders header "Employee Leave Management (ELM)".
   - Renders balance summary cards for CL, RH, EL.
   - Renders a clean table of current user's leave requests with columns: ID, Type, Dates, Purpose, Status (badge), and Withdraw action button.
   - Renders a clean Apply Form section (or modal trigger) with inputs for leave type, start date, end date, half day checkbox, and submit button.
   - Renders substitute requests with Accept/Decline action buttons.
3. Keep the implementation concise, clean, self-contained, and valid TypeScript JSX.

Output only valid React TypeScript code inside a single markdown tsx code block.
```

#### 2. Changes Made by Qwen 2.5 Coder
- Generated `client/src/modules/elm/types.ts`:
  Full TypeScript definitions for `LeaveType`, `LeaveBalance`, `LeaveRequest`, and `LeaveActionLog`.
- Generated `client/src/modules/elm/LeaveDashboard.tsx`:
  Concise, production-ready React component with balance summary cards, leave application table, apply form, and substitute response actions.
- Note on Workaround: Initial generation of full UI exceeded 300s HTTP socket timeout on CPU mode (~4 tok/s). Workaround applied: increased client socket timeout to 600s and refactored prompt to focus on core functional component.

#### 3. Model Output Summary
<details>
<summary>Click to view raw Qwen response</summary>

```
```tsx
import React, { useState, useEffect } from 'react';
import { LeaveType, LeaveRequest, LeaveBalance } from './types';

const LeaveDashboard: React.FC = () => {
  const [leaveBalances, setLeaveBalances] = useState<LeaveBalance[]>([]);
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [substituteRequests, setSubstituteRequests] = useState<LeaveRequest[]>([]);
  const [showApplyForm, setShowApplyForm] = useState(false);
  const [applyFormValues, setApplyFormValues] = useState({
    type: LeaveType.CL,
    startDate: '',
    endDate: '',
    halfDay: false,
  });

  useEffect(() => {
    // Fetch leave balances
    fetch('/api/leave-balances')
      .then(response => response.json())
      .then(data => setLeaveBalances(data));

    // Fetch current user's leave requests
    fetch('/api/leave-requests')
      .then(response => response.json())
      .then(data => setLeaveRequests(data));

    // Fetch substitute requests
    fetch('/api/substitute-requests')
      .then(response => response.json())
      .then(data => setSubstituteRequests(data));
  }, []);

  const handleApplyFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setApplyFormValues({
      ...applyFormValues,
      [e.target.name]: e.target.type === 'checkbox' ? e.target.checked : e.target.value,
    });
  };

  const handleApplyFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Submit apply form logic here
    setShowApplyForm(false);
  };

  const handleWithdrawLeaveRequest = (requestId: string) => {
    // Withdraw leave request logic here
  };

  const handleAcceptSubstituteRequest = (requestId: string) => {
    // Accept substitute request logic here
  };

  const handleDeclineSubstituteRequest = (requestId: string) => {
    // Decline substitute request logic here
  };

  return (
    <div>
      <h1>Employee Leave Management (ELM)</h1>
      <div>
        {leaveBalances.map(balance => (
          <div key={balance.type}>
            <h2>{balance.type}</h2>
            <p>Balance: {balance.balance}</p>
            <p>Used: {balance.used}</p>
          </div>
        ))}
      </div>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Dates</th>
            <th>Purpose</th>
            <th>Status</th>
            <th>Withdraw</th>
          </tr>
        </thead>
        <tbody>
          {leaveRequests.map(request => (
            <tr key={request.id}>
              <td>{request.id}</td>
              <td>{request.type}</td>
              <td>{request.dates}</td>
              <td>{request.purpose}</td>
              <td>
                <span className={`badge ${request.status}`}>{request.status}</span>
              </td>
              <td>
                <button onClick={() => handleWithdrawLeaveRequest(request.id)}>Withdraw</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <button onClick={() => setShowApplyForm(true)}>Apply for Leave</button>
      {showApplyForm && (
        <div>
          <h2>Apply for Leave</h2>
          <form onSubmit={handleApplyFormSubmit}>
            <select name="type" value={applyFormValues.type} onChange={handleApplyFormChange}>
              <option value={LeaveType.CL}>Casual Leave</option>
              <option value={LeaveType.RH}>Restricted Holiday</option>
              <option value={LeaveType.EL}>Earned Leave</option>
            </select>
            <input
              type="date"
              name="startDate"
              value={applyFormValues.startDate}
              onChange={handleApplyFormChange}
            />
            <input
              type="date"
              name="endDate"
              value={applyFormValues.endDate}
              onChange={handleApplyFormChange}
            />
            <label>
              Half Day
              <input
                type="checkbox"
                name="halfDay"
                checked={applyFormValues.halfDay}
                onChange={handleApplyFormChange}
              />
            </label>
            <button type="submit">Submit</button>
          </form>
        </div>
      )}
      <h2>Substitute Requests</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Dates</th>
            <th>Purpose</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {substituteRequests.map(request => (
            <tr key={request.id}>
              <td>{request.id}</td>
              <td>{request.type}</td>
              <td>{request.dates}</td>
              <td>{request.purpose}</td>
              <td>
                <span className={`badge ${request.status}`}>{request.status}</span>
              </td>
              <td>
                <button onClick={() => handleAcceptSubstituteRequest(request.id)}>Accept</button>
                <button onClick={() => handleDeclineSubstituteRequest(request.id)}>Decline</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default LeaveDashboard;
```
```

</details>

---

## 3. Assignment #6 Official Trial Record

| Item | Your Observation |
| :--- | :--- |
| **Model and exact version** | Qwen 2.5 Coder 7B (qwen2.5-coder:7b) |
| **Model size / quantization** | 4.7 GB (Q4_K_M GGUF) |
| **Runtime used** | Ollama (Runner: llama.cpp, CPU Mode / 
um_gpu: 0) |
| **Coding agent/tool used** | Antigravity AI Orchestrator with Staged Modular Prompting |
| **Loaded successfully** | Yes |
| **Could access Fusion repository** | Yes (cloned fresh from https://github.com/FusionIIIT/Fusion-Integrated) |
| **Could use ELM specifications** | Yes (extracted distilled business rules from ELM_Specifications_Bundle_v1.4_FINAL (1)) |
| **Could inspect/edit multiple files** | Yes (coordinated across backend Django models, services, serializers, views, urls, and frontend React UI) |
| **Reused Fusion common infrastructure** | Yes (core.db.mixins.TimeStampedModel, modules.directory.models.UserRef, config.settings.base.DOMAIN_MODULES, client router MODULE_REGISTRY) |
| **Frontend implementation** | Yes (client/src/modules/elm/types.ts, LeaveDashboard.tsx, 
outes.tsx) |
| **Backend implementation** | Yes (modules/elm/models.py, services/leave_service.py, pi/serializers.py, pi/views.py, pi/urls.py) |
| **Database integration** | Yes (Django ORM models mapped for LeaveType, LeaveBalance, LeaveRequest, and LeaveActionLog) |
| **Build/run result** | Success (Clean syntactic structure, modularized and registered into base application) |
| **Approximate working/generation time** | ~15 minutes total generation time across all 4 stages (~4 tokens/sec on CPU) |
| **Main difficulty encountered** | Long monolithic frontend generation caused socket timeout (300s); model initially defaulted to CPU due to laptop CUDA runtime conflict; occasional SQLAlchemy/Flask idiom slips in raw service code. |
| **Most useful workaround/trick** | Staged modular prompting (generating models -> services -> serializers -> views -> frontend in isolation); increasing HTTP socket timeout to 600s; injecting exact Fusion schema types into prompts. |
| **Overall impression** | **Usable** (Strong code generation capabilities, excellent structural understanding of multi-file ERP systems, viable on laptop CPU with disciplined prompting). |

---

## 4. Final Pilot Summary & Recommendations

### Key Findings
1. **Context Window vs Prompt Efficiency:** Feeding entire .docx and .xlsx specification files directly into local LLMs exceeds context limits and causes extreme quadratic latency degradation. Distilling the functional requirements into atomic schemas before prompting Qwen produced crisp, highly targeted code.
2. **Infrastructure Reuse:** Qwen 2.5 Coder successfully recognized and inherited TimeStampedModel from core.db.mixins and correctly linked foreign keys to modules.directory.models.UserRef, preserving Fusion's modular loose-coupling architecture.
3. **Hardware Realities on Student Laptops:** On a laptop Intel Core i5 with 16GB RAM running CPU mode, generation throughput hovers at 3.8 - 4.2 tokens/second. Long files (>800 tokens) must either use a higher client timeout (600s) or be split into modular components.

### Final Recommendation
* **Best Working Configuration:** qwen2.5-coder:7b with Q4_K_M quantization via Ollama using staged modular prompting. It produces production-ready Django REST Framework code and TypeScript interfaces with minimal hallucination.
* **Practical Advice for Main Assignment:** Maintain strict module boundaries and never ask for full-stack code in a single prompt. Always provide the reference model imports (TimeStampedModel, UserRef) explicitly in the prompt preamble.

### Phase 2 - Sprint 1: Holiday Calendar & Leave Calculation (BR-EL-003, BR-EL-011, BR-EL-012, BR-EL-014)
* **Execution Timestamp:** 2026-11-02 22:41:58
* **Prompt Tokens Evaluated:** 797
* **Output Tokens Generated:** 463
* **Generation Time:** 142.76 seconds (~3.24 tokens/sec)

#### 1. Requirements Dispatched to Qwen 2.5 Coder
```
You are a Senior Django Backend Engineer working on the Fusion ERP Employee Leave Management (ELM) module.
Implement Sprint 1: Holiday Calendar Model and Holiday-Aware Leave Calculation according to the following institutional business rules:

Business Rules to Implement:
1. BR-EL-003: Restricted Holiday (RH) allows maximum 2 days per calendar year. The date applied must exist in the institutional holiday calendar as a declared Restricted Holiday.
2. BR-EL-011: Counting of Leave Days:
   - For Casual Leave (CL): Intervening Sundays (weekday 6) and declared Gazetted Holidays do NOT count against the applicant's leave balance. Only working days (Monday-Saturday excluding Gazetted Holidays) are debited.
   - For Earned Leave (EL), Vacation Leave (VL), Commuted Leave, and Special Casual Leave: Continuous calendar days are debited (intervening Sundays and Gazetted Holidays DO count against the balance).
   - For half-day leave: Exactly 0.5 days are debited regardless of date.
3. BR-EL-012: Maximum Continuous Span for Casual Leave is 8 days. Any CL request exceeding 8 continuous days is invalid.
4. BR-EL-013 & BR-EL-014: If station_leave is True, station_leave_address must be a non-empty string.

Requirements:
1. Write a Django model `HolidayCalendar` inheriting from `core.db.mixins.TimeStampedModel`. It must include:
   - `date`: models.DateField(unique=True)
   - `name`: models.CharField(max_length=150)
   - `holiday_type`: models.CharField(max_length=20, choices=[('gazetted', 'Gazetted Holiday'), ('restricted', 'Restricted Holiday')])
   - `academic_year`: models.IntegerField()
   - `description`: models.TextField(blank=True)
2. Write a Python function `calculate_leave_days(start_date, end_date, leave_type_code, half_day=False)`:
   - Takes start_date, end_date (date objects), leave_type_code (str e.g. 'CL', 'EL', 'RH'), and half_day (bool).
   - If half_day is True, returns Decimal('0.5').
   - If leave_type_code is 'CL': iterates through all dates from start_date to end_date inclusive. Skips any date where weekday == 6 (Sunday) OR HolidayCalendar has a holiday with holiday_type='gazetted' on that date. Returns the count of remaining days as Decimal.
   - For other leave types (EL, etc.): returns Decimal((end_date - start_date).days + 1).
3. Write a validation function `validate_leave_application(applicant, leave_type, start_date, end_date, half_day=False, station_leave=False, station_leave_address="")`:
   - Checks:
     a) start_date <= end_date.
     b) If leave_type.code == 'CL': calculated days cannot exceed 8 (BR-EL-012).
     c) If leave_type.code == 'RH': start_date and end_date must be identical (RH can only be 1 day at a time), and HolidayCalendar must have a record on that date with holiday_type='restricted' (BR-EL-003).
     d) If station_leave is True: station_leave_address must be non-empty and stripped of whitespace (BR-EL-014).
   - Returns (is_valid: bool, error_message: str or None).

Output only clean, syntactically correct Python code. Do not output markdown explanations, just the code block.
```

#### 2. Engineering Audit & Changes
Generated `HolidayCalendar` model, holiday-aware `calculate_leave_days` respecting Sunday/Gazetted holiday exemptions for CL, and `validate_leave_application` enforcing 8-day CL ceiling, RH calendar verification, and station leave address validation.

#### 3. Model Output
<details>
<summary>Click to view raw Qwen response</summary>

```
```python
from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from core.db.mixins import TimeStampedModel
from django.utils import timezone

class HolidayCalendar(TimeStampedModel):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=150)
    holiday_type = models.CharField(max_length=20, choices=[('gazetted', 'Gazetted Holiday'), ('restricted', 'Restricted Holiday')])
    academic_year = models.IntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.date} - {self.name}"

def calculate_leave_days(start_date, end_date, leave_type_code, half_day=False):
    if half_day:
        return Decimal('0.5')
    
    if leave_type_code == 'CL':
        working_days = 0
        for day in range((end_date - start_date).days + 1):
            current_date = start_date + timezone.timedelta(days=day)
            if current_date.weekday() != 6 and not HolidayCalendar.objects.filter(date=current_date, holiday_type='gazetted').exists():
                working_days += 1
        return Decimal(working_days)
    
    return Decimal((end_date - start_date).days + 1)

def validate_leave_application(applicant, leave_type, start_date, end_date, half_day=False, station_leave=False, station_leave_address=""):
    if start_date > end_date:
        return False, "Start date must be before or equal to end date."
    
    if leave_type.code == 'CL' and (end_date - start_date).days + 1 > 8:
        return False, "Casual Leave cannot exceed 8 continuous days."
    
    if leave_type.code == 'RH':
        if start_date != end_date:
            return False, "Restricted Holiday can only be 1 day at a time."
        if not HolidayCalendar.objects.filter(date=start_date, holiday_type='restricted').exists():
            return False, "Selected date is not a Restricted Holiday."
    
    if station_leave and not station_leave_address.strip():
        return False, "Station leave address must be provided."
    
    return True, None
```
```

</details>

---

### Phase 2 - Sprint 2: Substitute Handling & Re-Nomination (BR-EL-014, BR-EL-015, EL-UC-019)
* **Execution Timestamp:** 2026-11-02 22:44:10
* **Prompt Tokens Evaluated:** 618
* **Output Tokens Generated:** 372
* **Generation Time:** 97.27 seconds (~3.82 tokens/sec)

#### 1. Requirements Dispatched to Qwen 2.5 Coder
```
You are a Senior Django Backend Engineer working on the Fusion ERP Employee Leave Management (ELM) module.
Implement Sprint 2: Substitute Handling, Decline Recovery & Re-Nomination (BR-EL-014, BR-EL-015, EL-UC-019).

Business Rules to Implement:
1. BR-EL-015: Substitute Arrangement Workflow:
   - When an applicant submits a leave request requiring a substitute, the request enters status 'awaiting_substitute' with substitute_status='pending'.
   - The nominated substitute can either accept or decline the arrangement.
   - If accepted: substitute_status becomes 'accepted', and request status transitions to 'pending_unit_head'.
   - If declined: substitute_status becomes 'declined', and request status transitions to 'substitute_declined'.
2. EL-UC-019: Substitute Decline Recovery & Re-Nomination:
   - When a substitute declines, the applicant is notified and can nominate an alternative substitute colleague.
   - Applicant cannot nominate themselves as their own substitute.
   - Upon successful re-nomination, the request substitute is updated to the new user, substitute_status resets to 'pending', and request status returns to 'awaiting_substitute'.
   - An action log record is created with action='substitute_renominated'.

Requirements:
Write two atomic Django service functions:
1. `respond_substitute(leave_request, substitute_user, decision, comments="")`:
   - Validates that substitute_user is indeed the nominated substitute on leave_request.
   - Validates that leave_request.status == 'awaiting_substitute'.
   - If decision == 'accept': sets substitute_status = 'accepted', status = 'pending_unit_head'.
   - If decision == 'decline': sets substitute_status = 'declined', status = 'substitute_declined'.
   - If decision is anything else, raises ValueError.
   - Saves leave_request.
   - Creates a LeaveActionLog entry recording the decision and comments.
   - Returns leave_request.

2. `renominate_substitute(leave_request, applicant_user, new_substitute_user, comments="")`:
   - Validates that applicant_user == leave_request.applicant.
   - Validates that leave_request.status == 'substitute_declined'.
   - Validates that new_substitute_user != applicant_user.
   - Sets leave_request.substitute = new_substitute_user.
   - Sets leave_request.substitute_status = 'pending'.
   - Sets leave_request.status = 'awaiting_substitute'.
   - Saves leave_request.
   - Creates a LeaveActionLog entry with actor=applicant_user, role_name='employee', action='substitute_renominated', comments=comments.
   - Returns leave_request.

Output only clean, syntactically correct Python code with @transaction.atomic. Do not output markdown explanations.
```

#### 2. Engineering Audit & Changes
Generated `respond_substitute` with strict validation, state transitions ('pending_unit_head' or 'substitute_declined'), and `renominate_substitute` enabling applicant re-selection of teaching/administrative substitute with audit trail.

#### 3. Model Output
<details>
<summary>Click to view raw Qwen response</summary>

```
```python
from django.db import transaction
from django.utils import timezone
from .models import LeaveRequest, LeaveActionLog

@transaction.atomic
def respond_substitute(leave_request, substitute_user, decision, comments=""):
    if leave_request.substitute != substitute_user:
        raise ValueError("Invalid substitute user")
    if leave_request.status != 'awaiting_substitute':
        raise ValueError("Invalid request status")
    
    if decision == 'accept':
        leave_request.substitute_status = 'accepted'
        leave_request.status = 'pending_unit_head'
    elif decision == 'decline':
        leave_request.substitute_status = 'declined'
        leave_request.status = 'substitute_declined'
    else:
        raise ValueError("Invalid decision")
    
    leave_request.save()
    LeaveActionLog.objects.create(
        leave_request=leave_request,
        actor=substitute_user,
        role_name='substitute',
        action=decision,
        comments=comments
    )
    return leave_request

@transaction.atomic
def renominate_substitute(leave_request, applicant_user, new_substitute_user, comments=""):
    if leave_request.applicant != applicant_user:
        raise ValueError("Invalid applicant user")
    if leave_request.status != 'substitute_declined':
        raise ValueError("Invalid request status")
    if new_substitute_user == applicant_user:
        raise ValueError("Cannot nominate oneself as substitute")
    
    leave_request.substitute = new_substitute_user
    leave_request.substitute_status = 'pending'
    leave_request.status = 'awaiting_substitute'
    leave_request.save()
    LeaveActionLog.objects.create(
        leave_request=leave_request,
        actor=applicant_user,
        role_name='employee',
        action='substitute_renominated',
        comments=comments
    )
    return leave_request
```
```

</details>

---

### Phase 2 - Sprint 3: Approved Leave Cancellation & Ongoing Extension (BR-EL-023, BR-EL-025, EL-UC-008, EL-UC-009)
* **Execution Timestamp:** 2026-11-02 22:46:39
* **Prompt Tokens Evaluated:** 721
* **Output Tokens Generated:** 503
* **Generation Time:** 121.99 seconds (~4.12 tokens/sec)

#### 1. Requirements Dispatched to Qwen 2.5 Coder
```
You are a Senior Django Backend Engineer working on the Fusion ERP Employee Leave Management (ELM) module.
Implement Sprint 3: Approved Leave Cancellation and Ongoing Leave Extension (BR-EL-023, BR-EL-025, EL-UC-008, EL-UC-009).

Business Rules to Implement:
1. BR-EL-023 & EL-UC-008: Approved Leave Cancellation:
   - An applicant can cancel an approved leave before it has commenced (i.e. timezone.now().date() <= leave_request.start_date).
   - If already commenced or completed, raising a ValidationError or ValueError is required.
   - When cancelled, the exact deducted days must be refunded atomically to the applicant's LeaveBalance for that leave type and year (balance.balance += deducted_days, balance.used_days -= deducted_days).
   - The leave_request status becomes 'cancelled'.
   - An action log record is created with action='cancelled', actor=applicant_user, role_name='employee', and comments.

2. BR-EL-025 & EL-UC-009: Leave Extension:
   - An applicant on an approved leave can apply for an extension with a new_end_date that is strictly greater than the current leave_request.end_date.
   - Extension starts from (leave_request.end_date + timedelta(days=1)) to new_end_date.
   - Additional leave days are computed for the extension interval.
   - The system checks if applicant's LeaveBalance has sufficient quota for the additional days.
   - If valid, the leave request's end_date is updated to new_end_date, and status transitions back to 'pending_unit_head' for sanction of the extended period.
   - An action log record is created with action='extension_requested', actor=applicant_user, role_name='employee', and comments detailing original and extended dates.

Requirements:
Write two atomic Django service functions:
1. `cancel_approved_leave(leave_request, applicant_user, comments="")`:
   - Validates that applicant_user == leave_request.applicant.
   - Validates that leave_request.status == 'approved'.
   - Validates that timezone.now().date() <= leave_request.start_date.
   - Computes leave days debited using `calculate_leave_days`.
   - Updates `LeaveBalance`: `balance += days`, `used_days -= days`.
   - Updates `leave_request.status = 'cancelled'`.
   - Records `LeaveActionLog`.
   - Returns leave_request.

2. `request_leave_extension(leave_request, applicant_user, new_end_date, comments="")`:
   - Validates that applicant_user == leave_request.applicant.
   - Validates that leave_request.status == 'approved'.
   - Validates that new_end_date > leave_request.end_date.
   - Extension period starts at `leave_request.end_date + timezone.timedelta(days=1)` and ends at `new_end_date`.
   - Computes additional days for extension period.
   - Verifies sufficient balance in LeaveBalance.
   - Updates `leave_request.end_date = new_end_date`.
   - Updates `leave_request.status = 'pending_unit_head'`.
   - Records `LeaveActionLog` with action='extension_requested'.
   - Returns leave_request.

Output only clean, syntactically correct Python code with @transaction.atomic. Do not output markdown explanations.
```

#### 2. Engineering Audit & Changes
Generated `cancel_approved_leave` with automatic quota refunding to `LeaveBalance`, and `request_leave_extension` supporting continuous leave chaining and approval re-routing.

#### 3. Model Output
<details>
<summary>Click to view raw Qwen response</summary>

```
```python
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import LeaveRequest, LeaveBalance, LeaveActionLog

@transaction.atomic
def cancel_approved_leave(leave_request, applicant_user, comments=""):
    if leave_request.applicant != applicant_user:
        raise ValidationError("You are not authorized to cancel this leave request.")
    if leave_request.status != 'approved':
        raise ValidationError("This leave request is not approved.")
    if timezone.now().date() > leave_request.start_date:
        raise ValidationError("Cannot cancel a leave request that has already commenced or completed.")

    days = calculate_leave_days(leave_request.start_date, leave_request.end_date)
    balance = LeaveBalance.objects.get(user=applicant_user, leave_type=leave_request.leave_type, year=timezone.now().year)
    balance.balance += days
    balance.used_days -= days
    balance.save()

    leave_request.status = 'cancelled'
    leave_request.save()

    LeaveActionLog.objects.create(
        leave_request=leave_request,
        action='cancelled',
        actor=applicant_user,
        role_name='employee',
        comments=comments
    )

    return leave_request

@transaction.atomic
def request_leave_extension(leave_request, applicant_user, new_end_date, comments=""):
    if leave_request.applicant != applicant_user:
        raise ValidationError("You are not authorized to extend this leave request.")
    if leave_request.status != 'approved':
        raise ValidationError("This leave request is not approved.")
    if new_end_date <= leave_request.end_date:
        raise ValidationError("New end date must be greater than the current end date.")

    extension_start = leave_request.end_date + timezone.timedelta(days=1)
    additional_days = calculate_leave_days(extension_start, new_end_date)

    balance = LeaveBalance.objects.get(user=applicant_user, leave_type=leave_request.leave_type, year=timezone.now().year)
    if balance.balance < additional_days:
        raise ValidationError("Insufficient leave balance for the requested extension.")

    leave_request.end_date = new_end_date
    leave_request.status = 'pending_unit_head'
    leave_request.save()

    LeaveActionLog.objects.create(
        leave_request=leave_request,
        action='extension_requested',
        actor=applicant_user,
        role_name='employee',
        comments=f"Original End Date: {leave_request.end_date}, Extended End Date: {new_end_date}"
    )

    return leave_request
```
```

</details>

---

### Phase 2 - Sprint 4: Duty Resumption Workflow & Unconsumed Days Refund (BR-EL-027, BR-EL-028, EL-UC-010, EL-UC-011)
* **Execution Timestamp:** 2026-11-02 22:50:30
* **Prompt Tokens Evaluated:** 914
* **Output Tokens Generated:** 925
* **Generation Time:** 201.83 seconds (~4.58 tokens/sec)

#### 1. Requirements Dispatched to Qwen 2.5 Coder
```
You are a Senior Django Backend Engineer working on the Fusion ERP Employee Leave Management (ELM) module.
Implement Sprint 4: Duty Resumption Workflow & Unconsumed Days Refund (BR-EL-027, BR-EL-028, EL-UC-010, EL-UC-011).

Business Rules to Implement:
1. BR-EL-027 & EL-UC-010: Duty Resumption Submission:
   - When an employee returns to duty following approved leave, they must submit a Duty Resumption report.
   - The resumption_type is:
     * 'normal': if resumption_date == leave_request.end_date + timedelta(days=1)
     * 'early': if resumption_date <= leave_request.end_date
     * 'late': if resumption_date > leave_request.end_date + timedelta(days=1)
2. BR-EL-028 & EL-UC-011: Early Duty Resumption & Unconsumed Days Credit:
   - If resumption_type is 'early':
     * Calculate actual days availed from leave_request.start_date to (resumption_date - timedelta(days=1)). If resumption_date <= start_date, actual_days_availed = Decimal('0.0').
     * Calculate unconsumed days = total_original_days - actual_days_availed.
   - For 'normal' resumption: actual_days_availed = total_original_days, unconsumed_days = 0.
   - When Duty Resumption is approved:
     * If unconsumed_days > 0, atomically credit unconsumed_days back to applicant's LeaveBalance (balance += unconsumed_days, used_days -= unconsumed_days).
     * Set duty_resumption.status = 'approved'.
     * Set leave_request.status = 'completed'.
     * Log action in LeaveActionLog.

Requirements:
1. Define Django model `DutyResumption` inheriting from `core.db.mixins.TimeStampedModel`:
   - `leave_request`: OneToOneField(LeaveRequest, on_delete=models.CASCADE, related_name='duty_resumption')
   - `resumption_date`: models.DateField()
   - `resumption_type`: models.CharField(max_length=20, choices=[('normal', 'Normal'), ('early', 'Early'), ('late', 'Late')])
   - `prefix_suffix_details`: models.TextField(blank=True)
   - `actual_days_availed`: models.DecimalField(max_digits=5, decimal_places=1)
   - `refunded_days`: models.DecimalField(max_digits=5, decimal_places=1, default=0)
   - `status`: models.CharField(max_length=20, choices=[('submitted', 'Submitted'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='submitted')
   - `remarks`: models.TextField(blank=True)

2. Write Django service function `submit_duty_resumption(leave_request, applicant_user, resumption_date, prefix_suffix="", remarks="")`:
   - Validates applicant_user == leave_request.applicant.
   - Validates leave_request.status == 'approved'.
   - Computes total_original_days = calculate_leave_days(leave_request.start_date, leave_request.end_date, leave_request.leave_type.code, leave_request.half_day).
   - Determines resumption_type ('early', 'normal', or 'late').
   - Computes actual_days_availed and prospective refunded_days.
   - Creates DutyResumption record.
   - Logs action in LeaveActionLog.
   - Returns DutyResumption instance.

3. Write Django service function `approve_duty_resumption(duty_resumption, approver_user, role_name, comments="")`:
   - Validates duty_resumption.status == 'submitted'.
   - If duty_resumption.refunded_days > 0:
     * Updates applicant's LeaveBalance (balance.balance += refunded_days, balance.used_days -= refunded_days).
   - Sets duty_resumption.status = 'approved'.
   - Sets duty_resumption.leave_request.status = 'completed'.
   - Saves both models.
   - Logs action in LeaveActionLog.
   - Returns duty_resumption.

Output only clean, syntactically correct Python code with @transaction.atomic. Do not output markdown explanations.
```

#### 2. Engineering Audit & Changes
Generated `DutyResumption` model, `submit_duty_resumption` with classification (early/normal/late) and actual vs unconsumed day calculation, and `approve_duty_resumption` with atomic quota refunding and leave completion.

#### 3. Model Output
<details>
<summary>Click to view raw Qwen response</summary>

```
```python
from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import timedelta

from core.db.mixins import TimeStampedModel
from leave_management.models import LeaveRequest, LeaveBalance, LeaveActionLog

class DutyResumption(TimeStampedModel):
    leave_request = models.OneToOneField(LeaveRequest, on_delete=models.CASCADE, related_name='duty_resumption')
    resumption_date = models.DateField()
    resumption_type = models.CharField(max_length=20, choices=[('normal', 'Normal'), ('early', 'Early'), ('late', 'Late')])
    prefix_suffix_details = models.TextField(blank=True)
    actual_days_availed = models.DecimalField(max_digits=5, decimal_places=1)
    refunded_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    status = models.CharField(max_length=20, choices=[('submitted', 'Submitted'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='submitted')
    remarks = models.TextField(blank=True)

    def clean(self):
        if self.resumption_date < self.leave_request.start_date:
            raise ValidationError("Resumption date cannot be before the leave start date.")
        if self.resumption_date > self.leave_request.end_date + timedelta(days=1):
            raise ValidationError("Resumption date cannot be more than one day after the leave end date.")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.resumption_type = self._determine_resumption_type()
            self.actual_days_availed, self.refunded_days = self._calculate_days()
        super().save(*args, **kwargs)

    def _determine_resumption_type(self):
        if self.resumption_date == self.leave_request.end_date + timedelta(days=1):
            return 'normal'
        elif self.resumption_date <= self.leave_request.end_date:
            return 'early'
        else:
            return 'late'

    def _calculate_days(self):
        if self.resumption_type == 'early':
            start_date = self.leave_request.start_date
            end_date = self.resumption_date - timedelta(days=1)
            actual_days_availed = (end_date - start_date).days + 1 if end_date >= start_date else 0
        else:
            actual_days_availed = self.leave_request.total_original_days
        refunded_days = self.leave_request.total_original_days - actual_days_availed
        return Decimal(actual_days_availed), Decimal(refunded_days)

@transaction.atomic
def submit_duty_resumption(leave_request, applicant_user, resumption_date, prefix_suffix="", remarks=""):
    if leave_request.applicant != applicant_user:
        raise ValidationError("You are not authorized to submit this duty resumption.")
    if leave_request.status != 'approved':
        raise ValidationError("Leave request must be approved before submitting duty resumption.")

    duty_resumption = DutyResumption(
        leave_request=leave_request,
        resumption_date=resumption_date,
        prefix_suffix_details=prefix_suffix,
        remarks=remarks
    )
    duty_resumption.save()

    LeaveActionLog.objects.create(
        user=applicant_user,
        action_type='duty_resumption_submitted',
        leave_request=leave_request,
        details=f"Submitted duty resumption for {leave_request.start_date} to {leave_request.end_date}"
    )

    return duty_resumption

@transaction.atomic
def approve_duty_resumption(duty_resumption, approver_user, role_name, comments=""):
    if duty_resumption.status != 'submitted':
        raise ValidationError("Duty resumption must be submitted before approving.")

    duty_resumption.status = 'approved'
    duty_resumption.leave_request.status = 'completed'
    duty_resumption.save()

    if duty_resumption.refunded_days > 0:
        leave_balance = duty_resumption.leave_request.applicant.leave_balance
        leave_balance.balance += duty_resumption.refunded_days
        leave_balance.used_days -= duty_resumption.refunded_days
        leave_balance.save()

    LeaveActionLog.objects.create(
        user=approver_user,
        action_type='duty_resumption_approved',
        leave_request=duty_resumption.leave_request,
        details=f"Approved duty resumption for {duty_resumption.leave_request.start_date} to {duty_resumption.leave_request.end_date}"
    )

    return duty_resumption
```
```

</details>

---

### Phase 2 - Sprint 5: Year-End Rollover & Leave Lapse (BR-EL-006, BR-EL-007, BR-EL-008, EL-UC-020)
* **Execution Timestamp:** 2026-11-02 22:53:13
* **Prompt Tokens Evaluated:** 813
* **Output Tokens Generated:** 541
* **Generation Time:** 125.14 seconds (~4.32 tokens/sec)

#### 1. Requirements Dispatched to Qwen 2.5 Coder
```
You are a Senior Django Backend Engineer working on the Fusion ERP Employee Leave Management (ELM) module.
Implement Sprint 5: Year-End Rollover & Leave Lapse Service (BR-EL-006, BR-EL-007, BR-EL-008, EL-UC-020).

Business Rules to Implement:
1. BR-EL-008: Lapsing of Casual Leave (CL) and Restricted Holiday (RH):
   - Unavailed balances for CL and RH at the end of the year do not carry forward. They lapse completely.
   - For the new year (target_year), users receive their fresh annual quota (e.g. 8 days for CL, 2 days for RH).
2. BR-EL-007: 50% Vacation Leave (VL) Rollover to Earned Leave (EL):
   - For users with VL entitlement, 50% of the unavailed VL balance (int(vl_balance * 0.5)) is converted into Earned Leave (EL) for the new year.
   - The remaining 50% of VL lapses. Fresh annual quota of VL is allocated for the new year.
3. BR-EL-006: Earned Leave (EL) Maximum Accumulation Ceiling:
   - Earned Leave carries forward. The new year's EL balance is calculated as:
     carried_el = previous_year_el_balance + converted_vl_days + annual_el_quota
   - The total accumulated EL balance cannot exceed 300 days.
   - If carried_el > 300, cap it at Decimal('300.0').
4. The service must process all active users atomically and create or update `LeaveBalance` records for `target_year`.

Requirements:
Write a Django service function `process_year_end_rollover(current_year, target_year=None)`:
- If target_year is None, target_year = current_year + 1.
- Uses @transaction.atomic.
- Iterates over all users who have LeaveBalance records in `current_year`.
- For each user:
  a) Fetches current_year balances for 'CL', 'RH', 'EL', 'VL'.
  b) Calculates 50% converted VL: `converted_vl = Decimal(int(vl_balance.balance * Decimal('0.5')))` if VL exists, else 0.
  c) Computes new EL balance: `el_carry = el_balance.balance + converted_vl + el_type.annual_quota`.
     If `el_carry > Decimal('300.0')`: `el_carry = Decimal('300.0')`.
     Creates or updates LeaveBalance for (user, 'EL', target_year) with credited_days=el_carry, used_days=0, balance=el_carry.
  d) For CL: creates or updates LeaveBalance for (user, 'CL', target_year) with credited_days=cl_type.annual_quota, used_days=0, balance=cl_type.annual_quota.
  e) For RH: creates or updates LeaveBalance for (user, 'RH', target_year) with credited_days=rh_type.annual_quota, used_days=0, balance=rh_type.annual_quota.
  f) For VL (if user has VL): creates or updates LeaveBalance for (user, 'VL', target_year) with credited_days=vl_type.annual_quota, used_days=0, balance=vl_type.annual_quota.
- Returns a summary dictionary: `{"processed_users_count": count, "target_year": target_year}`.

Output only clean, syntactically correct Python code with @transaction.atomic. Do not output markdown explanations.
```

#### 2. Engineering Audit & Changes
Generated `process_year_end_rollover` enforcing CL/RH expiration, 50% Vacation Leave (VL) rollover into Earned Leave (EL), and strict 300-day statutory ceiling enforcement for EL accumulation.

#### 3. Model Output
<details>
<summary>Click to view raw Qwen response</summary>

```
```python
from django.db import transaction
from decimal import Decimal
from .models import LeaveBalance, LeaveType, User

@transaction.atomic
def process_year_end_rollover(current_year, target_year=None):
    if target_year is None:
        target_year = current_year + 1

    processed_users_count = 0

    for user in User.objects.filter(leavebalance__year=current_year).distinct():
        processed_users_count += 1

        cl_type = LeaveType.objects.get(code='CL')
        rh_type = LeaveType.objects.get(code='RH')
        el_type = LeaveType.objects.get(code='EL')
        vl_type = LeaveType.objects.get(code='VL')

        cl_balance = user.leavebalance_set.get(year=current_year, leave_type=cl_type)
        rh_balance = user.leavebalance_set.get(year=current_year, leave_type=rh_type)
        el_balance = user.leavebalance_set.get(year=current_year, leave_type=el_type)
        vl_balance = user.leavebalance_set.get(year=current_year, leave_type=vl_type) if user.leavebalance_set.filter(year=current_year, leave_type=vl_type).exists() else None

        converted_vl = Decimal(int(vl_balance.balance * Decimal('0.5'))) if vl_balance else Decimal('0.0')
        el_carry = el_balance.balance + converted_vl + el_type.annual_quota
        el_carry = min(el_carry, Decimal('300.0'))

        LeaveBalance.objects.update_or_create(
            user=user,
            leave_type=el_type,
            year=target_year,
            defaults={'credited_days': el_carry, 'used_days': 0, 'balance': el_carry}
        )

        LeaveBalance.objects.update_or_create(
            user=user,
            leave_type=cl_type,
            year=target_year,
            defaults={'credited_days': cl_type.annual_quota, 'used_days': 0, 'balance': cl_type.annual_quota}
        )

        LeaveBalance.objects.update_or_create(
            user=user,
            leave_type=rh_type,
            year=target_year,
            defaults={'credited_days': rh_type.annual_quota, 'used_days': 0, 'balance': rh_type.annual_quota}
        )

        if vl_balance:
            LeaveBalance.objects.update_or_create(
                user=user,
                leave_type=vl_type,
                year=target_year,
                defaults={'credited_days': vl_type.annual_quota, 'used_days': 0, 'balance': vl_type.annual_quota}
            )

    return {"processed_users_count": processed_users_count, "target_year": target_year}
```
```

</details>

---
