from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from fusion_auth.principal import Principal
from modules.directory.models import UserRef
from modules.elm.models import LeaveType, LeaveBalance, LeaveRequest, HolidayCalendar, DutyResumption


class ElmApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_ref = UserRef.objects.create(
            user_id=201,
            username="faculty201",
            display_name="Prof. Sharma",
            kind="faculty",
            discipline="ECE"
        )
        self.sub_ref = UserRef.objects.create(
            user_id=202,
            username="faculty202",
            display_name="Prof. Verma",
            kind="faculty",
            discipline="ECE"
        )
        self.principal = Principal(
            user_id=201,
            username="faculty201",
            display_name="Prof. Sharma",
            kind="faculty",
            active_role="faculty",
            roles=("faculty", "admin"),
            permissions=frozenset(["elm:apply", "elm:view", "elm:approve"]),
            modules=("elm",)
        )
        self.client.force_authenticate(user=self.principal)

        self.leave_type = LeaveType.objects.create(
            code="CL",
            name="Casual Leave",
            annual_quota=Decimal("8.0"),
            max_continuous_days=8
        )
        self.balance = LeaveBalance.objects.create(
            user=self.user_ref,
            leave_type=self.leave_type,
            year=date.today().year,
            credited_days=Decimal("8.0"),
            used_days=Decimal("0.0"),
            balance=Decimal("8.0")
        )

        self.holiday = HolidayCalendar.objects.create(
            date=date(2026, 12, 25),
            name="Christmas Day",
            holiday_type="gazetted",
            academic_year=2026
        )

    def test_list_leave_types_endpoint(self):
        response = self.client.get("/api/v1/elm/types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
        self.assertEqual(response.data[0]["code"], "CL")

    def test_list_holidays_endpoint(self):
        response = self.client.get("/api/v1/elm/holidays/?year=2026")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
        self.assertEqual(response.data[0]["name"], "Christmas Day")

    def test_list_leave_balances_endpoint(self):
        response = self.client.get("/api/v1/elm/balances/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_create_and_withdraw_leave_request_api(self):
        payload = {
            "applicant": self.user_ref.user_id,
            "leave_type": "CL",
            "start_date": "2026-11-20",
            "end_date": "2026-11-21",
            "half_day": False,
            "purpose": "Academic conference attendance"
        }
        res_create = self.client.post("/api/v1/elm/requests/", payload, format="json")
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        req_id = res_create.data["id"]

        # Withdraw leave request
        res_withdraw = self.client.post(f"/api/v1/elm/requests/{req_id}/withdraw/")
        self.assertEqual(res_withdraw.status_code, status.HTTP_200_OK)
        self.assertEqual(res_withdraw.data["status"], "withdrawn")

    def test_cancel_approved_leave_api(self):
        # Create approved leave in the future
        future_start = (date.today() + timedelta(days=15)).strftime("%Y-%m-%d")
        future_end = (date.today() + timedelta(days=16)).strftime("%Y-%m-%d")

        payload = {
            "applicant": self.user_ref.user_id,
            "leave_type": "CL",
            "start_date": future_start,
            "end_date": future_end,
            "purpose": "Future research visit"
        }
        res_create = self.client.post("/api/v1/elm/requests/", payload, format="json")
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        req_id = res_create.data["id"]

        # Approve it
        res_approve = self.client.post(f"/api/v1/elm/requests/{req_id}/action/", {"action": "approve"})
        self.assertEqual(res_approve.status_code, status.HTTP_200_OK)
        self.assertEqual(res_approve.data["status"], "approved")

        # Cancel it
        res_cancel = self.client.post(f"/api/v1/elm/requests/{req_id}/cancel/", {"comments": "Trip cancelled"})
        self.assertEqual(res_cancel.status_code, status.HTTP_200_OK)
        self.assertEqual(res_cancel.data["status"], "cancelled")

    def test_duty_resumption_workflow_api(self):
        # Create and approve request
        req = LeaveRequest.objects.create(
            applicant=self.user_ref,
            leave_type=self.leave_type,
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 3),
            purpose="Workshop",
            status="approved"
        )
        # Deduct balance as if approved
        self.balance.balance -= Decimal("3.0")
        self.balance.used_days += Decimal("3.0")
        self.balance.save()

        # Submit duty resumption (normal resumption on 2026-12-04)
        res_resumption = self.client.post(
            f"/api/v1/elm/requests/{req.id}/resumption/",
            {"resumption_date": "2026-12-04", "remarks": "Back in office"},
            format="json"
        )
        self.assertEqual(res_resumption.status_code, status.HTTP_201_CREATED)
        resumption_id = res_resumption.data["id"]

        # Approve duty resumption
        res_approve_resumption = self.client.post(
            f"/api/v1/elm/resumptions/{resumption_id}/action/",
            {"role_name": "admin", "comments": "Approved"},
            format="json"
        )
        self.assertEqual(res_approve_resumption.status_code, status.HTTP_200_OK)
        self.assertEqual(res_approve_resumption.data["status"], "approved")

        req.refresh_from_db()
        self.assertEqual(req.status, "completed")
