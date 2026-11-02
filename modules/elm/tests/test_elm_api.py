from datetime import date
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from fusion_auth.principal import Principal
from modules.directory.models import UserRef
from modules.elm.models import LeaveType, LeaveBalance, LeaveRequest


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
        self.principal = Principal(
            user_id=201,
            username="faculty201",
            display_name="Prof. Sharma",
            kind="faculty",
            active_role="faculty",
            roles=("faculty",),
            permissions=frozenset(["elm:apply", "elm:view"]),
            modules=("elm",)
        )
        self.client.force_authenticate(user=self.principal)

        self.leave_type = LeaveType.objects.create(
            code="CL",
            name="Casual Leave",
            annual_quota=Decimal("8.0")
        )
        self.balance = LeaveBalance.objects.create(
            user=self.user_ref,
            leave_type=self.leave_type,
            year=date.today().year,
            credited_days=Decimal("8.0"),
            used_days=Decimal("0.0"),
            balance=Decimal("8.0")
        )

    def test_list_leave_types_endpoint(self):
        response = self.client.get("/api/v1/elm/types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
        self.assertEqual(response.data[0]["code"], "CL")

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
