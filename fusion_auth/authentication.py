"""DRF authentication against Fusion_System_Administrator.

Accepts either the httpOnly cookie the SPA carries, or an
`Authorization: Token ...` header for scripts and service calls. Both are
resolved by asking IAM who the holder is — this service never checks a
password and never reads a user table.
"""
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from core.api import csrf
from fusion_auth.client import IamUnavailable, get_client
from fusion_auth.principal import Principal


class IamSessionAuthentication(BaseAuthentication):
    keyword = "Token"

    def authenticate(self, request):
        # Forwarded as a header: the IAM names its cookie differently.
        token = self._token_from(request)
        # Only a cookie is ambient, so only a cookie needs the CSRF check.
        from_cookie = token is None
        token = token or request.COOKIES.get(settings.IAM_AUTH_COOKIE_NAME)
        if not token:
            return None                       # anonymous; permissions decide

        if settings.DEBUG and token and token.startswith("dev-token-"):
            user_str = token.replace("dev-token-", "")
            from modules.directory.models import UserRef
            from fusion_auth.dev_state import DEV_ACTIVE_ROLES

            user_ref = UserRef.objects.filter(username=user_str).first()
            if not user_ref:
                user_ref = UserRef.objects.filter(user_id=1).first() or UserRef.objects.first()

            uid = user_ref.user_id if user_ref else 1
            uname = user_ref.username if user_ref else user_str
            dname = user_ref.display_name if user_ref else f"Dr. {user_str.capitalize()}"
            kind = user_ref.kind if user_ref else "faculty"

            # Assign persona roles based on identity
            if uname in ("admin", "est_officer"):
                roles = ("admin", "establishment")
            elif uname == "director":
                roles = ("director", "faculty")
            elif uname == "dean_fa":
                roles = ("dean", "faculty")
            elif uname == "hod_cse":
                roles = ("hod", "faculty")
            elif uname == "staff_rajesh":
                roles = ("staff",)
            elif uname == "student_rahul":
                roles = ("student",)
            elif uname == "harish":
                roles = ("faculty", "hod")
            else:
                roles = ("faculty",)

            # Determine active role
            default_role = roles[0]
            saved_role = DEV_ACTIVE_ROLES.get(str(token))
            active_role = saved_role if (saved_role and saved_role in roles) else default_role

            # Determine permissions based on active role
            if active_role in ("admin", "establishment"):
                permissions = frozenset(["elm:apply", "elm:view", "elm:approve_unit_head", "elm:approve_higher", "elm:approve_resumption", "elm:admin_rollover", "elm:manage_calendar"])
            elif active_role in ("dean", "director"):
                permissions = frozenset(["elm:apply", "elm:view", "elm:approve_higher", "elm:substitute"])
            elif active_role in ("hod", "unit_head"):
                permissions = frozenset(["elm:apply", "elm:view", "elm:approve_unit_head", "elm:substitute"])
            elif active_role in ("faculty", "staff"):
                permissions = frozenset(["elm:apply", "elm:view", "elm:substitute"])
            elif active_role == "student":
                permissions = frozenset(["student:view"])
            else:
                permissions = frozenset(["elm:view"])

            modules_list = ("elm", "placement_cell") if active_role != "student" else ("placement_cell",)

            principal = Principal(
                user_id=uid,
                username=uname,
                display_name=dname,
                kind=kind,
                active_role=active_role,
                roles=roles,
                permissions=permissions,
                modules=modules_list,
                navigation=(
                    {
                        "section": "Employee Services",
                        "items": [
                            {
                                "code": "elm",
                                "label": "Leave Management",
                                "icon": "calendar",
                                "to": "/elm",
                                "links": [
                                    {"code": "elm_dashboard", "label": "Leave Dashboard", "to": "/elm"}
                                ]
                            }
                        ]
                    },
                ) if active_role != "student" else ()
            )
            request.principal = principal
            return (principal, token)

        try:
            session = get_client().resolve_session(auth_token=token)
        except IamUnavailable as exc:
            # Fail closed but honestly: a 401 would blame the user for our outage.
            raise AuthenticationFailed(
                f"Identity service unavailable: {exc}"
            ) from exc

        if session is None:
            raise AuthenticationFailed("Invalid or expired credentials.")

        if from_cookie:
            csrf.require(request, token)

        principal = Principal.from_session(session)
        request.principal = principal
        return (principal, token)

    def _token_from(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if header.startswith(self.keyword + " "):
            return header[len(self.keyword) + 1:].strip()
        return None

    def authenticate_header(self, request):
        return self.keyword
