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

    def __str__(self):
        return f"{self.code} - {self.name}"

class HolidayCalendar(TimeStampedModel):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=150)
    holiday_type = models.CharField(max_length=20, choices=[('gazetted', 'Gazetted Holiday'), ('restricted', 'Restricted Holiday')])
    academic_year = models.IntegerField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.date} ({self.holiday_type}): {self.name}"

class LeaveBalance(TimeStampedModel):
    user = models.ForeignKey(UserRef, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.IntegerField()
    credited_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    used_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    balance = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    class Meta:
        unique_together = ('user', 'leave_type', 'year')

    def __str__(self):
        return f"{self.user_id} - {self.leave_type_id} ({self.year}): {self.balance} left"

class LeaveRequest(TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('awaiting_substitute', 'Awaiting Substitute Response'),
        ('substitute_declined', 'Substitute Declined'),
        ('pending_unit_head', 'Pending Unit Head Review'),
        ('pending_higher_sanction', 'Pending Higher Sanction'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    SUBSTITUTE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

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
    substitute_status = models.CharField(max_length=20, choices=SUBSTITUTE_STATUS_CHOICES, default='pending')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_unit_head')

    def __str__(self):
        return f"Req #{self.id} by {self.applicant_id} ({self.leave_type_id}): {self.status}"

class DutyResumption(TimeStampedModel):
    RESUMPTION_TYPE_CHOICES = [
        ('normal', 'Normal Resumption'),
        ('early', 'Early Resumption'),
        ('late', 'Late Resumption'),
    ]
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    leave_request = models.OneToOneField(LeaveRequest, on_delete=models.CASCADE, related_name='duty_resumption')
    resumption_date = models.DateField()
    resumption_type = models.CharField(max_length=20, choices=RESUMPTION_TYPE_CHOICES)
    prefix_suffix_details = models.TextField(blank=True)
    actual_days_availed = models.DecimalField(max_digits=5, decimal_places=1)
    refunded_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Resumption for Req #{self.leave_request_id} ({self.resumption_type}): {self.status}"

class LeaveActionLog(TimeStampedModel):
    ACTION_CHOICES = [
        ('submitted', 'Submitted'),
        ('substitute_accepted', 'Substitute Accepted'),
        ('substitute_declined', 'Substitute Declined'),
        ('substitute_renominated', 'Substitute Re-Nominated'),
        ('recommended', 'Recommended'),
        ('not_recommended', 'Not Recommended'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
        ('cancelled', 'Cancelled'),
        ('extension_requested', 'Extension Requested'),
        ('resumption_submitted', 'Resumption Submitted'),
        ('resumption_approved', 'Resumption Approved'),
    ]

    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name='action_logs')
    actor = models.ForeignKey(UserRef, on_delete=models.CASCADE)
    role_name = models.CharField(max_length=50)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"Req #{self.leave_request_id} - {self.action} by {self.actor_id}"
