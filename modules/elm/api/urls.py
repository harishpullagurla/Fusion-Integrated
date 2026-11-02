from django.urls import path
from .views import (
    LeaveTypeListView,
    HolidayCalendarListView,
    EligibleSubstitutesListView,
    LeaveBalanceListView,
    LeaveRequestListCreateView,
    LeaveRequestDetailView,
    SubstituteResponseView,
    RenominateSubstituteView,
    LeaveApprovalActionView,
    LeaveWithdrawView,
    LeaveCancelView,
    LeaveExtendView,
    DutyResumptionListView,
    DutyResumptionSubmitView,
    DutyResumptionApproveView,
    YearEndRolloverView,
)

urlpatterns = [
    # Static and Reference Endpoints
    path('types/', LeaveTypeListView.as_view(), name='leave-type-list'),
    path('holidays/', HolidayCalendarListView.as_view(), name='holiday-calendar-list'),
    path('substitutes/', EligibleSubstitutesListView.as_view(), name='eligible-substitutes-list'),
    path('balances/', LeaveBalanceListView.as_view(), name='leave-balance-list'),

    # Application Lifecycle Endpoints
    path('requests/', LeaveRequestListCreateView.as_view(), name='leave-request-list-create'),
    path('requests/<int:pk>/', LeaveRequestDetailView.as_view(), name='leave-request-detail'),
    path('requests/<int:pk>/withdraw/', LeaveWithdrawView.as_view(), name='leave-withdraw'),
    path('requests/<int:pk>/cancel/', LeaveCancelView.as_view(), name='leave-cancel'),
    path('requests/<int:pk>/extend/', LeaveExtendView.as_view(), name='leave-extend'),

    # Substitute Workflow Endpoints
    path('requests/<int:pk>/substitute-response/', SubstituteResponseView.as_view(), name='substitute-response'),
    path('requests/<int:pk>/renominate-substitute/', RenominateSubstituteView.as_view(), name='renominate-substitute'),

    # Approval Workflow Endpoints
    path('requests/<int:pk>/action/', LeaveApprovalActionView.as_view(), name='leave-approval-action'),

    # Duty Resumption Endpoints
    path('resumptions/', DutyResumptionListView.as_view(), name='duty-resumption-list'),
    path('requests/<int:pk>/resumption/', DutyResumptionSubmitView.as_view(), name='duty-resumption-submit'),
    path('resumptions/<int:pk>/action/', DutyResumptionApproveView.as_view(), name='duty-resumption-approve'),

    # Administrative Services Endpoints
    path('admin/year-end-rollover/', YearEndRolloverView.as_view(), name='year-end-rollover'),
]
