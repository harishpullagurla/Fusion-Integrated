from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import timedelta, date
from django.utils import timezone

from modules.elm.models import LeaveType, LeaveBalance, LeaveRequest, LeaveActionLog, HolidayCalendar, DutyResumption
from modules.directory.models import UserRef

def calculate_leave_days(start_date, end_date, leave_type_code='EL', half_day=False):
    """
    BR-EL-011: Counting of Leave Days.
    - If half_day is True: exactly 0.5 days.
    - If leave_type_code == 'CL': Intervening Sundays and Gazetted Holidays do NOT count.
    - For EL, VL, COMMUTED, SPECIAL: Continuous calendar days count (Sundays and holidays count).
    """
    if half_day:
        return Decimal('0.5')

    if start_date > end_date:
        raise ValidationError("start_date cannot be greater than end_date.")

    if leave_type_code == 'CL':
        # Batch load gazetted holidays in the date range to avoid N+1 queries
        gazetted_dates = set(
            HolidayCalendar.objects.filter(
                date__range=(start_date, end_date),
                holiday_type='gazetted'
            ).values_list('date', flat=True)
        )
        working_days = 0
        total_span = (end_date - start_date).days + 1
        for day in range(total_span):
            cur = start_date + timedelta(days=day)
            # Sunday is weekday 6
            if cur.weekday() != 6 and cur not in gazetted_dates:
                working_days += 1
        return Decimal(str(working_days))

    # Standard continuous counting
    total_days = (end_date - start_date).days + 1
    return Decimal(str(total_days))

def check_leave_balance(user, leave_type, requested_days, year=None):
    if year is None:
        year = timezone.now().year
    balance = LeaveBalance.objects.filter(user=user, leave_type=leave_type, year=year).first()
    if balance and balance.balance >= requested_days:
        return True, balance
    else:
        return False, "Insufficient leave balance"

def check_overlapping_leave(user, start_date, end_date, half_day=False, half_day_period=None, exclude_request_id=None):
    active_statuses = ['approved', 'pending_unit_head', 'pending_higher_sanction', 'awaiting_substitute']
    overlapping_requests = LeaveRequest.objects.filter(
        applicant=user,
        status__in=active_statuses,
        start_date__lte=end_date,
        end_date__gte=start_date
    )
    if exclude_request_id:
        overlapping_requests = overlapping_requests.exclude(id=exclude_request_id)
    
    if half_day and half_day_period:
        # Check if another half-day leave exists on the same period
        return overlapping_requests.filter(
            half_day=True,
            half_day_period=half_day_period
        ).exists()

    return overlapping_requests.exists()

def validate_leave_application(applicant, leave_type, start_date, end_date, half_day=False, station_leave=False, station_leave_address=""):
    """
    Validates institutional leave rules:
    - BR-EL-012: CL continuous span cannot exceed 8 days.
    - BR-EL-003 / BR-EL-031: RH must be a single day and must exist as a declared Restricted Holiday.
    - BR-EL-014: Station leave requires non-empty destination/address.
    """
    if start_date > end_date:
        return False, "Start date must be before or equal to end date."

    if leave_type.code == 'CL':
        continuous_span = (end_date - start_date).days + 1
        if continuous_span > 8:
            return False, "Casual Leave cannot exceed 8 continuous calendar days (BR-EL-012)."

    if leave_type.code == 'RH':
        if start_date != end_date:
            return False, "Restricted Holiday can only be availed for a single day (BR-EL-003)."
        if not HolidayCalendar.objects.filter(date=start_date, holiday_type='restricted').exists():
            return False, "Selected date is not a declared Restricted Holiday in the academic calendar (BR-EL-031)."

    if station_leave and not (station_leave_address and station_leave_address.strip()):
        return False, "Station leave address must be provided when availing station leave (BR-EL-014)."

    return True, None

@transaction.atomic
def submit_leave_request(applicant, leave_type, start_date, end_date, purpose,
                         half_day=False, half_day_period=None, station_leave=False,
                         station_leave_address="", substitute=None):
    """
    Submits a leave request with institutional validations.
    If substitute is nominated, status is 'awaiting_substitute'.
    Otherwise enters 'pending_unit_head'.
    """
    is_valid, error = validate_leave_application(
        applicant, leave_type, start_date, end_date,
        half_day=half_day, station_leave=station_leave,
        station_leave_address=station_leave_address
    )
    if not is_valid:
        raise ValidationError(error)

    if check_overlapping_leave(applicant, start_date, end_date, half_day, half_day_period):
        raise ValidationError("Applicant already has an active or approved leave application covering this interval.")

    requested_days = calculate_leave_days(start_date, end_date, leave_type.code, half_day=half_day)
    has_balance, balance_or_msg = check_leave_balance(applicant, leave_type, requested_days, year=start_date.year)
    if not has_balance:
        raise ValidationError(f"Insufficient leave balance: requested {requested_days} days, but balance is unavailable.")

    if substitute:
        if substitute == applicant:
            raise ValidationError("Applicant cannot nominate themselves as their own substitute.")
        initial_status = 'awaiting_substitute'
        sub_status = 'pending'
    else:
        initial_status = 'pending_unit_head'
        sub_status = 'pending'

    leave_request = LeaveRequest.objects.create(
        applicant=applicant,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        purpose=purpose,
        half_day=half_day,
        half_day_period=half_day_period,
        station_leave=station_leave,
        station_leave_address=station_leave_address.strip() if station_leave else "",
        substitute=substitute,
        substitute_status=sub_status,
        status=initial_status
    )

    LeaveActionLog.objects.create(
        leave_request=leave_request,
        actor=applicant,
        role_name='employee',
        action='submitted',
        comments="Leave application submitted."
    )
    return leave_request

@transaction.atomic
def respond_substitute(leave_request, substitute_user, decision, comments=""):
    """
    BR-EL-015: Substitute workflow.
    - If decision == 'accept': substitute_status='accepted', transitions to 'pending_unit_head'.
    - If decision == 'decline': substitute_status='declined', transitions to 'substitute_declined'.
    """
    if leave_request.substitute != substitute_user:
        raise ValidationError("Unauthorized: user is not the nominated substitute for this request.")
    if leave_request.status != 'awaiting_substitute':
        raise ValidationError("Leave request is not awaiting substitute response.")

    if decision == 'accept':
        leave_request.substitute_status = 'accepted'
        leave_request.status = 'pending_unit_head'
        action_name = 'substitute_accepted'
    elif decision == 'decline':
        leave_request.substitute_status = 'declined'
        leave_request.status = 'substitute_declined'
        action_name = 'substitute_declined'
    else:
        raise ValidationError("Invalid substitute decision. Must be 'accept' or 'decline'.")

    leave_request.save()
    LeaveActionLog.objects.create(
        leave_request=leave_request,
        actor=substitute_user,
        role_name='substitute',
        action=action_name,
        comments=comments
    )
    return leave_request

@transaction.atomic
def renominate_substitute(leave_request, applicant_user, new_substitute_user, comments=""):
    """
    EL-UC-019: Substitute decline recovery and re-nomination.
    """
    if leave_request.applicant != applicant_user:
        raise ValidationError("Unauthorized: only the applicant can re-nominate a substitute.")
    if leave_request.status != 'substitute_declined':
        raise ValidationError("Leave request substitute has not declined.")
    if new_substitute_user == applicant_user:
        raise ValidationError("Cannot nominate yourself as substitute.")

    leave_request.substitute = new_substitute_user
    leave_request.substitute_status = 'pending'
    leave_request.status = 'awaiting_substitute'
    leave_request.save()

    LeaveActionLog.objects.create(
        leave_request=leave_request,
        actor=applicant_user,
        role_name='employee',
        action='substitute_renominated',
        comments=comments or f"Re-nominated substitute {new_substitute_user.id}."
    )
    return leave_request

@transaction.atomic
def process_approval(leave_request, actor_user, role_name, action, comments=""):
    """
    Handles sanctioning authority actions: 'recommend', 'approve', 'reject'.
    When 'approve' is invoked, debits the applicant's LeaveBalance.
    """
    if action == 'recommend':
        leave_request.status = 'pending_higher_sanction'
    elif action == 'approve':
        leave_request.status = 'approved'
        requested_days = calculate_leave_days(
            leave_request.start_date, leave_request.end_date,
            leave_request.leave_type.code, leave_request.half_day
        )
        balance_obj = LeaveBalance.objects.select_for_update().get(
            user=leave_request.applicant,
            leave_type=leave_request.leave_type,
            year=leave_request.start_date.year
        )
        if balance_obj.balance < requested_days:
            raise ValidationError(f"Cannot approve: applicant balance {balance_obj.balance} < {requested_days}.")
        balance_obj.used_days += requested_days
        balance_obj.balance -= requested_days
        balance_obj.save()
    elif action == 'reject':
        leave_request.status = 'rejected'
    else:
        raise ValidationError(f"Unknown action: {action}")

    leave_request.save()
    LeaveActionLog.objects.create(
        leave_request=leave_request,
        actor=actor_user,
        role_name=role_name,
        action=action,
        comments=comments
    )
    return leave_request

@transaction.atomic
def withdraw_leave_request(leave_request, applicant_user, comments=""):
    """
    Withdraws a pending leave request before sanction.
    """
    if leave_request.applicant != applicant_user:
        raise ValidationError("Unauthorized: only the applicant can withdraw this request.")
    if leave_request.status in ['approved', 'rejected', 'withdrawn', 'cancelled', 'completed']:
        raise ValidationError(f"Cannot withdraw request in '{leave_request.status}' status.")

    leave_request.status = 'withdrawn'
    leave_request.save()

    LeaveActionLog.objects.create(
        leave_request=leave_request,
        actor=applicant_user,
        role_name='employee',
        action='withdrawn',
        comments=comments
    )
    return leave_request

@transaction.atomic
def cancel_approved_leave(leave_request, applicant_user, comments=""):
    """
    BR-EL-023 & EL-UC-008: Approved leave cancellation prior to commencement.
    Refunds debited days back to applicant's LeaveBalance atomically.
    """
    if leave_request.applicant != applicant_user:
        raise ValidationError("Unauthorized: only the applicant can cancel this leave.")
    if leave_request.status != 'approved':
        raise ValidationError("Only approved leave requests can be cancelled.")
    
    current_date = timezone.now().date()
    if current_date > leave_request.start_date:
        raise ValidationError("Cannot cancel leave after commencement date (submit Duty Resumption instead).")

    days = calculate_leave_days(
        leave_request.start_date, leave_request.end_date,
        leave_request.leave_type.code, leave_request.half_day
    )
    balance_obj = LeaveBalance.objects.select_for_update().get(
        user=applicant_user,
        leave_type=leave_request.leave_type,
        year=leave_request.start_date.year
    )
    balance_obj.balance += days
    balance_obj.used_days -= days
    balance_obj.save()

    leave_request.status = 'cancelled'
    leave_request.save()

    LeaveActionLog.objects.create(
        leave_request=leave_request,
        actor=applicant_user,
        role_name='employee',
        action='cancelled',
        comments=comments or "Approved leave cancelled prior to start date; quota refunded."
    )
    return leave_request

@transaction.atomic
def request_leave_extension(leave_request, applicant_user, new_end_date, comments=""):
    """
    BR-EL-025 & EL-UC-009: Ongoing leave extension chaining.
    """
    if leave_request.applicant != applicant_user:
        raise ValidationError("Unauthorized: only the applicant can extend this leave.")
    if leave_request.status != 'approved':
        raise ValidationError("Only approved leaves can be extended.")
    if new_end_date <= leave_request.end_date:
        raise ValidationError("new_end_date must be strictly greater than current end_date.")

    extension_start = leave_request.end_date + timedelta(days=1)
    additional_days = calculate_leave_days(
        extension_start, new_end_date,
        leave_request.leave_type.code, half_day=False
    )

    balance_obj = LeaveBalance.objects.get(
        user=applicant_user,
        leave_type=leave_request.leave_type,
        year=leave_request.start_date.year
    )
    if balance_obj.balance < additional_days:
        raise ValidationError(f"Insufficient leave balance for extension: need {additional_days}, available {balance_obj.balance}.")

    old_end_date = leave_request.end_date
    leave_request.end_date = new_end_date
    leave_request.status = 'pending_unit_head'
    leave_request.save()

    LeaveActionLog.objects.create(
        leave_request=leave_request,
        actor=applicant_user,
        role_name='employee',
        action='extension_requested',
        comments=comments or f"Leave extended from {old_end_date} to {new_end_date} (+{additional_days} days). Re-submitted for approval."
    )
    return leave_request

@transaction.atomic
def submit_duty_resumption(leave_request, applicant_user, resumption_date, prefix_suffix="", remarks=""):
    """
    BR-EL-027 & EL-UC-010: Submitting duty resumption.
    Determines normal, early, or late resumption.
    Calculates actual days availed vs unconsumed days to refund.
    """
    if leave_request.applicant != applicant_user:
        raise ValidationError("Unauthorized: only the applicant can submit duty resumption.")
    if leave_request.status != 'approved':
        raise ValidationError("Duty resumption can only be submitted for approved leaves.")
    if hasattr(leave_request, 'duty_resumption'):
        raise ValidationError("Duty resumption has already been submitted for this leave.")

    total_original_days = calculate_leave_days(
        leave_request.start_date, leave_request.end_date,
        leave_request.leave_type.code, leave_request.half_day
    )

    expected_normal_resumption = leave_request.end_date + timedelta(days=1)
    if resumption_date < expected_normal_resumption:
        resumption_type = 'early'
        if resumption_date <= leave_request.start_date:
            actual_days = Decimal('0.0')
        else:
            actual_end = resumption_date - timedelta(days=1)
            actual_days = calculate_leave_days(
                leave_request.start_date, actual_end,
                leave_request.leave_type.code, leave_request.half_day
            )
        refunded_days = max(Decimal('0.0'), total_original_days - actual_days)
    elif resumption_date == expected_normal_resumption:
        resumption_type = 'normal'
        actual_days = total_original_days
        refunded_days = Decimal('0.0')
    else:
        resumption_type = 'late'
        actual_days = total_original_days
        refunded_days = Decimal('0.0')

    resumption = DutyResumption.objects.create(
        leave_request=leave_request,
        resumption_date=resumption_date,
        resumption_type=resumption_type,
        prefix_suffix_details=prefix_suffix,
        actual_days_availed=actual_days,
        refunded_days=refunded_days,
        status='submitted',
        remarks=remarks
    )

    LeaveActionLog.objects.create(
        leave_request=leave_request,
        actor=applicant_user,
        role_name='employee',
        action='resumption_submitted',
        comments=f"Duty resumption submitted on {resumption_date} ({resumption_type}). Refundable: {refunded_days} days."
    )
    return resumption

@transaction.atomic
def approve_duty_resumption(duty_resumption, approver_user, role_name='admin', comments=""):
    """
    BR-EL-028 & EL-UC-011: Approving duty resumption.
    Atomically credits unconsumed days to applicant balance and marks request completed.
    """
    if duty_resumption.status != 'submitted':
        raise ValidationError(f"Resumption already {duty_resumption.status}.")

    leave_request = duty_resumption.leave_request
    if duty_resumption.refunded_days > Decimal('0.0'):
        balance_obj = LeaveBalance.objects.select_for_update().get(
            user=leave_request.applicant,
            leave_type=leave_request.leave_type,
            year=leave_request.start_date.year
        )
        balance_obj.balance += duty_resumption.refunded_days
        balance_obj.used_days -= duty_resumption.refunded_days
        balance_obj.save()

    duty_resumption.status = 'approved'
    duty_resumption.save()

    leave_request.status = 'completed'
    leave_request.save()

    LeaveActionLog.objects.create(
        leave_request=leave_request,
        actor=approver_user,
        role_name=role_name,
        action='resumption_approved',
        comments=comments or f"Duty resumption approved. Refunded {duty_resumption.refunded_days} days."
    )
    return duty_resumption

@transaction.atomic
def process_year_end_rollover(current_year, target_year=None):
    """
    BR-EL-006, BR-EL-007, BR-EL-008, EL-UC-020:
    - Casual Leave (CL) and Restricted Holiday (RH) lapse and do not carry forward.
    - 50% of unavailed Vacation Leave (VL) converts to Earned Leave (EL).
    - Earned Leave carries forward, subject to statutory 300-day accumulation cap.
    - Fresh yearly allocations granted for target_year.
    """
    if target_year is None:
        target_year = current_year + 1

    cl_type = LeaveType.objects.get(code='CL')
    rh_type = LeaveType.objects.get(code='RH')
    el_type = LeaveType.objects.get(code='EL')
    vl_type = LeaveType.objects.filter(code='VL').first()

    distinct_users = UserRef.objects.filter(leave_balances__year=current_year).distinct()
    processed_count = 0

    for user in distinct_users:
        processed_count += 1
        cl_bal = LeaveBalance.objects.filter(user=user, leave_type=cl_type, year=current_year).first()
        rh_bal = LeaveBalance.objects.filter(user=user, leave_type=rh_type, year=current_year).first()
        el_bal = LeaveBalance.objects.filter(user=user, leave_type=el_type, year=current_year).first()
        vl_bal = LeaveBalance.objects.filter(user=user, leave_type=vl_type, year=current_year).first() if vl_type else None

        # 1. 50% VL Rollover into EL (BR-EL-007)
        converted_vl = Decimal('0.0')
        if vl_bal and vl_bal.balance > Decimal('0.0'):
            converted_vl = Decimal(str(int(vl_bal.balance * Decimal('0.5'))))

        # 2. EL Rollover with 300-day statutory ceiling (BR-EL-006)
        prev_el_balance = el_bal.balance if el_bal else Decimal('0.0')
        new_el_credit = prev_el_balance + converted_vl + el_type.annual_quota
        capped_el = min(new_el_credit, Decimal('300.0'))

        LeaveBalance.objects.update_or_create(
            user=user,
            leave_type=el_type,
            year=target_year,
            defaults={
                'credited_days': capped_el,
                'used_days': Decimal('0.0'),
                'balance': capped_el
            }
        )

        # 3. CL Lapsing & Fresh Allotment (BR-EL-008)
        LeaveBalance.objects.update_or_create(
            user=user,
            leave_type=cl_type,
            year=target_year,
            defaults={
                'credited_days': cl_type.annual_quota,
                'used_days': Decimal('0.0'),
                'balance': cl_type.annual_quota
            }
        )

        # 4. RH Lapsing & Fresh Allotment (BR-EL-008)
        LeaveBalance.objects.update_or_create(
            user=user,
            leave_type=rh_type,
            year=target_year,
            defaults={
                'credited_days': rh_type.annual_quota,
                'used_days': Decimal('0.0'),
                'balance': rh_type.annual_quota
            }
        )

        # 5. VL Fresh Allotment (if applicable)
        if vl_type and vl_bal:
            LeaveBalance.objects.update_or_create(
                user=user,
                leave_type=vl_type,
                year=target_year,
                defaults={
                    'credited_days': vl_type.annual_quota,
                    'used_days': Decimal('0.0'),
                    'balance': vl_type.annual_quota
                }
            )

    return {
        "processed_users_count": processed_count,
        "current_year": current_year,
        "target_year": target_year
    }
