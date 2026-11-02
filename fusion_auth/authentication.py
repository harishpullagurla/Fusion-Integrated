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
            from fusion_auth.dev_state import DEV_ACTIVE_ROLES
            active_role = DEV_ACTIVE_ROLES.get(str(token), "faculty")
            principal = Principal(
                user_id=1,
                username=user_str,
                display_name=f"Dr. {user_str.capitalize()}",
                kind="faculty",
                active_role=active_role,
                roles=("faculty", "hod", "dean", "director", "admin"),
                permissions=frozenset(["elm:apply", "elm:view", "elm:approve"]),
                modules=("elm", "placement_cell"),
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
                )
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
