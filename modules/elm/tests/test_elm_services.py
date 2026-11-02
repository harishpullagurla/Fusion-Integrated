from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from modules.directory.models import UserRef
from modules.elm.models import LeaveType, LeaveBalance, LeaveRequest, LeaveActionLog
from modules.elm.services.leave_service import (
    calculate_leave_days,
    check_leave_balance,
    check_overlapping_leave,
    submit_leave_request,
    respond_substitute,
    process_approval,
    withdraw_leave_request,
)


class ElmServicesTestCase(TestCase):
    def setUp(self):
        # Create test users in directory
        self.employee = UserRef.objects.create(
            user_id=101,
            username="emp101",
            display_name="Employee One",
            kind="faculty",
            discipline="CSE"
        )
        self.substitute = UserRef.objects.create(
            user_id=102,
            username="emp102",
            display_name="Employee Two",
            kind="faculty",
            discipline="CSE"
        )
        self.unit_head = UserRef.objects.create(
            user_id=103,
            username="head_cse",
            display_name="HoD CSE",
            kind="faculty",
            discipline="CSE"
        )

        # Create leave types
        self.cl_type = LeaveType.objects.create(
            code="CL",
            name="Casual Leave",
            annual_quota=Decimal("8.0"),
            is_vacation=False,
            max_continuous_days=3
        )
        self.el_type = LeaveType.objects.create(
            code="EL",
            name="Earned Leave",
            annual_quota=Decimal("30.0"),
            is_vacation=False,
            max_continuous_days=30
        )

        # Create initial balances
        self.cl_balance = LeaveBalance.objects.create(
            user=self.employee,
            leave_type=self.cl_type,
            year=date.today().year,
            credited_days=Decimal("8.0"),
            used_days=Decimal("0.0"),
            balance=Decimal("8.0")
        )

    def test_calculate_leave_days(self):
        start = date(2026, 11, 10)
        end = date(2026, 11, 12)
        # Full 3 days
        days = calculate_leave_days(start, end, half_day=False)
        self.assertEqual(days, 3)

        # Half day
        half_days = calculate_leave_days(start, start, half_day=True)
        self.assertEqual(half_days, Decimal("0.5"))

    def test_check_leave_balance_sufficient_and_insufficient(self):
        # Sufficient check
        ok, bal = check_leave_balance(self.employee, self.cl_type, Decimal("2.0"))
        self.assertTrue(ok)

        # Insufficient check
        ok_fail, msg = check_leave_balance(self.employee, self.cl_type, Decimal("10.0"))
        self.assertFalse(ok_fail)
        self.assertIn("Insufficient", msg)

    def test_submit_and_withdraw_request(self):
        start = date(2026, 11, 15)
        end = date(2026, 11, 16)
        req = submit_leave_request(
            applicant=self.employee,
            leave_type=self.cl_type,
            start_date=start,
            end_date=end,
            purpose="Family emergency",
            substitute=self.substitute
        )
        self.assertIsNotNone(req.id)
        # Check audit log
        action_log = LeaveActionLog.objects.filter(leave_request=req).first()
        self.assertEqual(action_log.action, "submitted")

        # Withdraw request (BR-EL-022)
        withdrawn_req = withdraw_leave_request(req, self.employee, "Withdrawn by applicant")
        self.assertEqual(withdrawn_req.status, "withdrawn")

    def test_substitute_consent_gate(self):
        req = submit_leave_request(
            applicant=self.employee,
            leave_type=self.cl_type,
            start_date=date(2026, 11, 20),
            end_date=date(2026, 11, 21),
            purpose="Conference",
            substitute=self.substitute
        )
        # Substitute accepts
        accepted_req = respond_substitute(req, self.substitute, "accept", "I will cover lectures")
        self.assertEqual(accepted_req.status, "approved")

    def test_process_approval_and_balance_deduction(self):
        req = submit_leave_request(
            applicant=self.employee,
            leave_type=self.cl_type,
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 2),
            purpose="Personal work"
        )
        # 2 days approved by Unit Head
        process_approval(req, self.unit_head, "unit_head", "approve", "Approved by HoD")

        # Verify status
        req.refresh_from_db()
        self.assertEqual(req.status, "approved")

        # Verify atomic balance deduction
        self.cl_balance.refresh_from_db()
        self.assertEqual(self.cl_balance.used_days, Decimal("2.0"))
        self.assertEqual(self.cl_balance.balance, Decimal("6.0"))
