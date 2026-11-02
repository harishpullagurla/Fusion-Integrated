from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from modules.directory.models import UserRef
from modules.elm.models import LeaveType, LeaveBalance, LeaveRequest, LeaveActionLog
from modules.elm.api.serializers import (
    LeaveTypeSerializer,
    LeaveBalanceSerializer,
    LeaveRequestSerializer,
    LeaveActionLogSerializer,
    SubstituteResponseSerializer,
    ApprovalActionSerializer,
)
from modules.elm.services.leave_service import (
    respond_substitute,
    process_approval,
    withdraw_leave_request,
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
        serializer = LeaveRequestSerializer(data=request.data)
        if serializer.is_valid():
            leave_request = serializer.save()
            LeaveActionLog.objects.create(
                leave_request=leave_request,
                actor=leave_request.applicant,
                role_name="employee",
                action="submitted",
            )
            return Response(LeaveRequestSerializer(leave_request).data, status=status.HTTP_201_CREATED)
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
            user_ref = get_user_ref(request.user)
            decision = serializer.validated_data.get("decision")
            comments = serializer.validated_data.get("comments", "")
            updated = respond_substitute(leave_request, user_ref, decision, comments)
            return Response(LeaveRequestSerializer(updated).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveApprovalActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        leave_request = LeaveRequest.objects.get(pk=pk)
        serializer = ApprovalActionSerializer(data=request.data)
        if serializer.is_valid():
            user_ref = get_user_ref(request.user)
            action = serializer.validated_data.get("action")
            role_name = serializer.validated_data.get("role_name", "unit_head")
            comments = serializer.validated_data.get("comments", "")
            updated = process_approval(leave_request, user_ref, role_name, action, comments)
            return Response(LeaveRequestSerializer(updated).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveWithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        leave_request = LeaveRequest.objects.get(pk=pk)
        user_ref = get_user_ref(request.user)
        updated = withdraw_leave_request(leave_request, user_ref)
        return Response(LeaveRequestSerializer(updated).data, status=status.HTTP_200_OK)
