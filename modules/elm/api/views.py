from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ValidationError

from modules.directory.models import UserRef
from modules.elm.models import LeaveType, LeaveBalance, LeaveRequest, LeaveActionLog, HolidayCalendar, DutyResumption
from modules.elm.api.serializers import (
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
        return UserRef.objects.filter(user_id=user.user_id).first()
    if hasattr(user, 'id'):
        return UserRef.objects.filter(user_id=user.id).first()
    return UserRef.objects.filter(user_id=1).first()


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


class LeaveBalanceListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user_ref = get_user_ref(request.user)
        if user_ref:
            leave_balances = LeaveBalance.objects.filter(user=user_ref)
        else:
            leave_balances = LeaveBalance.objects.none()
        serializer = LeaveBalanceSerializer(leave_balances, many=True)
        return Response(serializer.data)


class LeaveRequestListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user_ref = get_user_ref(request.user)
        if user_ref:
            leave_requests = LeaveRequest.objects.filter(applicant=user_ref)
        else:
            leave_requests = LeaveRequest.objects.none()
        serializer = LeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data)

    def post(self, request):
        user_ref = get_user_ref(request.user)
        data = request.data.copy()
        
        # If applicant not explicitly provided in payload, default to authenticated user
        if 'applicant' not in data and user_ref:
            data['applicant'] = user_ref.id

        serializer = LeaveRequestSerializer(data=data)
        if serializer.is_valid():
            try:
                applicant = UserRef.objects.get(pk=data['applicant'])
                leave_type = LeaveType.objects.get(pk=data['leave_type'])
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
                return Response({'error': str(e.message if hasattr(e, 'message') else e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveRequestDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        leave_request = LeaveRequest.objects.get(pk=pk)
        serializer = LeaveRequestSerializer(leave_request)
        return Response(serializer.data)


class SubstituteResponseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        leave_request = LeaveRequest.objects.get(pk=pk)
        serializer = SubstituteResponseSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user_ref = get_user_ref(request.user)
                decision = serializer.validated_data.get("decision")
                comments = serializer.validated_data.get("comments", "")
                updated = respond_substitute(leave_request, user_ref, decision, comments)
                return Response(LeaveRequestSerializer(updated).data, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RenominateSubstituteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        leave_request = LeaveRequest.objects.get(pk=pk)
        serializer = RenominateSubstituteSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user_ref = get_user_ref(request.user)
                new_sub = UserRef.objects.get(pk=serializer.validated_data['new_substitute_id'])
                comments = serializer.validated_data.get("comments", "")
                updated = renominate_substitute(leave_request, user_ref, new_sub, comments)
                return Response(LeaveRequestSerializer(updated).data, status=status.HTTP_200_OK)
            except (ValidationError, UserRef.DoesNotExist) as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveApprovalActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        leave_request = LeaveRequest.objects.get(pk=pk)
        serializer = ApprovalActionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user_ref = get_user_ref(request.user)
                action = serializer.validated_data.get("action")
                role_name = serializer.validated_data.get("role_name", "unit_head")
                comments = serializer.validated_data.get("comments", "")
                updated = process_approval(leave_request, user_ref, role_name, action, comments)
                return Response(LeaveRequestSerializer(updated).data, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveWithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            leave_request = LeaveRequest.objects.get(pk=pk)
            user_ref = get_user_ref(request.user)
            updated = withdraw_leave_request(leave_request, user_ref)
            return Response(LeaveRequestSerializer(updated).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LeaveCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            leave_request = LeaveRequest.objects.get(pk=pk)
            user_ref = get_user_ref(request.user)
            serializer = CancelLeaveSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comments = serializer.validated_data.get("comments", "")
            updated = cancel_approved_leave(leave_request, user_ref, comments)
            return Response(LeaveRequestSerializer(updated).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LeaveExtendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            leave_request = LeaveRequest.objects.get(pk=pk)
            user_ref = get_user_ref(request.user)
            serializer = ExtendLeaveSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_end_date = serializer.validated_data['new_end_date']
            comments = serializer.validated_data.get("comments", "")
            updated = request_leave_extension(leave_request, user_ref, new_end_date, comments)
            return Response(LeaveRequestSerializer(updated).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DutyResumptionSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            leave_request = LeaveRequest.objects.get(pk=pk)
            user_ref = get_user_ref(request.user)
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
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            resumption = DutyResumption.objects.get(pk=pk)
            user_ref = get_user_ref(request.user)
            serializer = ApproveDutyResumptionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            role_name = serializer.validated_data.get('role_name', 'admin')
            comments = serializer.validated_data.get('comments', '')
            approved_resumption = approve_duty_resumption(resumption, user_ref, role_name, comments)
            return Response(DutyResumptionSerializer(approved_resumption).data, status=status.HTTP_200_OK)
        except (ValidationError, DutyResumption.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class YearEndRolloverView(APIView):
    permission_classes = [IsAuthenticated]

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
