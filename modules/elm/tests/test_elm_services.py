from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError

from modules.directory.models import UserRef
from modules.elm.models import LeaveType, LeaveBalance, LeaveRequest, LeaveActionLog, HolidayCalendar, DutyResumption
from modules.elm.services.leave_service import (
    calculate_leave_days,
    check_leave_balance,
    check_overlapping_leave,
    validate_leave_application,
    submit_leave_request,
    respond_substitute,
    renominate_substitute,
    process_approval,
    withdraw_leave_request,
    cancel_approved_leave,
    request_leave_extension,
    submit_duty_resumption,
    approve_duty_resumption,
    process_year_end_rollover,
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
        self.substitute_alt = UserRef.objects.create(
            user_id=104,
            username="emp104",
            display_name="Employee Four",
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
            max_continuous_days=8
        )
        self.rh_type = LeaveType.objects.create(
            code="RH",
            name="Restricted Holiday",
            annual_quota=Decimal("2.0"),
            is_vacation=False,
            max_continuous_days=1
        )
        self.el_type = LeaveType.objects.create(
            code="EL",
            name="Earned Leave",
            annual_quota=Decimal("30.0"),
            is_vacation=False,
            max_continuous_days=30
        )
        self.vl_type = LeaveType.objects.create(
            code="VL",
            name="Vacation Leave",
            annual_quota=Decimal("60.0"),
            is_vacation=True,
            max_continuous_days=60
        )

        # Create initial balances for current year
        self.current_year = date.today().year
        self.cl_balance = LeaveBalance.objects.create(
            user=self.employee,
            leave_type=self.cl_type,
            year=self.current_year,
            credited_days=Decimal("8.0"),
            used_days=Decimal("0.0"),
            balance=Decimal("8.0")
        )
        self.rh_balance = LeaveBalance.objects.create(
            user=self.employee,
            leave_type=self.rh_type,
            year=self.current_year,
            credited_days=Decimal("2.0"),
            used_days=Decimal("0.0"),
            balance=Decimal("2.0")
        )
        self.el_balance = LeaveBalance.objects.create(
            user=self.employee,
            leave_type=self.el_type,
            year=self.current_year,
            credited_days=Decimal("30.0"),
            used_days=Decimal("0.0"),
            balance=Decimal("30.0")
        )

        # Seed test holidays: Friday (2026-11-13) as Gazetted, Monday (2026-11-16) as Restricted
        self.gazetted_holiday = HolidayCalendar.objects.create(
            date=date(2026, 11, 13),
            name="Diwali Festival",
            holiday_type="gazetted",
            academic_year=2026
        )
        self.restricted_holiday = HolidayCalendar.objects.create(
            date=date(2026, 11, 16),
            name="Guru Nanak Jayanti RH",
            holiday_type="restricted",
            academic_year=2026
        )

    def test_br_el_011_cl_holiday_and_sunday_exclusion(self):
        """
        BR-EL-011: For CL, intervening Sundays and Gazetted Holidays do NOT count.
        Range: Thursday 2026-11-12 to Monday 2026-11-16 (5 calendar days total)
        - 2026-11-12: Thursday (working -> counts)
        - 2026-11-13: Friday (Gazetted Holiday -> EXCLUDED)
        - 2026-11-14: Saturday (working -> counts)
        - 2026-11-15: Sunday (Sunday -> EXCLUDED)
        - 2026-11-16: Monday (working -> counts)
        Expected CL days = 3.
        """
        start = date(2026, 11, 12)
        end = date(2026, 11, 16)
        cl_days = calculate_leave_days(start, end, leave_type_code="CL")
        self.assertEqual(cl_days, Decimal("3"))

        # In contrast, EL counts all continuous calendar days = 5
        el_days = calculate_leave_days(start, end, leave_type_code="EL")
        self.assertEqual(el_days, Decimal("5"))

        # Half-day check
        half_day_count = calculate_leave_days(start, start, leave_type_code="CL", half_day=True)
        self.assertEqual(half_day_count, Decimal("0.5"))

    def test_br_el_003_rh_validation(self):
        """
        BR-EL-003 & BR-EL-031: Restricted Holiday can only be 1 day, and date must exist in HolidayCalendar.
        """
        # Valid RH on declared date
        valid, err = validate_leave_application(
            self.employee, self.rh_type,
            date(2026, 11, 16), date(2026, 11, 16)
        )
        self.assertTrue(valid)
        self.assertIsNone(err)

        # Invalid multi-day RH
        valid_multi, err_multi = validate_leave_application(
            self.employee, self.rh_type,
            date(2026, 11, 16), date(2026, 11, 17)
        )
        self.assertFalse(valid_multi)
        self.assertIn("single day", err_multi)

        # Invalid undeclared date
        valid_undec, err_undec = validate_leave_application(
            self.employee, self.rh_type,
            date(2026, 11, 17), date(2026, 11, 17)
        )
        self.assertFalse(valid_undec)
        self.assertIn("not a declared Restricted Holiday", err_undec)

    def test_br_el_012_cl_continuous_limit_and_station_leave(self):
        """
        BR-EL-012: CL continuous span cannot exceed 8 calendar days.
        BR-EL-014: Station leave requires non-empty address.
        """
        # 9 days span: 2026-12-01 to 2026-12-09
        valid_span, err_span = validate_leave_application(
            self.employee, self.cl_type,
            date(2026, 12, 1), date(2026, 12, 9)
        )
        self.assertFalse(valid_span)
        self.assertIn("cannot exceed 8 continuous calendar days", err_span)

        # Station leave missing address
        valid_stn, err_stn = validate_leave_application(
            self.employee, self.cl_type,
            date(2026, 12, 1), date(2026, 12, 3),
            station_leave=True, station_leave_address="   "
        )
        self.assertFalse(valid_stn)
        self.assertIn("Station leave address must be provided", err_stn)

    def test_br_el_015_and_el_uc_019_substitute_workflow_and_renomination(self):
        """
        BR-EL-015 & EL-UC-019:
        - When substitute nominated: request in awaiting_substitute.
        - When declined: transitions to substitute_declined.
        - Applicant can re-nominate replacement substitute.
        - When accepted: transitions to pending_unit_head.
        """
        req = submit_leave_request(
            applicant=self.employee,
            leave_type=self.cl_type,
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 2),
            purpose="Attending workshop",
            substitute=self.substitute
        )
        self.assertEqual(req.status, "awaiting_substitute")
        self.assertEqual(req.substitute_status, "pending")

        # Substitute declines
        req = respond_substitute(req, self.substitute, "decline", "Busy with lab invigilation")
        self.assertEqual(req.status, "substitute_declined")
        self.assertEqual(req.substitute_status, "declined")

        # Applicant re-nominates substitute_alt
        req = renominate_substitute(req, self.employee, self.substitute_alt, "Nominated alternate substitute")
        self.assertEqual(req.status, "awaiting_substitute")
        self.assertEqual(req.substitute, self.substitute_alt)
        self.assertEqual(req.substitute_status, "pending")

        # Substitute_alt accepts
        req = respond_substitute(req, self.substitute_alt, "accept", "Available to cover")
        self.assertEqual(req.status, "pending_unit_head")
        self.assertEqual(req.substitute_status, "accepted")

    def test_br_el_023_approved_leave_cancellation_and_quota_refund(self):
        """
        BR-EL-023 & EL-UC-008:
        Approved leave can be cancelled prior to commencement with full atomic quota refund.
        """
        # Choose dates with 2 working days (e.g., 2026-11-24 Tuesday and 2026-11-25 Wednesday)
        future_start = date(2026, 11, 24)
        future_end = date(2026, 11, 25)

        req = submit_leave_request(
            applicant=self.employee,
            leave_type=self.cl_type,
            start_date=future_start,
            end_date=future_end,
            purpose="Pre-planned medical checkup"
        )
        process_approval(req, self.unit_head, "unit_head", "approve")
        req.refresh_from_db()
        self.assertEqual(req.status, "approved")

        self.cl_balance.refresh_from_db()
        self.assertEqual(self.cl_balance.balance, Decimal("6.0"))
        self.assertEqual(self.cl_balance.used_days, Decimal("2.0"))

        # Cancel approved leave
        cancelled_req = cancel_approved_leave(req, self.employee, "Medical checkup cancelled")
        self.assertEqual(cancelled_req.status, "cancelled")

        # Balance must be atomically refunded back to 8.0
        self.cl_balance.refresh_from_db()
        self.assertEqual(self.cl_balance.balance, Decimal("8.0"))
        self.assertEqual(self.cl_balance.used_days, Decimal("0.0"))

    def test_br_el_025_leave_extension(self):
        """
        BR-EL-025 & EL-UC-009:
        Applicant can extend ongoing approved leave with strictly greater end date.
        """
        start = date(2026, 12, 1)
        end = date(2026, 12, 2)
        req = submit_leave_request(
            applicant=self.employee,
            leave_type=self.el_type,
            start_date=start,
            end_date=end,
            purpose="Conference"
        )
        process_approval(req, self.unit_head, "unit_head", "approve")

        # Extend by 1 day: new_end_date = 2026-12-03
        extended_req = request_leave_extension(req, self.employee, date(2026, 12, 3), "Flight delayed")
        self.assertEqual(extended_req.end_date, date(2026, 12, 3))
        self.assertEqual(extended_req.status, "pending_unit_head")

    def test_br_el_027_and_028_duty_resumption_and_unconsumed_days_refund(self):
        """
        BR-EL-027, BR-EL-028, EL-UC-010, EL-UC-011:
        Duty resumption submitted on early return refunds unconsumed leave days upon approval.
        """
        # Approved 4 continuous days of EL (e.g., 2026-12-10 to 2026-12-13)
        start = date(2026, 12, 10)
        end = date(2026, 12, 13)
        req = submit_leave_request(
            applicant=self.employee,
            leave_type=self.el_type,
            start_date=start,
            end_date=end,
            purpose="Field study"
        )
        process_approval(req, self.unit_head, "unit_head", "approve")
        self.el_balance.refresh_from_db()
        self.assertEqual(self.el_balance.balance, Decimal("26.0"))
        self.assertEqual(self.el_balance.used_days, Decimal("4.0"))

        # Early return on 2026-12-12 (only availed 10th and 11th = 2 days, 2 days unconsumed)
        resumption = submit_duty_resumption(
            leave_request=req,
            applicant_user=self.employee,
            resumption_date=date(2026, 12, 12),
            remarks="Work concluded earlier than planned"
        )
        self.assertEqual(resumption.resumption_type, "early")
        self.assertEqual(resumption.actual_days_availed, Decimal("2.0"))
        self.assertEqual(resumption.refunded_days, Decimal("2.0"))
        self.assertEqual(resumption.status, "submitted")

        # Admin approves duty resumption
        approved_resumption = approve_duty_resumption(resumption, self.unit_head, role_name="admin")
        self.assertEqual(approved_resumption.status, "approved")

        req.refresh_from_db()
        self.assertEqual(req.status, "completed")

        # Balance credited back by 2 days (26 + 2 = 28)
        self.el_balance.refresh_from_db()
        self.assertEqual(self.el_balance.balance, Decimal("28.0"))
        self.assertEqual(self.el_balance.used_days, Decimal("2.0"))

    def test_br_el_006_007_008_year_end_rollover(self):
        """
        BR-EL-006, BR-EL-007, BR-EL-008:
        - CL and RH lapse (not carried forward). Fresh allocation for next year.
        - 50% of unavailed Vacation Leave (VL) converts into EL.
        - EL balance accumulates up to 300 days ceiling.
        """
        # Create user with existing 280 EL days and 40 VL days in 2026
        vl_bal = LeaveBalance.objects.create(
            user=self.employee,
            leave_type=self.vl_type,
            year=self.current_year,
            credited_days=Decimal("60.0"),
            used_days=Decimal("20.0"),
            balance=Decimal("40.0")
        )
        self.el_balance.balance = Decimal("280.0")
        self.el_balance.save()

        # Execute rollover to next year
        next_year = self.current_year + 1
        result = process_year_end_rollover(self.current_year, next_year)
        self.assertEqual(result["target_year"], next_year)
        self.assertGreaterEqual(result["processed_users_count"], 1)

        # 1. 50% VL = 20 days.
        # EL carry = 280 (previous) + 20 (50% VL) + 30 (annual quota) = 330 -> CAPPED at 300!
        next_el_bal = LeaveBalance.objects.get(user=self.employee, leave_type=self.el_type, year=next_year)
        self.assertEqual(next_el_bal.balance, Decimal("300.0"))
        self.assertEqual(next_el_bal.credited_days, Decimal("300.0"))
        self.assertEqual(next_el_bal.used_days, Decimal("0.0"))

        # 2. CL lapsed and reset to fresh quota = 8.0
        next_cl_bal = LeaveBalance.objects.get(user=self.employee, leave_type=self.cl_type, year=next_year)
        self.assertEqual(next_cl_bal.balance, Decimal("8.0"))

        # 3. RH lapsed and reset to fresh quota = 2.0
        next_rh_bal = LeaveBalance.objects.get(user=self.employee, leave_type=self.rh_type, year=next_year)
        self.assertEqual(next_rh_bal.balance, Decimal("2.0"))
