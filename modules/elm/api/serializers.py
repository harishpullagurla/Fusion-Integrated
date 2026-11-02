from rest_framework import serializers
from modules.elm.models import LeaveType, LeaveBalance, LeaveRequest, LeaveActionLog, HolidayCalendar, DutyResumption
from modules.directory.models import UserRef

class UserRefSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRef
        fields = ['id', 'user_id', 'username', 'display_name', 'kind', 'discipline']

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'

class HolidayCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = HolidayCalendar
        fields = '__all__'

class LeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type_code = serializers.CharField(source='leave_type.code', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    user_name = serializers.CharField(source='user.display_name', read_only=True)

    class Meta:
        model = LeaveBalance
        fields = '__all__'

class LeaveActionLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.display_name', read_only=True)

    class Meta:
        model = LeaveActionLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class DutyResumptionSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='leave_request.applicant.display_name', read_only=True)
    leave_type_code = serializers.CharField(source='leave_request.leave_type.code', read_only=True)

    class Meta:
        model = DutyResumption
        fields = '__all__'
        read_only_fields = ['id', 'actual_days_availed', 'refunded_days', 'status', 'created_at', 'updated_at']

class LeaveRequestSerializer(serializers.ModelSerializer):
    action_logs = LeaveActionLogSerializer(many=True, read_only=True)
    duty_resumption = DutyResumptionSerializer(read_only=True)
    applicant_name = serializers.CharField(source='applicant.display_name', read_only=True)
    substitute_name = serializers.CharField(source='substitute.display_name', read_only=True)
    leave_type_code = serializers.CharField(source='leave_type.code', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ['id', 'status', 'substitute_status', 'created_at', 'updated_at']

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date must be less than or equal to end date.")
        if data.get('half_day') and data['start_date'] != data['end_date']:
            raise serializers.ValidationError("If half day is True, start date must equal end date.")
        if data.get('half_day') and not data.get('half_day_period'):
            raise serializers.ValidationError("Half day period must be provided if half day is True.")
        if data.get('station_leave') and not (data.get('station_leave_address') and data['station_leave_address'].strip()):
            raise serializers.ValidationError("Station leave address must be provided when availing station leave (BR-EL-014).")
        return data

class SubstituteResponseSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=['accept', 'decline'])
    comments = serializers.CharField(required=False, allow_blank=True)

class RenominateSubstituteSerializer(serializers.Serializer):
    new_substitute_id = serializers.IntegerField()
    comments = serializers.CharField(required=False, allow_blank=True)

class ApprovalActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['recommend', 'approve', 'reject'])
    role_name = serializers.CharField(default='unit_head')
    comments = serializers.CharField(required=False, allow_blank=True)

class CancelLeaveSerializer(serializers.Serializer):
    comments = serializers.CharField(required=False, allow_blank=True)

class ExtendLeaveSerializer(serializers.Serializer):
    new_end_date = serializers.DateField()
    comments = serializers.CharField(required=False, allow_blank=True)

class SubmitDutyResumptionSerializer(serializers.Serializer):
    resumption_date = serializers.DateField()
    prefix_suffix = serializers.CharField(required=False, allow_blank=True)
    remarks = serializers.CharField(required=False, allow_blank=True)

class ApproveDutyResumptionSerializer(serializers.Serializer):
    role_name = serializers.CharField(default='admin')
    comments = serializers.CharField(required=False, allow_blank=True)

class YearEndRolloverSerializer(serializers.Serializer):
    current_year = serializers.IntegerField()
    target_year = serializers.IntegerField(required=False, allow_null=True)
