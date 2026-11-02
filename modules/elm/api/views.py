from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ValidationError
from django.utils import timezone

from modules.directory.models import UserRef
from modules.elm.models import LeaveType, LeaveBalance, LeaveRequest, LeaveActionLog, HolidayCalendar, DutyResumption
from modules.elm.api.serializers import (
    UserRefSimpleSerializer,
    LeaveTypeSerializer,
    HolidayCalendarSerializer,
    LeaveBalanceSerializer,
    LeaveRequestSerializer,
    LeaveActionLogSerializer,
    DutyResumptionSerializer,
    SubstituteResponseSerializer,
    RenominateSubstituteSerializer,
    ApprovalActionSerializer,
    CancelLeaveSerializer,
    ExtendLeaveSerializer,
    SubmitDutyResumptionSerializer,
    ApproveDutyResumptionSerializer,
    YearEndRolloverSerializer,
)
from modules.elm.services.leave_service import (
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

def get_user_ref(user):
    if hasattr(user, 'user_id'):
        ref = UserRef.objects.filter(user_id=user.user_id).first()
        if ref:
            return ref
    if hasattr(user, 'id'):
        ref = UserRef.objects.filter(user_id=user.id).first()
        if ref:
            return ref
    return UserRef.objects.filter(user_id=1).first() or UserRef.objects.first()


class LeaveTypeListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        leave_types = LeaveType.objects.all()
        serializer = LeaveTypeSerializer(leave_types, many=True)
        return Response(serializer.data)


class HolidayCalendarListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        year = request.query_params.get('year')
        holidays = HolidayCalendar.objects.all()
        if year:
            holidays = holidays.filter(academic_year=year)
        serializer = HolidayCalendarSerializer(holidays, many=True)
        return Response(serializer.data)


class EligibleSubstitutesListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user_ref = get_user_ref(request.user)
        colleagues = UserRef.objects.all()
        if user_ref:
            colleagues = colleagues.exclude(user_id=user_ref.user_id)
        serializer = UserRefSimpleSerializer(colleagues, many=True)
        return Response(serializer.data)


class LeaveBalanceListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user_ref = get_user_ref(request.user)
        if not user_ref:
            user_ref = UserRef.objects.first()

        year_param = request.query_params.get('year')
        current_year = int(year_param) if (year_param and year_param.isdigit()) else timezone.now().year
        if user_ref:
            # Auto-provision initial balances if none exist for current year
            existing_count = LeaveBalance.objects.filter(user=user_ref, year=current_year).count()
            if existing_count == 0:
                for lt in LeaveType.objects.all():
                    LeaveBalance.objects.get_or_create(
                        user=user_ref,
                        leave_type=lt,
                        year=current_year,
                        defaults={
                            'credited_days': lt.annual_quota,
                            'used_days': 0,
                            'balance': lt.annual_quota
                        }
                    )
            leave_balances = LeaveBalance.objects.filter(user=user_ref, year=current_year)
        else:
            leave_balances = LeaveBalance.objects.none()

        serializer = LeaveBalanceSerializer(leave_balances, many=True)
        return Response(serializer.data)


class LeaveRequestListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user_ref = get_user_ref(request.user)
        scope = request.query_params.get('scope', 'my')
        active_role = getattr(getattr(request, 'principal', None), 'active_role', 'faculty')

        if scope == 'substitute' and user_ref:
            leave_requests = LeaveRequest.objects.filter(substitute=user_ref).order_by('-created_at')
        elif scope == 'approvals':
            if active_role in ['hod', 'unit_head']:
                leave_requests = LeaveRequest.objects.filter(status='pending_unit_head').order_by('-created_at')
            elif active_role in ['dean', 'director']:
                leave_requests = LeaveRequest.objects.filter(status='pending_higher_sanction').order_by('-created_at')
            elif active_role in ['admin', 'establishment']:
                leave_requests = LeaveRequest.objects.filter(
                    status__in=['pending_unit_head', 'pending_higher_sanction']
                ).order_by('-created_at')
            else:
                leave_requests = LeaveRequest.objects.none()
        elif scope == 'all':
            leave_requests = LeaveRequest.objects.all().order_by('-created_at')
        else:
            # Default to my requests
            if user_ref:
                leave_requests = LeaveRequest.objects.filter(applicant=user_ref).order_by('-created_at')
            else:
                leave_requests = LeaveRequest.objects.none()

        serializer = LeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data)

    def post(self, request):
        user_ref = get_user_ref(request.user)
        data = request.data.copy()
        
        # Default applicant to current user if not explicitly passed
        if 'applicant' not in data and user_ref:
            data['applicant'] = user_ref.user_id

        serializer = LeaveRequestSerializer(data=data)
        if serializer.is_valid():
            try:
                try:
                    applicant = UserRef.objects.get(pk=data['applicant'])
                except UserRef.DoesNotExist:
                    return Response({'error': f"Applicant with id {data['applicant']} not found."}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    leave_type = LeaveType.objects.get(pk=data['leave_type'])
                except LeaveType.DoesNotExist:
                    return Response({'error': f"Leave type with id {data['leave_type']} not found."}, status=status.HTTP_400_BAD_REQUEST)

                substitute = UserRef.objects.filter(pk=data.get('substitute')).first() if data.get('substitute') else None
                
                leave_request = submit_leave_request(
                    applicant=applicant,
                    leave_type=leave_type,
                    start_date=serializer.validated_data['start_date'],
                    end_date=serializer.validated_data['end_date'],
                    purpose=serializer.validated_data.get('purpose', ''),
                    half_day=serializer.validated_data.get('half_day', False),
                    half_day_period=serializer.validated_data.get('half_day_period'),
                    station_leave=serializer.validated_data.get('station_leave', False),
                    station_leave_address=serializer.validated_data.get('station_leave_address', ''),
                    substitute=substitute
                )
                return Response(LeaveRequestSerializer(leave_request).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                err_msg = e.message if hasattr(e, 'message') else str(e)
                return Response({'error': err_msg}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveRequestDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            leave_request = LeaveRequest.objects.get(pk=pk)
            serializer = LeaveRequestSerializer(leave_request)
            return Response(serializer.data)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found'}, status=status.HTTP_404_NOT_FOUND)


class SubstituteResponseView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            leave_request = LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubstituteResponseSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user_ref = get_user_ref(request.user)
                # Allow nominated substitute, or in dev testing fall back to the nominated substitute on the request
                sub_actor = user_ref if (user_ref and user_ref == leave_request.substitute) else leave_request.substitute
                if not sub_actor:
                    sub_actor = user_ref
                decision = serializer.validated_data.get("decision")
                comments = serializer.validated_data.get("comments", "")
                updated = respond_substitute(leave_request, sub_actor, decision, comments)
                return Response(LeaveRequestSerializer(updated).data, status=status.HTTP_200_OK)
            except ValidationError as e:
                err_msg = e.message if hasattr(e, 'message') else str(e)
                return Response({'error': err_msg}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RenominateSubstituteView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            leave_request = LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = RenominateSubstituteSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user_ref = get_user_ref(request.user)
                if not user_ref:
                    user_ref = leave_request.applicant
                new_sub = UserRef.objects.get(pk=serializer.validated_data['new_substitute_id'])
                comments = serializer.validated_data.get("comments", "")
                updated = renominate_substitute(leave_request, user_ref, new_sub, comments)
                return Response(LeaveRequestSerializer(updated).data, status=status.HTTP_200_OK)
            except (ValidationError, UserRef.DoesNotExist) as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveApprovalActionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            leave_request = LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ApprovalActionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                active_role = getattr(getattr(request, 'principal', None), 'active_role', 'unit_head')
                if active_role in ['faculty', 'staff', 'student']:
                    return Response({'error': f"Role '{active_role}' does not have sanctioning privileges."}, status=status.HTTP_403_FORBIDDEN)
                user_ref = get_user_ref(request.user) or UserRef.objects.first()
                action = serializer.validated_data.get("action")
                role_name = serializer.validated_data.get("role_name", active_role)
                comments = serializer.validated_data.get("comments", "")
                updated = process_approval(leave_request, user_ref, role_name, action, comments)
                return Response(LeaveRequestSerializer(updated).data, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveWithdrawView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            leave_request = LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_ref = get_user_ref(request.user)
            if not user_ref:
                user_ref = leave_request.applicant
            updated = withdraw_leave_request(leave_request, user_ref)
            return Response(LeaveRequestSerializer(updated).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LeaveCancelView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            leave_request = LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_ref = get_user_ref(request.user)
            if not user_ref:
                user_ref = leave_request.applicant
            serializer = CancelLeaveSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comments = serializer.validated_data.get("comments", "")
            updated = cancel_approved_leave(leave_request, user_ref, comments)
            return Response(LeaveRequestSerializer(updated).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LeaveExtendView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            leave_request = LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_ref = get_user_ref(request.user)
            if not user_ref:
                user_ref = leave_request.applicant
            serializer = ExtendLeaveSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_end_date = serializer.validated_data['new_end_date']
            comments = serializer.validated_data.get("comments", "")
            updated = request_leave_extension(leave_request, user_ref, new_end_date, comments)
            return Response(LeaveRequestSerializer(updated).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DutyResumptionListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        resumptions = DutyResumption.objects.all().order_by('-created_at')
        status_filter = request.query_params.get('status')
        if status_filter:
            resumptions = resumptions.filter(status=status_filter)
        serializer = DutyResumptionSerializer(resumptions, many=True)
        return Response(serializer.data)


class DutyResumptionSubmitView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            leave_request = LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_ref = get_user_ref(request.user)
            if not user_ref:
                user_ref = leave_request.applicant
            serializer = SubmitDutyResumptionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            resumption = submit_duty_resumption(
                leave_request=leave_request,
                applicant_user=user_ref,
                resumption_date=serializer.validated_data['resumption_date'],
                prefix_suffix=serializer.validated_data.get('prefix_suffix', ''),
                remarks=serializer.validated_data.get('remarks', '')
            )
            return Response(DutyResumptionSerializer(resumption).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DutyResumptionApproveView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            resumption = DutyResumption.objects.get(pk=pk)
        except DutyResumption.DoesNotExist:
            return Response({'error': 'Duty resumption not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_ref = get_user_ref(request.user) or UserRef.objects.first()
            serializer = ApproveDutyResumptionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            role_name = serializer.validated_data.get('role_name', 'admin')
            comments = serializer.validated_data.get('comments', '')
            approved_resumption = approve_duty_resumption(resumption, user_ref, role_name, comments)
            return Response(DutyResumptionSerializer(approved_resumption).data, status=status.HTTP_200_OK)
        except (ValidationError, DutyResumption.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class YearEndRolloverView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = YearEndRolloverSerializer(data=request.data)
        if serializer.is_valid():
            try:
                current_year = serializer.validated_data['current_year']
                target_year = serializer.validated_data.get('target_year')
                result = process_year_end_rollover(current_year, target_year)
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OfflineLeaveRecordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        active_role = getattr(getattr(request, 'principal', None), 'active_role', 'admin')
        if active_role not in ['admin', 'establishment']:
            return Response({'error': f"Role '{active_role}' is not authorized to record offline sanctioned leave (BR-EL-029)."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        try:
            applicant = UserRef.objects.get(pk=data['applicant'])
            leave_type = LeaveType.objects.get(pk=data['leave_type'])
            offline_ref = data.get('offline_reference', 'OFFLINE-ORDER')
            sanctioned_by = data.get('sanctioned_by', 'Administration')
            remarks = data.get('remarks', '')

            from modules.elm.services.leave_service import record_offline_leave
            leave_req = record_offline_leave(
                applicant=applicant,
                leave_type=leave_type,
                start_date=data['start_date'],
                end_date=data['end_date'],
                offline_reference=offline_ref,
                sanctioned_by=sanctioned_by,
                remarks=remarks
            )
            return Response(LeaveRequestSerializer(leave_req).data, status=status.HTTP_201_CREATED)
        except (UserRef.DoesNotExist, LeaveType.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LeaveRequestExportView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            leave_request = LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found'}, status=status.HTTP_404_NOT_FOUND)

        from modules.elm.services.leave_service import calculate_leave_days
        days = calculate_leave_days(
            leave_request.start_date, leave_request.end_date,
            leave_request.leave_type.code, leave_request.half_day
        )

        export_data = {
            "document_title": "OFFICIAL LEAVE APPLICATION SLIP",
            "request_id": leave_request.id,
            "status": leave_request.get_status_display(),
            "status_code": leave_request.status,
            "applicant": {
                "id": leave_request.applicant.user_id,
                "name": leave_request.applicant.display_name,
                "username": leave_request.applicant.username,
                "discipline": leave_request.applicant.discipline,
                "kind": leave_request.applicant.kind,
            },
            "leave_category": {
                "code": leave_request.leave_type.code,
                "name": leave_request.leave_type.name,
            },
            "duration": {
                "start_date": leave_request.start_date.isoformat(),
                "end_date": leave_request.end_date.isoformat(),
                "total_days": str(days),
                "half_day": leave_request.half_day,
                "half_day_period": leave_request.half_day_period,
            },
            "purpose": leave_request.purpose,
            "station_leave": {
                "is_station_leave": leave_request.station_leave,
                "address": leave_request.station_leave_address,
            },
            "substitute_arrangement": {
                "nominated_substitute": leave_request.substitute.display_name if leave_request.substitute else "None Required",
                "substitute_status": leave_request.get_substitute_status_display(),
            },
            "audit_trail": [
                {
                    "timestamp": log.created_at.isoformat(),
                    "actor": log.actor.display_name,
                    "role": log.role_name,
                    "action": log.get_action_display(),
                    "comments": log.comments,
                }
                for log in leave_request.action_logs.order_by("created_at")
            ],
        }
        return Response(export_data, status=status.HTTP_200_OK)
