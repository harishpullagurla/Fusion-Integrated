from django.db import transaction
from django.db.models import Q
from decimal import Decimal
from modules.elm.models import LeaveType, LeaveBalance, LeaveRequest, LeaveActionLog
from django.utils import timezone

def calculate_leave_days(start_date, end_date, half_day=False):
    if half_day:
        return Decimal('0.5')
    else:
        return (end_date - start_date).days + 1

def check_leave_balance(user, leave_type, requested_days, year=None):
    if year is None:
        year = timezone.now().year
    balance = LeaveBalance.objects.filter(user=user, leave_type=leave_type, year=year).first()
    if balance and balance.balance >= requested_days:
        return True, balance
    else:
        return False, "Insufficient leave balance"

def check_overlapping_leave(user, start_date, end_date, half_day=False, half_day_period=None, exclude_request_id=None):
    overlapping_requests = LeaveRequest.objects.filter(
        user=user,
        status='approved',
        start_date__lte=end_date,
        end_date__gte=start_date
    )
    if exclude_request_id:
        overlapping_requests = overlapping_requests.exclude(id=exclude_request_id)
    if half_day:
        if half_day_period == 'morning':
            overlapping_requests = overlapping_requests.filter(
                (Q(start_date=start_date, end_date=start_date) & Q(half_day=True, half_day_period='morning')) |
                (Q(start_date=start_date, end_date__gt=start_date) & Q(half_day=True, half_day_period='morning'))
            )
        elif half_day_period == 'afternoon':
            overlapping_requests = overlapping_requests.filter(
                (Q(start_date=start_date, end_date=start_date) & Q(half_day=True, half_day_period='afternoon')) |
                (Q(start_date__lt=start_date, end_date=start_date) & Q(half_day=True, half_day_period='afternoon'))
            )
    return overlapping_requests.exists()

@transaction.atomic
def submit_leave_request(applicant, leave_type, start_date, end_date, purpose, half_day=False, half_day_period=None, station_leave=False, station_leave_address="", substitute=None):
    leave_request = LeaveRequest.objects.create(
        applicant=applicant,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        purpose=purpose,
        half_day=half_day,
        half_day_period=half_day_period,
        station_leave=station_leave,
        station_leave_address=station_leave_address,
        substitute=substitute
    )
    LeaveActionLog.objects.create(
        leave_request=leave_request,
        actor=applicant,
        role_name='employee',
        action='submitted'
    )
    return leave_request

@transaction.atomic
def respond_substitute(leave_request, substitute_user, decision, comments=""):
    if decision == 'accept':
        leave_request.substitute = substitute_user
        leave_request.status = 'approved'
    elif decision == 'decline':
        leave_request.status = 'rejected'
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
def process_approval(leave_request, actor_user, role_name, action, comments=""):
    if action == 'recommend':
        leave_request.status = 'recommended'
    elif action == 'approve':
        leave_request.status = 'approved'
        leave_type = leave_request.leave_type
        requested_days = calculate_leave_days(leave_request.start_date, leave_request.end_date, leave_request.half_day)
        balance_obj = LeaveBalance.objects.get(user=leave_request.applicant, leave_type=leave_type, year=timezone.now().year)
        balance_obj.used_days += requested_days
        balance_obj.balance -= requested_days
        balance_obj.save()
    elif action == 'reject':
        leave_request.status = 'rejected'
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